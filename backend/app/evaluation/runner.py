import time
from typing import Dict, Any, List

from app.evaluation.dataset import EVALUATION_PROMPTS
from app.pipeline.intent.extractor import extract_intent
from app.pipeline.architecture.planner import generate_architecture
from app.pipeline.schema.generator import generate_schema
from app.pipeline.validation.validator import validate_schema
from app.pipeline.repair.repair_engine import repair_schema
from app.pipeline.runtime.runtime_engine import generate_runtime


def _runtime_is_executable(runtime: Dict[str, Any]) -> bool:
    if runtime.get("runtime_status") != "ready":
        return False

    for route in runtime.get("backend_routes", []):
        if not route.get("executable"):
            return False

    for page in runtime.get("frontend_pages", []):
        if not page.get("executable"):
            return False

    for model in runtime.get("database_models", []):
        if not model.get("executable"):
            return False

    return True


def _run_single(prompt_item: Dict[str, str]) -> Dict[str, Any]:
    start_time = time.time()

    retry_count = 0
    repair_applied = False
    repair_log: List[Dict[str, str]] = []

    intent = extract_intent(prompt_item["prompt"])
    architecture = generate_architecture(intent)
    schema = generate_schema(intent, architecture)

    validation = validate_schema(intent, architecture, schema)

    repaired_schema = schema

    if not validation["valid"]:
        repair_applied = True
        retry_count += 1

        repaired_schema, repair_log = repair_schema(
            intent,
            architecture,
            schema,
            validation
        )

        validation = validate_schema(
            intent,
            architecture,
            repaired_schema
        )

    runtime = generate_runtime(repaired_schema)

    latency = round(time.time() - start_time, 4)

    executable = _runtime_is_executable(runtime)

    success = validation["valid"] and executable

    return {
        "id": prompt_item["id"],
        "type": prompt_item["type"],
        "prompt": prompt_item["prompt"],
        "success": success,
        "validation_valid": validation["valid"],
        "runtime_executable": executable,
        "repair_applied": repair_applied,
        "retry_count": retry_count,
        "latency_seconds": latency,
        "error_count": len(validation.get("errors", [])),
        "failure_types": validation.get("failure_types", []),
        "warnings": validation.get("warnings", []),
        "repair_log": repair_log,
        "app_type": intent.get("app_type"),
        "entity_count": len(intent.get("entities", [])),
        "api_count": len(repaired_schema.get("api", [])),
        "db_table_count": len(repaired_schema.get("database", [])),
        "ui_page_count": len(repaired_schema.get("ui", []))
    }


def run_evaluation() -> Dict[str, Any]:
    results = []

    for prompt_item in EVALUATION_PROMPTS:
        result = _run_single(prompt_item)
        results.append(result)

    total = len(results)
    successful = len([item for item in results if item["success"]])
    failed = total - successful

    average_latency = round(
        sum(item["latency_seconds"] for item in results) / total,
        4
    )

    average_retries = round(
        sum(item["retry_count"] for item in results) / total,
        2
    )

    repair_count = len([item for item in results if item["repair_applied"]])

    failure_type_counts: Dict[str, int] = {}

    for item in results:
        for failure_type in item.get("failure_types", []):
            failure_type_counts[failure_type] = failure_type_counts.get(failure_type, 0) + 1

    return {
        "summary": {
            "total_prompts": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total, 2),
            "average_latency_seconds": average_latency,
            "average_retries_per_request": average_retries,
            "repair_applied_count": repair_count,
            "failure_type_counts": failure_type_counts
        },
        "results": results
    }