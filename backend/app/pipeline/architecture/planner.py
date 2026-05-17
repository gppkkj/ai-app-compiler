from typing import Dict, Any, List


def _title(name: str) -> str:
    return name.replace("_", " ").title().replace(" ", "")


def _route(entity: str) -> str:
    return "/" + entity.replace("_", "-")


def _service(entity: str) -> str:
    return _title(entity) + "Service"


def _page(entity: str) -> str:
    return _title(entity)


def _component(entity: str) -> str:
    return _title(entity) + "Table"


def _permissions_for_role(role: str) -> List[str]:
    if role == "admin":
        return ["create", "read", "update", "delete", "manage_users", "view_analytics"]
    if role in ["manager", "seller", "agent", "instructor"]:
        return ["create", "read", "update"]
    return ["read"]


def generate_architecture(intent: Dict[str, Any]) -> Dict[str, Any]:
    features = intent.get("features", [])
    roles = intent.get("roles", ["admin", "user"])
    entities = intent.get("entities", ["users", "resources"])

    pages: List[str] = []
    components: List[str] = []
    services: List[str] = []
    endpoints: List[str] = []
    tables: List[str] = []

    # Base UI
    if "authentication" in features:
        pages.append("Login")

    pages.append("Dashboard")
    components.extend(["Navbar", "Sidebar", "AnalyticsCard"])

    # Entity-driven architecture
    for entity in entities:
        tables.append(entity)

        if entity != "users":
            pages.append(_page(entity))
            components.append(_component(entity))
            services.append(_service(entity))
            endpoints.append(_route(entity))

    # Auth service and endpoint
    if "authentication" in features or "users" in entities:
        services.insert(0, "AuthService")
        endpoints.insert(0, "/login")

    # Feature-specific services/endpoints
    if "premium subscriptions" in features and "subscriptions" not in tables:
        tables.append("subscriptions")
        pages.append("Subscriptions")
        components.append("SubscriptionTable")
        services.append("SubscriptionService")
        endpoints.append("/subscriptions")

    if "payments" in features and "payments" not in tables:
        tables.append("payments")
        pages.append("Payments")
        components.append("PaymentTable")
        services.append("PaymentService")
        endpoints.append("/payments")

    if "analytics dashboard" in features:
        services.append("AnalyticsService")
        endpoints.append("/analytics")
        if "AnalyticsCard" not in components:
            components.append("AnalyticsCard")

    # Remove duplicates
    pages = list(dict.fromkeys(pages))
    components = list(dict.fromkeys(components))
    services = list(dict.fromkeys(services))
    endpoints = list(dict.fromkeys(endpoints))
    tables = list(dict.fromkeys(tables))

    permissions = {
        role: _permissions_for_role(role)
        for role in roles
    }

    # Business flows are architecture-level workflows
    flows = []

    if "authentication" in features:
        flows.append({
            "name": "login_flow",
            "steps": ["submit_credentials", "validate_user", "issue_session"]
        })

    if "premium subscriptions" in features:
        flows.append({
            "name": "subscription_flow",
            "steps": ["select_plan", "create_subscription", "activate_premium_access"]
        })

    if "payments" in features:
        flows.append({
            "name": "payment_flow",
            "steps": ["create_checkout", "process_payment", "store_payment_status"]
        })

    if "analytics dashboard" in features:
        flows.append({
            "name": "analytics_flow",
            "steps": ["collect_metrics", "aggregate_data", "render_dashboard"]
        })

    return {
        "frontend": {
            "pages": pages,
            "components": components
        },
        "backend": {
            "services": services,
            "endpoints": endpoints
        },
        "database": {
            "tables": tables
        },
        "auth": {
            "roles": roles,
            "permissions": permissions
        },
        "flows": flows
    }