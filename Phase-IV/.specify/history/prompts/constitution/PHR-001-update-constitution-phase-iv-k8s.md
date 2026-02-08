---
id: PHR-001
title: update-constitution-phase-iv-k8s
stage: constitution
date: 2026-02-06
surface: claude-code-cli
model: claude-sonnet-4-5
feature: phase-iv-k8s-deployment
branch: master
user: adeel-ahmed
command: /sp.constitution
labels: [constitution, phase-iv, kubernetes, helm, devops, ai-assisted]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    action: updated
tests:
  - N/A (documentation update)
---

## Prompt

Update the project constitution.md file for Phase IV based on the following overview and constraints, building on Phases I–III:

This is Phase IV of the Todo application: Deploy the full-stack AI-powered Todo Chatbot (Phase III) to a local Kubernetes cluster using Minikube, with containerization, Helm packaging, and AI-assisted DevOps tools.

Key principles and constraints:
- Monorepo continues: /frontend, /backend, /specs, /charts (new – for Helm charts), docker-compose.yml (keep for local non-k8s), minikube setup scripts
- Containerization: Produce Dockerfiles for frontend (Next.js) and backend (FastAPI + Agents SDK + MCP server); use Docker AI Agent (Gordon) where available, otherwise standard Docker best practices
- Use Gordon (Docker AI) for intelligent Dockerfile generation, image build, compose → kubernetes conversion hints if possible
- Kubernetes: Minikube (single-node local cluster), kubectl, Helm 3+
- Helm charts: Create production-grade charts for frontend, backend, postgres (optional local Neon-like via bitnami/postgresql or postgres chart), with values.yaml overrides
- AI DevOps tools: Use kubectl-ai and kagent for generating manifests, debugging, scaling, health checks, optimization
- LLM change: Replace all OpenAI API usage with Cohere API (via COHERE_API_KEY env var). Keep OpenAI Agents SDK structure / tool-calling pattern, but configure it to use Cohere as the model backend (via compatible client wrapper or direct Cohere chat completions endpoint). Update agent/tool calling logic accordingly.
- No cloud resources except local Minikube; no real Neon DB in Phase IV (use local PostgreSQL via Helm or Docker)
- Security: Keep JWT auth; expose services via Minikube ingress or LoadBalancer
- Deliverables: /charts/todo-frontend, /charts/todo-backend, /charts/postgres (if used), deployment scripts, README updates with Minikube + Helm + kubectl-ai/kagent usage, Gordon commands (or fallback), troubleshooting section

Include sections updates for: overview (full evolution to cloud-native local deployment), technology stack additions (Minikube, Helm, Docker AI/Gordon, kubectl-ai, kagent, Cohere), architecture notes (pods, services, ingress, persistent volumes), AI-assisted workflow emphasis, testing approach (port-forward, kubectl describe/logs, kagent health checks), deliverables.

## Response snapshot

Updated constitution.md from version 3.0.0 to 4.0.0 with the following major changes:

**Modified Principles:**
- V. Persistent Storage → Local PostgreSQL via Helm (instead of Neon)
- VII. Monorepo Structure → Added /charts directory for Helm charts
- IX. Backend Technology → Updated for local PostgreSQL + preserved Cohere
- X. Development Workflow → Added AI-Assisted DevOps (Gordon, kubectl-ai, kagent)
- XIV. Environment Variables → Updated for K8s Secrets management

**New Sections Added:**
- XV. Containerization Standards (Docker and Gordon)
- XVI. Kubernetes Architecture (Minikube + kubectl)
- XVII. Helm Charts Architecture
- XVIII. AI-Assisted DevOps Workflow
- XIX. Local Development vs Kubernetes Deployment
- "Differences from Phase III" migration guide
- Updated Phase Evolution Summary table (4 phases)

**Key Architectural Decisions:**
- Database: Neon → Local PostgreSQL via Helm
- Deployment: Docker Compose → Kubernetes/Minikube + Helm
- Infrastructure: Added Gordon, kubectl-ai, kagent tooling
- Cohere: Preserved as AI provider (NOT OpenAI)

## Outcome

- ✅ Impact: Constitution updated to version 4.0.0 with comprehensive Phase IV guidance
- 🧪 Tests: N/A (documentation update)
- 📁 Files: .specify/memory/constitution.md (updated)
- 🔁 Next prompts: Update CLAUDE.md, backend/CLAUDE.md, README.md for Phase IV context
- 🧠 Reflection: Major version bump justified by new deployment architecture (K8s), infrastructure tools (Gordon, kubectl-ai, kagent), and database change (Neon → local PostgreSQL)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify Helm chart templates align with constitution structure
