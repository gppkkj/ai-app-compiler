from typing import Dict, Any, List


def _route(entity: str) -> str:
    return "/" + entity.replace("_", "-")


def _entity_from_path(path: str) -> str:
    return path.strip("/").replace("-", "_")


def _title(name: str) -> str:
    return name.replace("_", " ").title().replace(" ", "")


def _camel_to_kebab(name: str) -> str:
    result = ""

    for index, char in enumerate(name):
        if char.isupper() and index != 0:
            result += "-"

        result += char.lower()

    return result


def _normalize_key(value: str) -> str:
    return (
        value.lower()
        .replace("/", "")
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )


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

    if table in ["appointments", "time_slots"]:
        return {
            **common,
            "user_id": "integer",
            "scheduled_at": "datetime",
            "status": "string"
        }

    if table in [
        "courses",
        "quizzes",
        "projects",
        "tasks",
        "tickets",
        "employees",
        "inventory_items",
        "suppliers"
    ]:
        return {
            **common,
            "user_id": "integer",
            "title": "string",
            "status": "string"
        }

    return {
        **common,
        "user_id": "integer",
        "name": "string",
        "status": "string"
    }


def _relations_for_table(
    table: str,
    fields: Dict[str, str],
    all_tables: List[str]
) -> List[Dict[str, str]]:
    relations = []

    if table != "users" and "user_id" in fields and "users" in all_tables:
        relations.append({
            "field": "user_id",
            "references": "users.id"
        })

    if table == "cart_items" and "item_id" in fields:
        if "menu_items" in all_tables:
            item_reference = "menu_items.id"
        elif "products" in all_tables:
            item_reference = "products.id"
        else:
            item_reference = None

        if item_reference:
            relations.append({
                "field": "item_id",
                "references": item_reference
            })

    return relations


def _api_method_for_path(path: str) -> str:
    if path == "/login":
        return "POST"

    return "GET"


def _request_schema_for_path(path: str) -> Dict[str, str]:
    if path == "/login":
        return {
            "email": "string",
            "password": "string"
        }

    if path in ["/payments", "/subscriptions", "/orders"]:
        return {
            "user_id": "integer",
            "status": "string"
        }

    return {}


def _response_schema_for_path(path: str) -> Dict[str, str]:
    if path == "/login":
        return {
            "token": "string",
            "role": "string"
        }

    entity = _entity_from_path(path)

    return {
        entity: "array"
    }


def _roles_allowed_for_path(path: str, roles: List[str]) -> List[str]:
    if path == "/login":
        return ["public"]

    if path in ["/analytics", "/payments"]:
        return ["admin"] if "admin" in roles else roles

    return roles


def _ui_route(page: str) -> str:
    if page == "Dashboard":
        return "/dashboard"

    if page == "Login":
        return "/login"

    return "/" + _camel_to_kebab(page)


def _components_for_page(page: str, architecture: Dict[str, Any]) -> List[str]:
    components = architecture.get("frontend", {}).get("components", [])

    page_key = _normalize_key(page)

    selected = []

    if page == "Login":
        selected.append("LoginView")
        return selected

    selected.extend(["Navbar", "Sidebar"])

    for component in components:
        component_key = _normalize_key(component)

        if page_key in component_key or component_key in page_key:
            selected.append(component)

    if page == "Dashboard":
        selected.append("AnalyticsCard")

    if len(selected) == 2:
        selected.append(page + "View")

    return list(dict.fromkeys(selected))


def _api_bindings_for_page(page: str, api_paths: List[str]) -> List[str]:
    page_key = _normalize_key(page)

    bindings = []

    for path in api_paths:
        path_key = _normalize_key(path)

        if path_key == page_key:
            bindings.append(path)

        elif path_key in page_key:
            bindings.append(path)

        elif page_key in path_key:
            bindings.append(path)

    if page == "Dashboard" and "/analytics" in api_paths:
        bindings.append("/analytics")

    return list(dict.fromkeys(bindings))


def _business_logic(intent: Dict[str, Any]) -> List[Dict[str, str]]:
    features = intent.get("features", [])
    roles = intent.get("roles", [])

    rules = []

    if "premium subscriptions" in features:
        rules.append({
            "name": "premium_gating",
            "condition": "subscription.status == active",
            "effect": "allow premium-only features"
        })

    if "payments" in features:
        rules.append({
            "name": "payment_required_for_premium",
            "condition": "payment.status == successful",
            "effect": "activate subscription"
        })

    if "analytics dashboard" in features and "admin" in roles:
        rules.append({
            "name": "admin_analytics_access",
            "condition": "user.role == admin",
            "effect": "allow analytics dashboard access"
        })

    if "authentication" in features:
        rules.append({
            "name": "authenticated_access",
            "condition": "valid session token exists",
            "effect": "allow protected API access"
        })

    return rules


def generate_schema(intent: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
    tables = architecture.get("database", {}).get("tables", [])
    endpoints = architecture.get("backend", {}).get("endpoints", [])
    pages = architecture.get("frontend", {}).get("pages", [])

    roles = architecture.get(
        "auth",
        {}
    ).get(
        "roles",
        intent.get("roles", ["admin", "user"])
    )

    permissions = architecture.get("auth", {}).get("permissions", {})

    database = []

    for table in tables:
        fields = _default_fields_for_table(table)

        database.append({
            "name": table,
            "fields": fields,
            "primary_key": "id",
            "relations": _relations_for_table(table, fields, tables),
            "constraints": {
                "id": "required unique",
                "created_at": "required",
                "updated_at": "required"
            }
        })

    api = []

    for path in endpoints:
        api.append({
            "path": path,
            "method": _api_method_for_path(path),
            "auth_required": path != "/login",
            "roles_allowed": _roles_allowed_for_path(path, roles),
            "request_schema": _request_schema_for_path(path),
            "response_schema": _response_schema_for_path(path),
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
        })

    api_paths = [item["path"] for item in api]

    ui = []

    for page in pages:
        ui.append({
            "name": page,
            "route": _ui_route(page),
            "layout": "AuthenticatedLayout" if page != "Login" else "PublicLayout",
            "components": _components_for_page(page, architecture),
            "access": roles if page != "Login" else ["public"],
            "api_bindings": _api_bindings_for_page(page, api_paths)
        })

    auth = []

    for role in roles:
        auth.append({
            "role": role,
            "permissions": permissions.get(role, ["read"])
        })

    return {
        "database": database,
        "api": api,
        "ui": ui,
        "auth": auth,
        "business_logic": _business_logic(intent)
    }