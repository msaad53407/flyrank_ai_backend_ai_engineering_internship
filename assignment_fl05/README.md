# Week 4 · Assignment FL-05 — Agent Concepts and MCP Basics

This document provides a technical explainer essay on the fundamental differences between AI workflows and AI agents, details the Model Context Protocol (MCP) architecture, logs three non-chat tool executions, and outlines the upgrade path for the FL-04 pipeline into an autonomous agent.

---

## 📄 Technical Explainer Essay (750 Words)

### 1. Workflows vs. Agents: The Fundamental Boundary
In contemporary AI engineering, the word "agent" is frequently used as marketing shorthand for any LLM interaction. However, a strict architectural distinction exists between **workflows** and **agents**:

- **Workflows:** Workflows are deterministic, pre-sequenced pipelines where control flow is governed by hardcoded code paths, state machines, or graph edges (e.g. Step 1 -> Step 2 -> Step 3). The LLM is invoked at specific nodes to process text or transform schemas, but the sequence of steps, conditions, and error recovery routes are entirely static.
- **Agents:** Agents are autonomous control loops where the LLM itself dynamically determines control flow, tool selection, evaluation, and iteration. Operating within a **ReAct** (Reasoning + Acting) loop, an agent evaluates an environment state, formulates a plan, selects and invokes external tools, inspects the tool output, and autonomously decides whether to adjust its plan or finish execution.

### 2. The Model Context Protocol (MCP) Architecture
The Model Context Protocol (MCP) is an open standard developed by Anthropic that standardizes how AI applications connect to external tools, databases, and local resources. MCP eliminates custom one-off integrations by establishing a universal client-server protocol built on three core primitives:

1. **Tools:** Dynamic executable functions exposed by an MCP server that an AI client can invoke to perform side effects (e.g., executing a SQL query, writing a file, or running a terminal command).
2. **Resources:** Read-only data streams exposed by an MCP server that provide passive contextual grounding to the LLM (e.g., file system contents, database schema definitions, or live log files).
3. **Prompts:** Pre-configured template prompts managed by the server that standardize complex user workflows and domain interactions.

### 3. Classification of the FL-04 Pipeline
The FL-04 microservice generator built in Week 4 is a **Workflow Pipeline**, not an agent. It follows a fixed 4-step sequence (Gather -> Synthesize -> Code -> Audit). Each step passes structured Pydantic data to the next step along a static path. If step 3 encounters a syntax error, the pipeline cannot autonomously decide to loop back to step 2 with an error log to fix its own code—it requires human intervention.

---

## 🛠️ Evidence of 3 Non-Chat MCP Tool Executions

| Task | MCP Primitive | Tool / Command | Live Output | Why Chat Alone Cannot Do |
|---|---|---|---|---|
| **1. File Inspection** | `tool` | `list_dir` | Discovered Dockerfile, docker-compose.yml, main.py | Chat models have no access to local disk filesystems. |
| **2. Git Querying** | `tool` | `run_command(git status)` | `On branch main, up to date with origin/main` | Chat models cannot execute local git binary commands. |
| **3. Live HTTP Check** | `resource` | `urllib.request('http://localhost:8000/health')` | `{"status":"ok","repository":"PostgresTaskRepository"}` | Chat models cannot send HTTP requests to localhost ports. |

*See [`mcp_tool_logs.json`](file:///f:/Programming/flyrank_ai_internship/assignment_fl05/mcp_tool_logs.json) for raw machine logs.*

---

## 🚀 Upgrade Path: Turning FL-04 into an Autonomous Agent

To upgrade the static FL-04 workflow into a true **Autonomous Software Engineering Agent**:
1. **Dynamic ReAct Loop:** Implement an autonomous evaluation loop where the LLM receives compiler error tracebacks from `pytest` and autonomously decides whether to rerun `git status`, edit specific lines, or adjust its database schema.
2. **MCP Tool Integration:** Equip the agent with MCP tool access (`read_file`, `write_to_file`, `run_command`, `git_commit`) so it can autonomously create files, run test suites, inspect failure logs, and commit clean fixes without human intervention.
