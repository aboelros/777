"""
Read-only Remote Staging Preflight Inspection Tool.
Connects strictly in read-only mode to inspect database identity, server version,
Alembic head revision, and structural properties of migration target tables.
Fails closed if target identity is missing, invalid, or matches production.
"""

import os
import sys
import asyncio
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.db_identity import (
    normalize_db_identity,
    is_production_target,
    DatabaseIdentity,
    PROD_SUPABASE_PROJECT_REF
)
from app.core.staging_preflight_queries import (
    SQL_DB_VERSION,
    SQL_CHECK_ALEMBIC_TABLE,
    SQL_ALEMBIC_VERSION,
    SQL_CHECK_TABLE_EXISTS,
    SQL_TABLE_COLUMNS,
    SQL_TABLE_INDEXES,
    SQL_TABLE_CONSTRAINTS,
    SQL_TABLE_RLS,
    SQL_TABLE_POLICIES,
    SQL_TABLE_GRANTS,
    verify_canonical_schema
)


def validate_preflight_environment(url_override: str = None) -> Tuple[str, DatabaseIdentity]:
    """
    Validates staging environment preconditions and verifies target is not production.
    Fails closed if any precondition is unmet.
    """
    env = os.environ.get("ENVIRONMENT", "").strip().lower()
    if env != "staging":
        raise RuntimeError(
            f"FAIL CLOSED: ENVIRONMENT must be explicitly set to 'staging' (current: '{env or 'UNSET'}')."
        )

    confirm = os.environ.get("CONFIRM_READONLY_STAGING_PREFLIGHT", "").strip().lower()
    if confirm != "true":
        raise RuntimeError(
            "FAIL CLOSED: CONFIRM_READONLY_STAGING_PREFLIGHT must be explicitly set to 'true'."
        )

    raw_url = url_override or os.environ.get("STAGING_DATABASE_URL", "").strip()
    if not raw_url:
        raise RuntimeError("FAIL CLOSED: STAGING_DATABASE_URL is missing or empty.")

    identity = normalize_db_identity(raw_url, "STAGING_DATABASE_URL")
    if is_production_target(raw_url, identity):
        raise RuntimeError(
            f"FAIL CLOSED: Target matches production Supabase reference ({PROD_SUPABASE_PROJECT_REF}). "
            "Connecting to production from preflight is strictly prohibited."
        )

    return raw_url, identity


