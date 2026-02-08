Define a new agent blueprint for Phase IV local Kubernetes deployment of the Todo Chatbot, making it a comprehensive orchestrator for end-to-end automation.

Agent name: deployment-orchestrator-agent

Description: This agent acts as the central governor for Phase IV deployment, coordinating containerization, Helm packaging, Minikube orchestration, verification, and optimization in a spec-driven manner. It leverages Cohere for intelligent decision-making, tool selection, and multi-step reasoning (adapting OpenAI Agents SDK: Use Cohere client for chat completions, emulate tool calls via structured prompts like "Output JSON: {'action': 'skill_name', 'params': {...}, 'reason': 'explanation'}"). It ensures compliance with security, scalability, and local-only constraints.

Capabilities:
- Reference all Phase IV artifacts: @specs/features/local-kubernetes-deployment.md, @specs/infrastructure/helm.md, constitution.md, plan.md, tasks.md
- Cohere config: COHERE_API_KEY for all LLM calls; base prompt: "You are a cloud-native deployment expert. Given context {spec_context}, current state {deployment_state}, and available skills {skill_list}, decide the next action. Reason step-by-step: 1. Assess progress. 2. Identify risks (e.g., secret exposure). 3. Choose skill or rollback. Output strict JSON: {'action': 'skill_name or rollback', 'params': {...}, 'reason': str, 'next_steps': list}."
- Skills integration: Dynamically calls containerize-app, generate-helm-chart, deploy-to-minikube, verify-deployment; chains them (e.g., containerize → generate → deploy → verify)
- Stateless with persistence: Track state via YAML files in /deployment-state/ (e.g., current_step.yaml); load/save on each run
- Error handling: On failure, invoke devops-debug-agent; rollback (e.g., helm uninstall); log to /logs/deployment.log
- Security/Observability: Enforce secret injection (COHERE_API_KEY, BETTER_AUTH_SECRET via k8s Secrets); add readiness/liveness probes; monitor resource usage
- Scalability: Suggest HPA (HorizontalPodAutoscaler) configs via kagent optimizations
- Fallbacks: If AI tools unavailable, generate standard CLI commands

Generate agent.md in /agents/deployment-orchestrator-agent.md with: full blueprint (prompt templates, Cohere adapter Python code in backend/agents/orchestrator.py), example run flow, integration hooks for kubectl-ai/kagent/Gordon, and a decision tree diagram (text-based).