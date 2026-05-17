import time
from typing import Dict, Any, List

from app.pipeline.intent.extractor import extract_intent
from app.pipeline.architecture.planner import generate_architecture
from app.pipeline.schema.generator import generate_schema
from app.pipeline.validation.validator import validate_schema
from app.pipeline.repair.repair_engine import repair_schema
from app.pipeline.runtime.runtime_engine import generate_runtime
from app.pipeline.codegen.generator import generate_code_artifacts
from app.pipeline.codegen.zipper import create_project_zip


def detect_ambiguity(prompt: str) -> Dict[str, Any]:
    text = prompt.lower().strip()

    vague_terms = [
        "something",
        "anything",
        "app for teams",
        "platform for users",
        "system for business",
        "tool for work",
    ]

    clarification_needed = any(term in text for term in vague_terms) or len(text.split()) < 5

    clarifying_questions: List[str] = []
    assumptions: List[str] = []

    if clarification_needed:
        clarifying_questions = [
            "What type of users or roles should the application support?",
            "What core entities should the system manage?",
            "Should the application include authentication and role-based access?",
            "What are the most important workflows the app should support?"
        ]
        assumptions = [
            "Defaulting to a generic team collaboration application.",
            "Using admin and member as default roles.",
            "Including authentication by default.",
            "Generating a minimal dashboard, settings page, and resource management flow."
        ]
    else:
        assumptions = [
            "Authentication is included when login, users, roles, admin, or premium features are mentioned.",
            "Admin role receives management permissions by default.",
            "Database tables are inferred from detected entities.",
            "API endpoints are generated from detected entities and workflows."
        ]

    return {
        "clarification_needed": clarification_needed,
        "clarifying_questions": clarifying_questions,
        "assumptions": assumptions
    }


async def generate(request):
    start_time = time.time()

    prompt = request.prompt

    ambiguity = detect_ambiguity(prompt)

    intent = extract_intent(prompt)
    architecture = generate_architecture(intent)
    schema = generate_schema(intent, architecture)

    validation = validate_schema(intent, architecture, schema)

    repaired_schema = schema
    repair_log = []

    if not validation.get("valid", False):
        repaired_schema, repair_log = repair_schema(intent, architecture, schema, validation)
        validation = validate_schema(intent, architecture, repaired_schema)
    else:
        repaired_schema, repair_log = repair_schema(intent, architecture, schema, validation)

    runtime = generate_runtime(repaired_schema)
    generated_files = generate_code_artifacts(runtime)
    project_zip = create_project_zip()

    latency = round(time.time() - start_time, 2)

    metrics = {
        "success": validation.get("valid", False),
        "latency_seconds": latency,
        "repair_applied": len(repair_log) > 0,
        "error_count": len(validation.get("errors", [])),
        "retry_count": 0,
        "failure_types": validation.get("failure_types", [])
    }

    return {
        "input_prompt": prompt,
        "intent": intent,
        "architecture": architecture,
        "schema": schema,
        "validation": validation,
        "repaired_schema": repaired_schema,
        "repair_log": repair_log,
        "runtime": runtime,
        "generated_files": generated_files,
        "metrics": metrics,
        "project_zip": project_zip,
        "clarification_needed": ambiguity["clarification_needed"],
        "clarifying_questions": ambiguity["clarifying_questions"],
        "assumptions": ambiguity["assumptions"]
    }