from typing import Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.pipeline.orchestration.generate import generate as run_generation

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


class RefineRequest(BaseModel):
    previous_config: Dict[str, Any]
    change_request: str


@router.post("/generate")
async def generate(request: PromptRequest):
    return await run_generation(request)


@router.post("/refine")
async def refine(request: RefineRequest):
    previous_prompt = request.previous_config.get("input_prompt", "")
    combined_prompt = previous_prompt + "\nUpdate request: " + request.change_request

    refined_request = PromptRequest(prompt=combined_prompt)

    result = await run_generation(refined_request)

    result["refinement"] = {
        "applied": True,
        "change_request": request.change_request,
        "strategy": "Regenerated targeted configuration from previous prompt plus change request"
    }

    return result