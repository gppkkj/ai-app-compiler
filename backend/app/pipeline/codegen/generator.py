import os
import json
from typing import Dict, Any, List


PYTHON_TYPE_MAP = {
    "integer": "int",
    "string": "str",
    "float": "float",
    "datetime": "str",
    "boolean": "bool"
}


def _safe_filename(name: str) -> str:
    return name.strip("/").replace("-", "_").replace(" ", "_") or "root"


def _class_name(name: str) -> str:
    return name.replace("_", " ").title().replace(" ", "")


def _python_type(field_type: str) -> str:
    return PYTHON_TYPE_MAP.get(field_type, "str")


def generate_code_artifacts(runtime: Dict[str, Any]) -> List[str]:
    generated_files: List[str] = []

    os.makedirs("generated/backend/routes", exist_ok=True)
    os.makedirs("generated/backend/models", exist_ok=True)
    os.makedirs("generated/frontend/pages", exist_ok=True)
    os.makedirs("generated/runtime", exist_ok=True)

    # -------------------------
    # Runtime manifest
    # -------------------------
    manifest_path = "generated/runtime/runtime_manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(runtime, file, indent=2)

    generated_files.append(manifest_path)

    # -------------------------
    # Backend route files
    # -------------------------
    for route in runtime.get("backend_routes", []):
        handler_name = route.get("handler", "handler")
        path = route.get("path", "/")
        method = route.get("method", "GET").lower()

        filename = f"{handler_name}.py"
        filepath = os.path.join("generated/backend/routes", filename)

        decorator = method if method in ["get", "post", "put", "patch", "delete"] else "get"

        code = f'''from fastapi import APIRouter

router = APIRouter()


@router.{decorator}("{path}")
async def {handler_name}():
    return {{
        "route": "{path}",
        "method": "{route.get("method", "GET")}",
        "status": "executed",
        "message": "Generated runtime route executed successfully",
        "auth_required": {str(route.get("auth_required", True))},
        "roles_allowed": {route.get("roles_allowed", [])}
    }}
'''

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(code)

        generated_files.append(filepath)

    # -------------------------
    # Database model files
    # -------------------------
    for model in runtime.get("database_models", []):
        table = model.get("table", "resource")
        filename = f"{table}.py"
        filepath = os.path.join("generated/backend/models", filename)

        class_name = model.get("model_name", _class_name(table))

        fields_code = ""

        for field, field_type in model.get("fields", {}).items():
            fields_code += f"    {field}: {_python_type(field_type)}\n"

        if not fields_code.strip():
            fields_code = "    pass\n"

        code = f'''from pydantic import BaseModel


class {class_name}(BaseModel):
{fields_code}
'''

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(code)

        generated_files.append(filepath)

    # -------------------------
    # Frontend page stubs
    # -------------------------
    for page in runtime.get("frontend_pages", []):
        page_name = page.get("page_name", "Page")
        filename = f"{_safe_filename(page_name)}.tsx"
        filepath = os.path.join("generated/frontend/pages", filename)

        components = page.get("components", [])
        api_bindings = page.get("api_bindings", [])

        code = f'''export default function {page_name.replace(" ", "")}Page() {{
  return (
    <main>
      <h1>{page_name}</h1>
      <p>Generated page route: {page.get("route")}</p>
      <p>Layout: {page.get("layout")}</p>
      <pre>{json.dumps({"components": components, "api_bindings": api_bindings}, indent=2)}</pre>
    </main>
  );
}}
'''

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(code)

        generated_files.append(filepath)

    return generated_files