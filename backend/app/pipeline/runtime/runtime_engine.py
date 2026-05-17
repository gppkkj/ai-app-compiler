from typing import Dict, Any


def _handler_name(path: str) -> str:
    cleaned = path.strip("/").replace("-", "_")

    if cleaned == "":
        cleaned = "root"

    return f"{cleaned}_handler"


def _model_name(table: str) -> str:
    return table.replace("_", " ").title().replace(" ", "") + "Model"


def generate_runtime(schema: Dict[str, Any]) -> Dict[str, Any]:
    runtime = {
        "backend_routes": [],
        "frontend_pages": [],
        "database_models": [],
        "execution_plan": [],
        "runtime_status": "ready"
    }

    # Backend routes
    for endpoint in schema.get("api", []):
        path = endpoint.get("path")
        method = endpoint.get("method", "GET")

        route = {
            "path": path,
            "method": method,
            "handler": _handler_name(path),
            "auth_required": endpoint.get("auth_required", True),
            "roles_allowed": endpoint.get("roles_allowed", []),
            "request_schema": endpoint.get("request_schema", {}),
            "response_schema": endpoint.get("response_schema", {}),
            "executable": True
        }

        runtime["backend_routes"].append(route)

        runtime["execution_plan"].append({
            "type": "api_route",
            "target": path,
            "status": "mapped",
            "description": f"{method} {path} mapped to {_handler_name(path)}"
        })

    # Frontend pages
    for page in schema.get("ui", []):
        frontend_page = {
            "page_name": page.get("name"),
            "route": page.get("route"),
            "layout": page.get("layout"),
            "components": page.get("components", []),
            "access": page.get("access", []),
            "api_bindings": page.get("api_bindings", []),
            "executable": True
        }

        runtime["frontend_pages"].append(frontend_page)

        runtime["execution_plan"].append({
            "type": "frontend_page",
            "target": page.get("route"),
            "status": "mapped",
            "description": f"Page {page.get('name')} mapped to route {page.get('route')}"
        })

    # Database models
    for table in schema.get("database", []):
        model = {
            "table": table.get("name"),
            "model_name": _model_name(table.get("name")),
            "fields": table.get("fields", {}),
            "primary_key": table.get("primary_key", "id"),
            "relations": table.get("relations", []),
            "constraints": table.get("constraints", {}),
            "executable": True
        }

        runtime["database_models"].append(model)

        runtime["execution_plan"].append({
            "type": "database_model",
            "target": table.get("name"),
            "status": "mapped",
            "description": f"Table {table.get('name')} mapped to {_model_name(table.get('name'))}"
        })

    return runtime