# Week 2 · Assignment FL-02 — Prompting Fundamentals on Real Tasks v2

This assignment takes Target Task 1 from FL-01 (*API Specification Digest & Schema Generation*), applies 5 named prompting techniques across 6 iterations, and performs a cross-model benchmark between Claude 3.5 Sonnet and ChatGPT (GPT-4o).

---

## 🔄 Iteration Log (6 Versions)

### Version 0 (Naive Baseline)
- **Prompt:** `"Convert this user API spec into Pydantic models."`
- **Output:** Generic Python class with untyped fields.

### Version 1 (Role Assignment)
- **Technique:** Role & Persona.
- **Prompt:** `"Act as a Principal Python Backend Architect..."`
- **Observed Difference:** Switched from plain classes to Pydantic v2 `BaseModel` inheritance.

### Version 2 (Context & Motivation)
- **Technique:** Context & Intent.
- **Prompt:** `"Act as a Principal Python Backend Architect. We are building a high-throughput microservice..."`
- **Observed Difference:** Added field-level validation rules (`Field(..., min_length=3)`).

### Version 3 (Output Structure)
- **Technique:** Structured Format Enforcer.
- **Prompt:** `"Output ONLY valid Python code inside a markdown ```python block. Include docstrings and ConfigDict..."`
- **Observed Difference:** Removed conversational filler text; clean drop-in file output.

### Version 4 (Few-Shot Examples)
- **Technique:** Few-Shot Exemplars.
- **Prompt:** `"Here is an example input spec and the target Pydantic v2 class with Field(..., description='...')..."`
- **Observed Difference:** Model accurately adopted custom validator patterns and detailed Field descriptions.

### Version 5 (Step Decomposition / Chain of Thought)
- **Technique:** Step-by-Step Reasoning.
- **Prompt:** `"Step 1: Extract entity fields. Step 2: Map Python types. Step 3: Add validation. Step 4: Write Pydantic class."`
- **Observed Difference:** Captured nested model relationships and edge-case enum types without hallucination.

---

## 🥊 Cross-Model Benchmark (Claude 3.5 Sonnet vs. ChatGPT GPT-4o)

| Metric | Claude 3.5 Sonnet | ChatGPT (GPT-4o) |
|---|---|---|
| **Tone** | Extremely concise, pure technical implementation | Friendly conversational intro text before code |
| **Accuracy** | 100% compliant with Pydantic v2 syntax (`ConfigDict`) | Mixed Pydantic v1 (`class Config`) & v2 syntax |
| **Structure** | Modular, PEP-8 compliant import organization | Single block without docstring headers |
| **Failure Points**| Occasional over-engineering of custom validators | Requires explicit instruction to omit explanatory prose |

---

## 🧩 Standalone Reusable Prompt Template

```markdown
Role: Principal Python Backend Architect
Task: Convert the raw API spec below into production Pydantic v2 models.

Execution Steps:
1. Identify all core entities, data types, and required vs. optional fields.
2. Define Pydantic models inheriting from pydantic.BaseModel using Python 3.13 type hints.
3. Apply pydantic.Field with min_length, max_length, gt, lt, and regex validation.
4. Include docstrings and Field descriptions.

Input Spec:
[INSERT RAW API SPEC HERE]
```
