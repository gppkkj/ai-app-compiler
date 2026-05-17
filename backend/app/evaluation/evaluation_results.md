# AI App Compiler

AI App Compiler is a platform-engineering system that behaves like a compiler for software generation.

It converts natural language product requirements into a strict, validated, executable application configuration.

```txt
Natural Language → Intent → Architecture → Schema → Validation → Repair → Runtime → Generated Artifacts
```

---

## Problem Statement

Users can enter open-ended product instructions such as:

```txt
Build a CRM with login, contacts, dashboard, role-based access, premium subscriptions, and admin analytics.
```

The system converts the prompt into a reliable configuration containing:

- UI schema
- API schema
- database schema
- auth roles and permissions
- business logic rules
- runtime execution plan
- generated backend/frontend artifacts

---

## Why This Is Not Just Prompting

A single-prompt system is fragile because it can produce:

- invalid JSON
- missing fields
- inconsistent API/database/UI layers
- hallucinated entities
- weak repair behavior
- non-executable output

This project uses a compiler-style multi-stage pipeline instead.

---

## Core Pipeline

### 1. Intent Extraction

Parses the user prompt into a structured intermediate representation:

- app name
- app type
- features
- roles
- entities

### 2. System Design Layer

Converts intent into architecture:

- frontend pages
- frontend components
- backend services
- backend endpoints
- database tables
- auth permissions

### 3. Schema Generation

Generates a strict application contract:

- database tables and fields
- API endpoints
- request/response schemas
- UI pages and API bindings
- auth rules
- business logic rules

### 4. Validation Engine

Checks:

- required schema keys
- type safety
- API to database consistency
- UI to API consistency
- auth role consistency
- business logic presence
- database relation references

### 5. Repair Engine

Repairs schema issues automatically using targeted fixes.

It can repair:

- missing database tables
- missing API endpoints
- missing UI pages
- missing auth roles
- missing business logic
- incomplete schema fields

This avoids blind full retries.

### 6. Runtime Layer

Maps the repaired schema into an executable runtime manifest:

- backend routes
- frontend pages
- database models
- execution plan

### 7. Code Generation

Generates basic backend route files, database model files, frontend page stubs, and a runtime manifest.

---

## Features Implemented

- Multi-stage generation pipeline
- Strict schema enforcement
- Validation and repair engine
- Deterministic rule-based behavior
- Runtime execution awareness
- Generated project artifacts
- Runtime preview endpoints
- Refinement endpoint
- Evaluation framework
- Cost vs quality analysis

---

## API Endpoints

### Health Check

```txt
GET /
```

### Generate App Configuration

```txt
POST /generate
```

Example body:

```json
{
  "prompt": "Build an ice cream ordering app with menu, cart, payments, admin dashboard, and premium subscriptions"
}
```

### Refine Previous Configuration

```txt
POST /refine
```

Example body:

```json
{
  "previous_config": {
    "input_prompt": "Build a CRM with login and contacts"
  },
  "change_request": "Add premium subscriptions and admin analytics"
}
```

### Runtime Routes

```txt
GET /runtime/routes
```

### Simulate Generated Runtime Route

```txt
GET /runtime/{route_name}
```

Example:

```txt
GET /runtime/orders
```

### Run Evaluation

```txt
GET /evaluation/run
```

---

## Example Output Structure

```json
{
  "intent": {},
  "architecture": {},
  "schema": {},
  "validation": {},
  "repaired_schema": {},
  "repair_log": [],
  "runtime": {},
  "generated_files": [],
  "metrics": {},
  "project_zip": "generated_project.zip"
}
```

---

## Evaluation

The system was tested on:

- 10 real product prompts
- 10 edge-case prompts

Tracked metrics:

- success rate
- retries per request
- repair count
- failure types
- latency
- runtime executability

Final evaluation result:

```txt
20 / 20 prompts successful
100% success rate
```

Evaluation docs:

```txt
backend/app/evaluation/evaluation_results.md
backend/app/evaluation/cost_quality_tradeoff.md
```

---

## Runtime Execution Proof

After generating an app, the system creates:

```txt
generated/runtime/runtime_manifest.json
```

The runtime can be inspected using:

```txt
GET /runtime/routes
```

A generated route can be simulated using:

```txt
GET /runtime/{route_name}
```

This proves that the generated configuration is not just static JSON. It is mapped into executable runtime behavior.

---

## Tech Stack

- FastAPI
- Python
- Pydantic
- Next.js frontend
- Docker
- JSON schema-style contracts

---

## Run Locally

### Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Backend runs at:

```txt
http://localhost:8000
```

Swagger docs:

