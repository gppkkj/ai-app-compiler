from copy import deepcopy
from typing import Dict, Any, List, Tuple


def _route(entity: str) -> str:
    return "/" + entity.replace("_", "-")


def _entity_from_path(path: str) -> str:
    return path.strip("/").replace("-", "_")


def _default_fields_for_table(table: str) -> Dict[str, str]:
    common = {
        "id": "integer",
        "created_at": "datetime",
        "updated_at": "datetime"
    }

    if table == "users":
        return {
            **common,
            "email": "string",
            "password_hash": "string",
            "role": "string"
        }

    if table in ["contacts", "customers"]:
        return {
            **common,
            "user_id": "integer",
            "name": "string",
            "email": "string",
            "phone": "string"
        }

    if table == "subscriptions":
        return {
            **common,
            "user_id": "integer",
            "plan": "string",
            "status": "string",
            "started_at": "datetime"
        }

    if table == "payments":
        return {
            **common,
            "user_id": "integer",
            "amount": "float",
            "status": "string",
            "provider": "string"
        }

    if table in ["products", "menu_items", "resources"]:
        return {
            **common,
            "name": "string",
            "description": "string",
            "price": "float",
            "status": "string"
        }

    if table == "orders":
        return {
            **common,
            "user_id": "integer",
            "status": "string",
            "total_amount": "float"
        }

    if table == "cart_items":
        return {
            **common,
            "user_id": "integer",
            "item_id": "integer",
            "quantity": "integer"
        }

    return {
        **common,
        "user_id": "integer",
        "name": "string",
        "status": "string"
    }


def _relations_for_table(table: str, fields: Dict[str, str]) -> List[Dict[str, str]]:
    relations = []

    if table != "users" and "user_id" in fields:
        relations.append({
            "field": "user_id",
            "references": "users.id"
        })

    if "item_id" in fields:
        relations.append({
            "field": "item_id",
            "references": "menu_items.id"
        })

    return relations


def _make_table(table: str) -> Dict[str, Any]:
    fields = _default_fields_for_table(table)

    return {
        "name": table,
        "fields": fields,
        "primary_key": "id",
        "relations": _relations_for_table(table, fields),
        "constraints": {
            "id": "required unique",
            "created_at": "required",
            "updated_at": "required"
        }
    }


def _make_api(path: str, roles: List[str]) -> Dict[str, Any]:
    if path == "/login":
        return {
            "path": "/login",
            "method": "POST",
            "auth_required": False,
            "roles_allowed": ["public"],
            "request_schema": {
                "email": "string",
                "password": "string"
            },
            "response_schema": {
                "token": "string",
                "role": "string"
            },
            "validation": [
                "email is required",
                "password is required"
            ],
            "error_responses": {
                "400": "Invalid request",
                "401": "Invalid credentials",
                "500": "Internal server error"
            }
        }

    entity = _entity_from_path(path)

    return {
        "path": path,
        "method": "GET",
        "auth_required": True,
        "roles_allowed": roles,
        "request_schema": {},
        "response_schema": {
            entity: "array"
        },
        "validation": [
            "required fields must be present",
            "field types must match schema"
        ],
        "error_responses": {
            "400": "Invalid request",
            "401": "Unauthorized",
            "403": "Forbidden",
            "500": "Internal server error"
        }
    }


def _make_ui_page(page_name: str, api_paths: List[str], roles: List[str]) -> Dict[str, Any]:
    route = "/" + page_name.lower().replace(" ", "-").replace("_", "-")

    bindings = []

    key = page_name.lower().replace(" ", "_")

    for path in api_paths:
        path_key = path.strip("/").replace("-", "_")
        if path_key in key or key in path_key:
            bindings.append(path)

    if page_name == "Dashboard" and "/analytics" in api_paths:
        bindings.append("/analytics")

    return {
        "name": page_name,
        "route": route,
        "layout": "PublicLayout" if page_name == "Login" else "AuthenticatedLayout",
        "components": ["Navbar", "Sidebar", page_name + "View"] if page_name != "Login" else ["LoginForm"],
        "access": ["public"] if page_name == "Login" else roles,
        "api_bindings": list(dict.fromkeys(bindings))
    }


def _make_auth(role: str) -> Dict[str, Any]:
    if role == "admin":
        permissions = ["create", "read", "update", "delete", "manage_users", "view_analytics"]
    elif role in ["manager", "seller", "agent", "instructor"]:
        permissions = ["create", "read", "update"]
    else:
        permissions = ["read"]

    return {
        "role": role,
        "permissions": permissions
    }


def _ensure_business_logic(intent: Dict[str, Any], schema: Dict[str, Any], repair_log: List[Dict[str, str]]) -> None:
    if "business_logic" not in schema:
        schema["business_logic"] = []
        repair_log.append({
            "issue": "Missing business_logic section",
            "repair": "Added empty business_logic list"
        })

    rule_names = [rule.get("name") for rule in schema.get("business_logic", [])]
    features = intent.get("features", [])
    roles = intent.get("roles", [])

    if "premium subscriptions" in features and "premium_gating" not in rule_names:
        schema["business_logic"].append({
            "name": "premium_gating",
            "condition": "subscription.status == active",
            "effect": "allow premium-only features"
        })
        repair_log.append({
            "issue": "Premium feature missing premium_gating rule",
            "repair": "Added premium_gating business rule"
        })

    if "payments" in features and "payment_required_for_premium" not in rule_names:
        schema["business_logic"].append({
            "name": "payment_required_for_premium",
            "condition": "payment.status == successful",
            "effect": "activate subscription"
        })
        repair_log.append({
            "issue": "Payments feature missing payment business rule",
            "repair": "Added payment_required_for_premium rule"
        })

    if "analytics dashboard" in features and "admin" in roles and "admin_analytics_access" not in rule_names:
        schema["business_logic"].append({
            "name": "admin_analytics_access",
            "condition": "user.role == admin",
            "effect": "allow analytics dashboard access"
        })
        repair_log.append({
            "issue": "Admin analytics missing access rule",
            "repair": "Added admin_analytics_access business rule"
        })


