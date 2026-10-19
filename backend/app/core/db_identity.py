"""
Database identity models and normalization utilities.
Excludes credentials and normalizes endpoints for strict identity comparison.
"""

from dataclasses import dataclass
from typing import Tuple
from urllib.parse import urlencode
from sqlalchemy.engine import make_url


@dataclass(frozen=True)
class DatabaseIdentity:
    """Normalized full database target identity without credentials."""
    dialect: str
    driver: str
    host: str
    port: int
    database: str
    query_params: Tuple[Tuple[str, str], ...]

    @property
    def sanitized_endpoint(self) -> str:
        """Formatted endpoint without credentials."""
        params_str = f"?{urlencode(self.query_params)}" if self.query_params else ""
        return f"{self.dialect}+{self.driver}://{self.host}:{self.port}/{self.database}{params_str}"


# Known production Supabase reference to prevent accidental test targeting
PROD_SUPABASE_PROJECT_REF = "ccejhzadokkjssjiwmxt"


def is_production_target(raw_url: str = "", identity: DatabaseIdentity = None) -> bool:
    """Checks whether a raw URL string or identity points to known production targets."""
    if raw_url and PROD_SUPABASE_PROJECT_REF in raw_url.lower():
        return True
    if identity and PROD_SUPABASE_PROJECT_REF in identity.host.lower():
        return True
    return False


def assert_not_production_target(raw_url: str, identity: DatabaseIdentity, url_label: str) -> None:
    """Raises a fail-closed error if raw_url or identity targets production."""
    if is_production_target(raw_url, identity):
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} targets the production Supabase reference ({PROD_SUPABASE_PROJECT_REF}). "
            "Testing against production is strictly prohibited."
        )


def is_loopback_host(host: str) -> bool:
    """Checks whether host points to loopback interface."""
    return host in ("localhost", "127.0.0.1", "::1")


def are_same_physical_target(a: DatabaseIdentity, b: DatabaseIdentity) -> bool:
    """Checks whether two identities reach the same database server and catalog."""
    if a.database != b.database:
        return False
    if a.port != b.port:
        return False
    if a.dialect != b.dialect:
        return False
    if is_loopback_host(a.host) and is_loopback_host(b.host):
        return True
    return a.host == b.host


def normalize_db_identity(raw_url: str, url_label: str) -> DatabaseIdentity:
    """
    Parse and extract normalized database identity attributes using SQLAlchemy make_url.
    Credentials (username/password) are completely excluded to prevent credential leakage.
    Rejects malformed or ambiguous URLs fail-closed.
    """
    if not raw_url or not isinstance(raw_url, str) or not raw_url.strip():
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} is missing, empty, or not a string. Halting before database initialization."
        )

    try:
        url_obj = make_url(raw_url.strip())
    except Exception as exc:
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} is malformed or invalid ({type(exc).__name__}). Halting before database initialization."
        ) from None

    backend = (url_obj.get_backend_name() or "").lower().strip()
    driver = (url_obj.get_driver_name() or "").lower().strip()
    if not backend:
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} has no dialect specified. Halting before database initialization."
        )

    raw_host = (url_obj.host or "").strip().lower()
    if not raw_host:
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} has no host or socket endpoint specified. Halting before database initialization."
        )
    if raw_host == "0.0.0.0":
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} specifies ambiguous host '0.0.0.0'. Halting before database initialization."
        )

    port = url_obj.port
    if not port:
        if backend == "postgresql":
            port = 5432
        else:
            raise RuntimeError(
                f"FAIL CLOSED: {url_label} has no port specified for dialect '{backend}'. Halting before database initialization."
            )
    elif port < 1 or port > 65535:
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} specifies invalid port {port}. Halting before database initialization."
        )

    raw_db = (url_obj.database or "").strip()
    database = raw_db.lstrip("/").lower()
    if not database:
        raise RuntimeError(
            f"FAIL CLOSED: {url_label} has no database name specified. Halting before database initialization."
        )

    query_params: Tuple[Tuple[str, str], ...] = ()
    if url_obj.query:
        query_params = tuple(sorted((k.lower(), str(v).lower()) for k, v in url_obj.query.items()))

    return DatabaseIdentity(
        dialect=backend,
        driver=driver,
        host=raw_host,
        port=port,
        database=database,
        query_params=query_params,
    )