async def inspect_staging_database(url_override: str = None) -> Dict[str, Any]:
    """
    Executes read-only catalog inspection against authorized staging database.
    Does not create, alter, drop, or update any database objects.
    """
    raw_url, identity = validate_preflight_environment(url_override)
    engine = create_async_engine(raw_url, isolation_level="AUTOCOMMIT")

    report: Dict[str, Any] = {
        "target_endpoint": identity.sanitized_endpoint,
        "database_name": identity.database,
        "host": identity.host,
        "port": identity.port,
        "is_production": False,
        "tables": {}
    }

    try:
        async with engine.connect() as conn:
            # Enforce read-only transaction state
            await conn.execute(text("SET TRANSACTION READ ONLY;"))

            # 1. Server Version & Current Database
            ver_res = (await conn.execute(text(SQL_DB_VERSION))).fetchone()
            report["server_database"] = ver_res[0] if ver_res else "unknown"
            report["server_version"] = ver_res[1] if ver_res else "unknown"

            # 2. Alembic Version
            has_alembic = (await conn.execute(text(SQL_CHECK_ALEMBIC_TABLE))).scalar()
            report["alembic_table_exists"] = bool(has_alembic)
            if has_alembic:
                ver = (await conn.execute(text(SQL_ALEMBIC_VERSION))).scalar()
                report["current_alembic_version"] = ver
            else:
                report["current_alembic_version"] = None

            # 3. Target Migration Tables
            for table_name in ["business_context", "product_images"]:
                exists = (await conn.execute(text(SQL_CHECK_TABLE_EXISTS), {"table_name": table_name})).scalar()
                table_info: Dict[str, Any] = {"exists": bool(exists)}
                if exists:
                    # Columns
                    cols = (await conn.execute(text(SQL_TABLE_COLUMNS), {"table_name": table_name})).fetchall()
                    table_info["columns"] = [
                        {"name": c[0], "type": c[1], "max_len": c[2], "nullable": c[3], "default": c[4]}
                        for c in cols
                    ]
                    # Indexes
                    idxs = (await conn.execute(text(SQL_TABLE_INDEXES), {"table_name": table_name})).fetchall()
                    table_info["indexes"] = [{"name": i[0], "def": i[1]} for i in idxs]
                    # Constraints
                    cons = (await conn.execute(text(SQL_TABLE_CONSTRAINTS), {"table_name": table_name})).fetchall()
                    table_info["constraints"] = [
                        {"name": k[0], "type": k[1], "col": k[2], "f_table": k[3], "f_col": k[4], "delete_rule": k[5]}
                        for k in cons
                    ]
                    # RLS
                    rls = (await conn.execute(text(SQL_TABLE_RLS), {"table_name": table_name})).fetchone()
                    table_info["rls_enabled"] = bool(rls[0]) if rls else False
                    table_info["rls_forced"] = bool(rls[1]) if rls else False
                    # Policies
                    pols = (await conn.execute(text(SQL_TABLE_POLICIES), {"table_name": table_name})).fetchall()
                    table_info["policies"] = [{"name": p[0], "permissive": p[1], "roles": p[2], "cmd": p[3]} for p in pols]
                    # Grants
                    grants = (await conn.execute(text(SQL_TABLE_GRANTS), {"table_name": table_name})).fetchall()
                    table_info["grants"] = [{"grantee": g[0], "privilege": g[1], "grantable": g[2]} for g in grants]

                report["tables"][table_name] = table_info

    finally:
        await engine.dispose()

    # Classification logic based on strict schema verification
    is_canonical, issues = verify_canonical_schema(report)
    report["is_canonical"] = is_canonical
    report["verification_issues"] = issues

    bc_exists = report["tables"]["business_context"]["exists"]
    pi_exists = report["tables"]["product_images"]["exists"]
    ver = report["current_alembic_version"]

    if is_canonical:
        report["classification"] = "MIGRATED_CANONICAL"
    elif not bc_exists and not pi_exists and (ver is None or ver == "c1412562210a"):
        report["classification"] = "FRESH_ISOLATED"
    elif pi_exists and not bc_exists:
        report["classification"] = "DRIFTED_LEGACY_STORAGE"
    else:
        report["classification"] = "CUSTOM_OR_PARTIAL"

    return report


def format_preflight_report(report: Dict[str, Any]) -> str:
    """Renders structured preflight inspection report for human review."""
    lines = [
        "============================================================",
        "  AUTOMIND REMOTE STAGING READ-ONLY PREFLIGHT REPORT",
        "============================================================",
        f"Target Endpoint (Sanitized): {report['target_endpoint']}",
        f"Database Name:               {report['database_name']}",
        f"Server Host:Port:            {report['host']}:{report['port']}",
        f"Server PostgreSQL Version:   {report.get('server_version', 'unknown')[:60]}...",
        f"Alembic Version Table:       {'PRESENT' if report['alembic_table_exists'] else 'ABSENT'}",
        f"Current Alembic Revision:    {report['current_alembic_version'] or 'NONE'}",
        f"Schema Classification:       {report['classification']}",
        "------------------------------------------------------------",
        "Target Migration Tables Inspection:"
    ]

    for tname, tinfo in report["tables"].items():
        lines.append(f"\n[Table: {tname}]")
        if not tinfo["exists"]:
            lines.append("  Status: DOES NOT EXIST (Safe for fresh Alembic migration)")
            continue

        lines.append(f"  Status:        EXISTS ({len(tinfo['columns'])} columns)")
        lines.append(f"  RLS Enabled:   {tinfo['rls_enabled']} (Forced: {tinfo['rls_forced']})")
        lines.append(f"  RLS Policies:  {len(tinfo['policies'])} active")
        lines.append(f"  Indexes:       {len(tinfo['indexes'])}")
        lines.append(f"  Constraints:   {len(tinfo['constraints'])}")
        lines.append("  Columns:")
        for c in tinfo["columns"]:
            lines.append(f"    - {c['name']}: {c['type']} (nullable={c['nullable']}, default={c['default']})")

    if report.get("verification_issues"):
        lines.append("\n------------------------------------------------------------")
        lines.append("Schema Verification Discrepancies (Prevents MIGRATED_CANONICAL):")
        for issue in report["verification_issues"]:
            lines.append(f"  [!] {issue}")

    lines.append("============================================================")
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        data = asyncio.run(inspect_staging_database())
        print(format_preflight_report(data))
    except Exception as exc:
        print(f"\n[PREFLIGHT ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
