from typing import Dict, Any, List


REQUIRED_TOP_LEVEL_KEYS = [
    "database",
    "api",
    "ui",
    "auth",
    "business_logic"
]


REQUIRED_DB_KEYS = [
    "name",
    "fields",
    "primary_key",
    "relations",
    "constraints"
]


REQUIRED_API_KEYS = [
    "path",
    "method",
    "auth_required",
    "roles_allowed",
    "request_schema",
    "response_schema",
    "validation",
    "error_responses"
]


REQUIRED_UI_KEYS = [
    "name",
    "route",
    "layout",
    "components",
    "access",
    "api_bindings"
]


REQUIRED_AUTH_KEYS = [
    "role",
    "permissions"
]


def _entity_from_path(path: str) -> str:
    return path.strip("/").replace("-", "_")


def _table_names(schema: Dict[str, Any]) -> List[str]:
    return [table.get("name") for table in schema.get("database", []) if table.get("name")]


def _api_paths(schema: Dict[str, Any]) -> List[str]:
    return [api.get("path") for api in schema.get("api", []) if api.get("path")]


def _auth_roles(schema: Dict[str, Any]) -> List[str]:
    return [auth.get("role") for auth in schema.get("auth", []) if auth.get("role")]


def validate_schema(
    intent: Dict[str, Any],
    architecture: Dict[str, Any],
    schema: Dict[str, Any]
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []
    failure_types: List[str] = []

    # -------------------------
    # Top-level contract
    # -------------------------
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in schema:
            errors.append(f"Missing top-level key: {key}")
            failure_types.append("missing_top_level_key")

    # -------------------------
    # Database contract
    # -------------------------
    for table in schema.get("database", []):
        for key in REQUIRED_DB_KEYS:
            if key not in table:
                errors.append(f"Database table {table.get('name')} missing key: {key}")
                failure_types.append("database_contract_error")

        if not isinstance(table.get("fields", {}), dict):
            errors.append(f"Database table {table.get('name')} fields must be an object")
            failure_types.append("type_error")

    # -------------------------
    # API contract
    # -------------------------
    for endpoint in schema.get("api", []):
        for key in REQUIRED_API_KEYS:
            if key not in endpoint:
                errors.append(f"API endpoint {endpoint.get('path')} missing key: {key}")
                failure_types.append("api_contract_error")

        if endpoint.get("method") not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            errors.append(f"API endpoint {endpoint.get('path')} has invalid method")
            failure_types.append("api_method_error")

    # -------------------------
    # UI contract
    # -------------------------
    for page in schema.get("ui", []):
        for key in REQUIRED_UI_KEYS:
            if key not in page:
                errors.append(f"UI page {page.get('name')} missing key: {key}")
                failure_types.append("ui_contract_error")

        if not isinstance(page.get("components", []), list):
            errors.append(f"UI page {page.get('name')} components must be a list")
            failure_types.append("type_error")

    # -------------------------
    # Auth contract
    # -------------------------
    for auth in schema.get("auth", []):
        for key in REQUIRED_AUTH_KEYS:
            if key not in auth:
                errors.append(f"Auth rule {auth.get('role')} missing key: {key}")
                failure_types.append("auth_contract_error")

    # -------------------------
    # Cross-layer consistency
    # -------------------------
    tables = _table_names(schema)
    api_paths = _api_paths(schema)
    roles = _auth_roles(schema)

    # Intent entities should exist in DB
    for entity in intent.get("entities", []):
        if entity not in tables:
            errors.append(f"Intent entity '{entity}' missing from database schema")
            failure_types.append("cross_layer_entity_missing")

    # Architecture tables should exist in DB
    for table in architecture.get("database", {}).get("tables", []):
        if table not in tables:
            errors.append(f"Architecture table '{table}' missing from database schema")
            failure_types.append("cross_layer_table_missing")

        # DB relation references should point to existing tables
    for table in schema.get("database", []):
        for relation in table.get("relations", []):
            reference = relation.get("references", "")

            if "." in reference:
                referenced_table = reference.split(".")[0]

                if referenced_table not in tables:
                    errors.append(
                        f"Database relation in table '{table.get('name')}' references missing table '{referenced_table}'"
                    )
                    failure_types.append("db_relation_mismatch")

    # API resource should map to DB table unless system endpoint
    system_paths = ["/login", "/analytics"]

    for path in api_paths:
        if path not in system_paths:
            entity = _entity_from_path(path)
            if entity not in tables:
                errors.append(f"API path '{path}' does not map to any database table")
                failure_types.append("api_db_mismatch")

    # UI API bindings should exist in API schema
    for page in schema.get("ui", []):
        for binding in page.get("api_bindings", []):
            if binding not in api_paths:
                errors.append(f"UI page '{page.get('name')}' binds to missing API '{binding}'")
                failure_types.append("ui_api_mismatch")

    # Roles used in UI/API should exist in auth schema
    for endpoint in schema.get("api", []):
        for role in endpoint.get("roles_allowed", []):
            if role != "public" and role not in roles:
                errors.append(f"API endpoint '{endpoint.get('path')}' uses undefined role '{role}'")
                failure_types.append("undefined_role")

    for page in schema.get("ui", []):
        for role in page.get("access", []):
            if role != "public" and role not in roles:
                errors.append(f"UI page '{page.get('name')}' uses undefined role '{role}'")
                failure_types.append("undefined_role")

    # Business logic should be explicit for advanced features
    features = intent.get("features", [])

    if "premium subscriptions" in features:
        has_premium_rule = any(
            rule.get("name") == "premium_gating"
            for rule in schema.get("business_logic", [])
        )
        if not has_premium_rule:
            errors.append("Premium subscriptions feature missing premium_gating business rule")
            failure_types.append("business_logic_missing")

    if "analytics dashboard" in features and "admin" in intent.get("roles", []):
        has_admin_analytics_rule = any(
            rule.get("name") == "admin_analytics_access"
            for rule in schema.get("business_logic", [])
        )
        if not has_admin_analytics_rule:
            errors.append("Admin analytics feature missing admin_analytics_access business rule")
            failure_types.append("business_logic_missing")

    # Warning only: empty UI binding
    for page in schema.get("ui", []):
        if page.get("name") != "Login" and len(page.get("api_bindings", [])) == 0:
            warnings.append(f"UI page '{page.get('name')}' has no API bindings")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "failure_types": list(dict.fromkeys(failure_types))
    }