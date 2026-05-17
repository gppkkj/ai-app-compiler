import json
import os
from app.evaluation.runner import run_evaluation

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.generate import router as generate_router

app = FastAPI(
    title="AI App Compiler",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(generate_router)


@app.get("/")
async def root():
    return {
        "message": "AI Compiler System Running",
        "runtime_preview": "/runtime/routes",
        "docs": "/docs"
    }


def _load_runtime_manifest():
    manifest_path = "generated/runtime/runtime_manifest.json"

    if not os.path.exists(manifest_path):
        return None

    with open(manifest_path, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/runtime/routes")
async def runtime_routes():
    runtime = _load_runtime_manifest()

    if runtime is None:
        return {
            "status": "not_ready",
            "message": "No runtime manifest found. Generate an app first using POST /generate."
        }

    return {
        "status": "ready",
        "routes": runtime.get("backend_routes", []),
        "frontend_pages": runtime.get("frontend_pages", []),
        "database_models": runtime.get("database_models", []),
        "execution_plan": runtime.get("execution_plan", [])
    }


@app.get("/runtime/{route_name}")
async def execute_runtime_route(route_name: str):
    runtime = _load_runtime_manifest()

    if runtime is None:
        return {
            "status": "not_ready",
            "message": "No runtime manifest found. Generate an app first using POST /generate."
        }

    normalized = "/" + route_name.replace("_", "-")

    matched_route = None

    for route in runtime.get("backend_routes", []):
        route_path = route.get("path", "")
        route_key = route_path.strip("/").replace("-", "_")

        if route_name == route_key or normalized == route_path:
            matched_route = route
            break

    if matched_route is None:
        return {
            "status": "not_found",
            "message": f"No generated runtime route found for {route_name}",
            "available_routes": [
                route.get("path")
                for route in runtime.get("backend_routes", [])
            ]
        }

    return {
        "status": "executed",
        "route": matched_route.get("path"),
        "method": matched_route.get("method"),
        "handler": matched_route.get("handler"),
        "auth_required": matched_route.get("auth_required"),
        "roles_allowed": matched_route.get("roles_allowed"),
        "response_schema": matched_route.get("response_schema"),
        "message": "Generated runtime route executed successfully"
    }
@app.get("/evaluation/run")
async def evaluation_run():
    return run_evaluation()