def repair_schema(
    intent: Dict[str, Any],
    architecture: Dict[str, Any],
    schema: Dict[str, Any],
    validation: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:

    repaired_schema = deepcopy(schema)
    repair_log: List[Dict[str, str]] = []

    # Ensure top-level sections
    for key, default_value in {
        "database": [],
        "api": [],
        "ui": [],
        "auth": [],
        "business_logic": []
    }.items():
        if key not in repaired_schema:
            repaired_schema[key] = default_value
            repair_log.append({
                "issue": f"Missing top-level key: {key}",
                "repair": f"Added {key} section"
            })

    roles = architecture.get("auth", {}).get("roles", intent.get("roles", ["admin", "user"]))

    # Ensure DB tables from intent and architecture
    existing_tables = [
        table.get("name")
        for table in repaired_schema.get("database", [])
        if table.get("name")
    ]

    required_tables = list(dict.fromkeys(
        intent.get("entities", []) + architecture.get("database", {}).get("tables", [])
    ))

    for table in required_tables:
        if table not in existing_tables:
            repaired_schema["database"].append(_make_table(table))
            existing_tables.append(table)
            repair_log.append({
                "issue": f"Missing database table: {table}",
                "repair": f"Added {table} table with fields, primary key, relations, and constraints"
            })

    # Repair existing DB table contracts
    for table in repaired_schema.get("database", []):
        table_name = table.get("name", "unknown_table")

        if "fields" not in table or not isinstance(table.get("fields"), dict):
            table["fields"] = _default_fields_for_table(table_name)
            repair_log.append({
                "issue": f"Table {table_name} missing or invalid fields",
                "repair": "Added default typed fields"
            })

        if "primary_key" not in table:
            table["primary_key"] = "id"
            repair_log.append({
                "issue": f"Table {table_name} missing primary_key",
                "repair": "Added primary_key=id"
            })

        if "relations" not in table:
            table["relations"] = _relations_for_table(table_name, table.get("fields", {}))
            repair_log.append({
                "issue": f"Table {table_name} missing relations",
                "repair": "Added inferred relations"
            })

        if "constraints" not in table:
            table["constraints"] = {
                "id": "required unique",
                "created_at": "required",
                "updated_at": "required"
            }
            repair_log.append({
                "issue": f"Table {table_name} missing constraints",
                "repair": "Added default constraints"
            })

    # Ensure API endpoints from architecture
    existing_paths = [
        endpoint.get("path")
        for endpoint in repaired_schema.get("api", [])
        if endpoint.get("path")
    ]

    required_paths = architecture.get("backend", {}).get("endpoints", [])

    for path in required_paths:
        if path not in existing_paths:
            repaired_schema["api"].append(_make_api(path, roles))
            existing_paths.append(path)
            repair_log.append({
                "issue": f"Missing API endpoint: {path}",
                "repair": f"Added strict API schema for {path}"
            })

    # Repair API contracts
    for endpoint in repaired_schema.get("api", []):
        path = endpoint.get("path", "/unknown")

        strict_api = _make_api(path, roles)

        for key, value in strict_api.items():
            if key not in endpoint:
                endpoint[key] = value
                repair_log.append({
                    "issue": f"API {path} missing {key}",
                    "repair": f"Added {key} to API schema"
                })

    # Ensure auth roles
    existing_roles = [
        auth.get("role")
        for auth in repaired_schema.get("auth", [])
        if auth.get("role")
    ]

    for role in roles:
        if role not in existing_roles:
            repaired_schema["auth"].append(_make_auth(role))
            existing_roles.append(role)
            repair_log.append({
                "issue": f"Missing auth role: {role}",
                "repair": f"Added auth permissions for {role}"
            })

    for auth in repaired_schema.get("auth", []):
        if "permissions" not in auth:
            auth["permissions"] = _make_auth(auth.get("role", "user"))["permissions"]
            repair_log.append({
                "issue": f"Role {auth.get('role')} missing permissions",
                "repair": "Added default permissions"
            })

    # Ensure UI pages from architecture
    existing_pages = [
        page.get("name")
        for page in repaired_schema.get("ui", [])
        if page.get("name")
    ]

    api_paths = [
        endpoint.get("path")
        for endpoint in repaired_schema.get("api", [])
        if endpoint.get("path")
    ]

    for page_name in architecture.get("frontend", {}).get("pages", []):
        if page_name not in existing_pages:
            repaired_schema["ui"].append(_make_ui_page(page_name, api_paths, roles))
            existing_pages.append(page_name)
            repair_log.append({
                "issue": f"Missing UI page: {page_name}",
                "repair": f"Added UI schema for {page_name}"
            })

    for page in repaired_schema.get("ui", []):
        strict_page = _make_ui_page(page.get("name", "Page"), api_paths, roles)

        for key, value in strict_page.items():
            if key not in page:
                page[key] = value
                repair_log.append({
                    "issue": f"UI page {page.get('name')} missing {key}",
                    "repair": f"Added {key} to UI schema"
                })

    # Ensure business rules
    _ensure_business_logic(intent, repaired_schema, repair_log)

    return repaired_schema, repair_log