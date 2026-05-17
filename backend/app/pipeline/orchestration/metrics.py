import time


def generate_metrics(start_time,
                     validation,
                     repaired):

    latency = time.time() - start_time

    metrics = {

        "success": validation["valid"],

        "latency_seconds": round(latency, 3),

        "repair_applied": repaired,

        "error_count": len(
            validation["errors"]
        )
    }

    return metrics