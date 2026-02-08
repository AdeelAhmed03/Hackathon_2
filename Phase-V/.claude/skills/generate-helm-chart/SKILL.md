Define a new skill blueprint for generating Helm charts in Phase IV.

Skill name: generate-helm-chart

Description: This skill creates Helm charts for Todo components (frontend, backend, postgres), using kubectl-ai for initial manifests.

Inputs: Component (e.g., backend), values overrides (replicas=2, env=COHERE_API_KEY as secret)
Process:
- Use kubectl-ai: Prompt like 'kubectl-ai "generate helm chart for fastapi backend with Cohere env secret and 2 replicas"'
- Refine with Cohere: "Review this Helm YAML for best practices in Phase IV: {yaml}. Suggest improvements."
- Structure: /charts/{component} with templates/deployment.yaml, service.yaml, ingress.yaml, values.yaml
- Handle Cohere secrets: Use Kubernetes Secrets for COHERE_API_KEY, BETTER_AUTH_SECRET