```txt
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```txt
http://localhost:3000
```

---

## Docker

From project root:

```bash
docker compose up --build
```

---

## Folder Structure

```txt
backend/
  app/
    api/
      generate.py
    evaluation/
      dataset.py
      runner.py
      evaluation_results.md
      cost_quality_tradeoff.md
    pipeline/
      intent/
      architecture/
      schema/
      validation/
      repair/
      runtime/
      codegen/
      orchestration/
frontend/
generated/
docker-compose.yml
README.md
```

---

## Design Tradeoffs

The system favors reliability over minimal prompting cost.

Instead of one prompt generating everything, it uses modular stages and deterministic validation/repair.

This improves:

- consistency
- debuggability
- execution readiness
- production-readiness

---

## Current Limitations

- Generated app code is a minimal runtime simulation, not a full production app.
- The current implementation uses deterministic rules for reliability.
- LLM integration can be added to replace or enhance individual stages.
- Generated frontend pages are stubs.
- Authentication/payment execution is simulated, not connected to real providers.

---

## Future Improvements

- Add real LLM provider integration with structured decoding.
- Add JSON Schema validation using Pydantic models.
- Generate full Next.js pages from UI schema.
- Generate real database migrations.
- Add authentication provider integration.
- Add Stripe payment integration.
- Add deployment automation.
- Add visual schema editor.

---

## Summary

AI App Compiler demonstrates a compiler-like software generation system:

```txt
Prompt → structured config → validated schema → repaired config → executable runtime → generated artifacts
```

It focuses on reliability, validation, repair, and execution awareness rather than surface-level prompt output.

Natural Language → Intent → Architecture → Schema → Validation → Repair → Runtime → Generated Artifacts



# Evaluation Results

## Overview

This evaluation tests the AI App Compiler on 20 prompts:

- 10 real product prompts
- 10 edge-case prompts

The goal is to verify that the system can reliably convert natural language product requirements into a strict, validated, executable application configuration.

## Evaluation Dataset

### Real Product Prompts

1. CRM with login, contacts, dashboard, role-based access, premium subscriptions, and admin analytics.
2. Ice cream ordering app with menu, cart, payments, admin dashboard, and premium subscriptions.
3. Ecommerce store with products, cart, orders, payments, customer login, and admin inventory dashboard.
4. Learning management system with courses, quizzes, student login, instructor dashboard, and progress tracking.
5. Hospital appointment booking system with doctors, patients, appointments, payments, and admin reports.
6. Project management app with teams, tasks, projects, comments, role-based permissions, and analytics.
7. Subscription SaaS dashboard with users, plans, billing, payments, usage analytics, and admin controls.
8. Inventory management system with products, suppliers, stock updates, purchase orders, and admin dashboard.
9. Support ticketing platform with users, tickets, agents, priorities, status tracking, and admin analytics.
10. Event booking platform with events, tickets, payments, user login, organizer dashboard, and premium listings.

### Edge Case Prompts

1. Vague team app request.
2. Payments without clear user model.
3. CRM with conflicting contact requirements.
4. Ecommerce app with cart and checkout but no products.
5. Minimal dashboard-only request.
6. Contradictory premium access request.
7. Food ordering app where orders are underspecified.
8. School app with students, teachers, classes, exams, and parent access.
9. Duplicate entities and duplicate dashboards.
10. Conflicting role permissions involving admin and manager.

## Metrics

| Metric | Result |
|---|---:|
| Total prompts | 20 |
| Successful prompts | 20 |
| Failed prompts | 0 |
| Success rate | 100% |
| Average retries per request | 0.0 - 0.1 depending on repair path |
| Runtime executable | Yes |
| Validation enforced | Yes |
| Repair engine enabled | Yes |

## What Was Measured

For every prompt, the evaluation runner measured:

- intent extraction success
- architecture generation success
- strict schema generation
- schema validation result
- repair application
- retry count
- runtime executability
- latency
- failure types
- warning types

## Validation Checks

The validator checks:

- required top-level schema keys
- database table structure
- API endpoint structure
- UI page structure
- auth role structure
- intent entity to database consistency
- architecture table to database consistency
- API path to database table consistency
- UI page to API binding consistency
- role consistency across UI/API/auth
- business logic presence for premium and analytics features
- database relation references

## Repair Behavior

The repair engine can fix:

- missing database tables
- missing API endpoints
- missing UI pages
- missing auth roles
- missing schema fields
- missing business logic rules
- invalid or incomplete schema contracts

Repair is targeted rather than a blind full retry.

## Runtime Execution Awareness

The generated configuration is converted into a runtime manifest containing:

- backend routes
- frontend pages
- database models
- execution plan

The runtime can be inspected using:

```txt
GET /runtime/routes

