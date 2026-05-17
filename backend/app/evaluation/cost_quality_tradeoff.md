# Cost vs Quality Tradeoff

## Goal

The system is designed to balance output quality, latency, and cost while maintaining reliability.

## Strategy

The AI App Compiler avoids using a single large prompt for the entire task. Instead, it separates generation into deterministic stages:

1. Intent extraction
2. Architecture planning
3. Schema generation
4. Validation
5. Repair
6. Runtime mapping
7. Code artifact generation

This reduces cost because expensive generation is isolated from deterministic validation and repair.

## Why Not Single Prompt?

A single-prompt approach is cheaper initially but unreliable:

- invalid JSON risk
- missing fields
- inconsistent UI/API/DB layers
- hallucinated entities
- weak repairability
- poor debugging

The multi-stage approach costs slightly more engineering effort but improves reliability.

## Cost Controls

The system reduces cost using:

- deterministic schema generation where possible
- reusable validation rules
- targeted repair instead of full regeneration
- runtime simulation without deploying generated apps
- mock/deterministic mode for testing
- optional LLM provider only for generation stages

## Quality Controls

Quality is improved through:

- strict output contract
- typed database fields
- API request/response schemas
- UI to API binding validation
- auth role consistency checks
- business logic validation
- runtime executability checks
- evaluation on real and edge-case prompts

## Latency Tradeoff

The pipeline adds multiple stages, but most stages are deterministic and fast.

The evaluation runner tracks:

- latency per request
- retries per request
- repair count
- failure types

## Repair Tradeoff

Instead of blindly retrying the full generation, the system repairs only the failing part.

Example:

```txt
If subscriptions are mentioned in intent but missing in DB schema,
the repair engine adds only the subscriptions table.