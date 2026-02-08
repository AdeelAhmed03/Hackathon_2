Define a new skill blueprint for deploying to Minikube in Phase IV, optimized for comprehensive, secure, and scalable local orchestration.

Skill name: deploy-to-minikube

Description: This skill manages the full Minikube cluster setup, Helm chart installation/upgrades, secret/config injection, and initial scaling for the Todo Chatbot stack (frontend, backend with Cohere-adapted agents, postgres). It uses AI tools for automation while ensuring spec compliance.

Inputs: Helm chart paths (e.g., /charts/todo-app), values overrides (YAML dict for replicas, resources, env secrets), minikube profile (default: todo-cluster), dry_run (bool, default: false)
Process:
- Setup: minikube start --profile {profile} --driver=docker --addons=ingress,metrics-server; verify with minikube status
- Secrets/Config: Create k8s Secrets for COHERE_API_KEY, BETTER_AUTH_SECRET; ConfigMaps for non-sensitive (e.g., DATABASE_URL)
- Deploy: helm dependency build {chart}; helm install/upgrade todo-app {chart} --values {overrides} --dry-run if dry_run; handle namespaces
- AI Assistance: Use kubectl-ai "deploy {component} with 2 replicas and liveness probes"; kagent "optimize resource allocation for backend pods"
- Cohere Role: Post-deploy, use Cohere to review kubectl get all output: "Analyze deployment status: {output}. Suggest optimizations like HPA: Output JSON {'status': 'healthy/pending/error', 'recommendations': list}."
- Observability: Add probes (readiness: HTTP /healthz, liveness: TCP port); enable metrics
- Error Handling: On failure, capture logs and return for devops-debug-agent; rollback with helm uninstall
- Scalability: Apply initial scaling (e.g., kubectl scale deployment/backend --replicas=2); suggest autoscaling YAML

Generate skill.md in /skills/deploy-to-minikube.md with: sequential steps (bash/Python pseudocode), example Cohere prompts, AI tool command templates, security checklists (e.g., no hard-coded secrets), and test cases (e.g., verify ingress URL responds).