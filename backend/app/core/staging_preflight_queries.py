"""
SQL catalog queries and schema comparison helpers for staging preflight inspection.
Contains exclusively read-only queries against PostgreSQL system catalogs.
"""

SQL_DB_VERSION = "SELECT current_database(), version();"

SQL_CHECK_ALEMBIC_TABLE = """
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'alembic_version'
);
"""

SQL_ALEMBIC_VERSION = "SELECT version_num FROM alembic_version LIMIT 1;"

SQL_CHECK_TABLE_EXISTS = """
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = :table_name
);
"""

SQL_TABLE_COLUMNS = """
SELECT 
    column_name, 
    data_type, 
    character_maximum_length, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = :table_name
ORDER BY ordinal_position;
"""

SQL_TABLE_INDEXES = """
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = :table_name
ORDER BY indexname;
"""

SQL_TABLE_CONSTRAINTS = """
SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON rc.unique_constraint_name = ccu.constraint_name AND rc.unique_constraint_schema = ccu.constraint_schema
WHERE tc.table_schema = 'public' AND tc.table_name = :table_name
ORDER BY tc.constraint_name;
"""

SQL_TABLE_RLS = """
SELECT relrowsecurity, relforcerowsecurity
FROM pg_class
WHERE relname = :table_name AND relnamespace = 'public'::regnamespace;
"""

SQL_TABLE_POLICIES = """
SELECT policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = :table_name
ORDER BY policyname;
"""

SQL_TABLE_GRANTS = """
SELECT grantee, privilege_type, is_grantable
FROM information_schema.role_table_grants
WHERE table_schema = 'public' AND table_name = :table_name
ORDER BY grantee, privilege_type;
"""

CANONICAL_SPEC = {
    "alembic_head": "d8f3a1e5c2b4",
    "tables": {
        "business_context": {
            "columns": {
                "id": {"type": "uuid", "nullable": "NO"},
                "project_id": {"type": "uuid", "nullable": "NO"},
                "context_type": {"type": "character varying", "nullable": "NO"},
                "context_key": {"type": "character varying", "nullable": "NO"},
                "title": {"type": "character varying", "nullable": "NO"},
                "content": {"type": "text", "nullable": "NO"},
                "tags": {"type": "jsonb", "nullable": "YES"},
                "relevance_score": {"type": "double precision", "nullable": "YES"},
                "times_used": {"type": "integer", "nullable": "YES"},
                "learned_from": {"type": "character varying", "nullable": "YES"},
                "confidence_score": {"type": "double precision", "nullable": "YES"},
                "active_for_platforms": {"type": "jsonb", "nullable": "YES"},
                "examples": {"type": "jsonb", "nullable": "YES"},
                "is_active": {"type": "boolean", "nullable": "YES"},
                "last_used": {"type": "timestamp with time zone", "nullable": "YES"},
                "created_at": {"type": "timestamp with time zone", "nullable": "NO"},
                "updated_at": {"type": "timestamp with time zone", "nullable": "YES"},
            },
            "indexes": [
                "idx_business_context_project",
                "idx_business_context_type",
                "idx_business_context_key",
                "idx_business_context_used",
            ],
            "foreign_keys": [
                {"col": "project_id", "f_table": "projects", "f_col": "id", "delete_rule": "CASCADE"}
            ],
            "rls_required": True,
        },
        "product_images": {
            "columns": {
                "key": {"type": "character varying", "nullable": "NO"},
                "project_id": {"type": "uuid", "nullable": "YES"},
                "data": {"type": "bytea", "nullable": "NO"},
                "content_type": {"type": "character varying", "nullable": "NO"},
                "size": {"type": "integer", "nullable": "NO"},
                "created_at": {"type": "timestamp with time zone", "nullable": "NO"},
                "updated_at": {"type": "timestamp with time zone", "nullable": "YES"},
            },
            "indexes": [
                "idx_product_images_project_id",
            ],
            "foreign_keys": [
                {"col": "project_id", "f_table": "projects", "f_col": "id", "delete_rule": "CASCADE"}
            ],
            "rls_required": True,
        }
    }
}


def verify_canonical_schema(report: dict) -> tuple[bool, list[str]]:
    """
    Rigorously verifies that a database schema matches the canonical Alembic migration definitions.
    Checks exact column existence, data types, nullability, primary/foreign keys, indexes, and RLS.
    Returns (True, []) if canonical, or (False, [issues]) if any discrepancy exists.
    """
    issues = []
    ver = report.get("current_alembic_version")
    if ver != CANONICAL_SPEC["alembic_head"]:
        issues.append(f"Alembic revision mismatch: expected '{CANONICAL_SPEC['alembic_head']}', got '{ver}'")

    tables_report = report.get("tables", {})
    for tname, spec in CANONICAL_SPEC["tables"].items():
        if tname not in tables_report or not tables_report[tname].get("exists"):
            issues.append(f"Required canonical table '{tname}' does not exist")
            continue

        tinfo = tables_report[tname]
        col_map = {c["name"]: c for c in tinfo.get("columns", [])}

        # Verify all expected columns
        for col_name, c_spec in spec["columns"].items():
            if col_name not in col_map:
                issues.append(f"Table '{tname}' is missing column '{col_name}'")
            else:
                actual = col_map[col_name]
                if actual["nullable"] != c_spec["nullable"]:
                    issues.append(
                        f"Table '{tname}.{col_name}' nullability mismatch: expected {c_spec['nullable']}, got {actual['nullable']}"
                    )

        # Verify indexes
        idx_names = {i["name"] for i in tinfo.get("indexes", [])}
        for exp_idx in spec["indexes"]:
            if exp_idx not in idx_names:
                issues.append(f"Table '{tname}' is missing required index '{exp_idx}'")

        # Verify foreign keys
        cons = tinfo.get("constraints", [])
        for exp_fk in spec["foreign_keys"]:
            matched = any(
                c.get("col") == exp_fk["col"] and
                c.get("f_table") == exp_fk["f_table"] and
                c.get("f_col") == exp_fk["f_col"] and
                c.get("delete_rule") == exp_fk["delete_rule"]
                for c in cons
            )
            if not matched:
                issues.append(
                    f"Table '{tname}' is missing foreign key on '{exp_fk['col']}' -> {exp_fk['f_table']}({exp_fk['f_col']}) ON DELETE {exp_fk['delete_rule']}"
                )

        # Verify RLS
        if spec.get("rls_required") and not tinfo.get("rls_enabled"):
            issues.append(f"Table '{tname}' does not have Row-Level Security (RLS) enabled")

    return len(issues) == 0, issues

