# Celesto Sandbox Agent with Evals and Containment

## Problem statement

**Who has the problem:** Security-conscious developers who need to test untrusted code safely without risking their local machine or production systems.

**Why it matters:** Running untrusted code, dependencies, or browsing untrusted content directly on a host machine exposes systems to destructive commands, secret leakage, and prompt injection attacks.

**What the agent does on a computer:** The agent provisions a Celesto sandbox, executes commands in complete isolation, applies safety hooks and network policy, audits all command attempts, and manages full lifecycle (create/ready/run/succeed/fail/delete). Every tool execution that runs code, touches files, or browses happens inside the Celesto sandbox, never on the host.

**What output proves it worked:** A containment report showing blocked malicious actions with evidence that the host remained untouched, plus an audited command log, reliability metrics from 20 fresh runs, and full lifecycle cleanup verification.

## How I used Celesto

This project leverages Celesto as the essential execution layer for all untrusted operations. The following differentiating capabilities are used:

- **Snapshots** - Checkpoint state before risky operations (like step 7 in our 10-step workflow). Enables rollback to a known good state if failures occur. Without snapshots, recovery would require full environment rebuild.
- **Safety hooks** - Inspect and block dangerous commands before they execute in the guest VM. Prevents prompt injection exfiltration and destructive commands. Without safety hooks, we would only rely on prompts which cannot guarantee enforcement.

The sandbox boundary is non-negotiable - all code execution, file operations, and network-bound operations run inside isolated Celesto microVMs.

## Architecture

The system consists of:
1. **Trusted Control Plane** (Docker Compose): API service (FastAPI) and Postgres ledger
2. **Execution Zone**: Celesto sandboxes created via SDK/CLI - isolated microVMs where all agent work happens
3. **Audit Trail**: All command attempts logged to `logs/commands.jsonl` with `execution_target: celesto_sandbox`
4. **Reports**: Structured JSON/Markdown artifacts proving eval results, containment, and failure handling

Data flow: Operator ? API ? Celesto SDK/CLI ? Isolated Sandbox ? Audit Log ? Reports

## Eval report

We ran **20 fresh sandboxes** end-to-end. Results are in [reports/reliability.json](reports/reliability.json):

- **Run count:** 20 (all fresh)
- **Success rate:** 90% (18/20)
- **Median wall-clock time:** ~14.5s
- **P90 wall-clock time:** ~19.0s  
- **Median boot-to-ready time:** ~3.0s
- **Total cost:** ~$0.28 USD

See [reports/postmortem.md](reports/postmortem.md) for failure analysis.

## Containment test

**Attack:** Prompt injection exfiltration attempt  
**Result:** Blocked by safety hooks and network policy  
**Host untouched:** Confirmed  
**Evidence:** [reports/evidence/containment.log](reports/evidence/containment.log)

The malicious command attempting to exfiltrate environment variables was intercepted before execution in the guest, demonstrating effective containment.

## State and failure design

**Scenario:** Step 7 of 10 fails mid-task  
**Policy:** Rollback using snapshots  
**Rationale:** Taking a snapshot before the risky step allows restoration to a known good state quickly without rebuilding the entire environment from scratch. This balances reliability and cost.  
**Trace:** [reports/failure_trace.jsonl](reports/failure_trace.jsonl) shows `policy_applied` event with policy `rollback`.

All sandboxes are cleaned up on success, failure, and interrupt. See [reports/lifecycle.json](reports/lifecycle.json).

## Setup

**Prerequisites:** Docker and Docker Compose

1. Clone this repository
2. Copy environment template: `cp .env.example .env` (or just use .env.example)
3. Start the control plane: `docker-compose up`
4. Wait for services to be healthy (within 5 minutes)
5. Verify health: `curl http://localhost:8080/health` returns `{"status":"ok"}`
6. Check runs: `curl http://localhost:8080/api/runs` includes `sbx-seeddemo1`

All environment variables are documented in [.env.example](.env.example) with placeholders. No live secrets are committed.

## Demo

Demo video: [demo/walkthrough.mp4](demo/walkthrough.mp4) (3 minutes or less, shows agent working in sandbox with live viewer)

## Concurrency

5 concurrent jobs tested across uniquely named sandboxes. See [reports/concurrency.json](reports/concurrency.json).