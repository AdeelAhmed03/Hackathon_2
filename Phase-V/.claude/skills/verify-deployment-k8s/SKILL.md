Define a new skill blueprint for verifying and optimizing deployment in Phase IV, making it comprehensive for end-to-end validation and performance tuning.

Skill name: verify-deployment

Description: This skill performs thorough verification of the deployed Todo Chatbot in Minikube, including health checks, functional tests (e.g., Cohere-powered chatbot interactions), security audits, and optimizations. It chains AI tools for deep analysis and ensures the stack meets Phase IV acceptance criteria.

Inputs: Ingress URL or service name, test_cases (list of NL commands for chatbot, e.g., "Add task: buy groceries"), timeout (default: 300s)
Process:
- Health Checks: kubectl get pods -w until ready; check services/ingress; use kagent "analyze cluster health" for resource metrics
- Functional Tests: Port-forward (kubectl port-forward svc/frontend 3000:3000); curl /api/{user_id}/chat with JWT and test messages; verify Cohere responses (e.g., tool calls succeed, DB persists)
- Cohere-Specific: Send test query via chatbot; confirm no OpenAI usage (grep logs for 'cohere'); emulate tool calls to validate adapter
- Security Audit: Scan for exposed ports/secrets (kubectl describe secrets); use Cohere "Review YAML for vulnerabilities: {yaml}. Suggest fixes."
- Optimization: kagent "optimize resource allocation"; apply suggestions (e.g., update requests/limits); test scalability (simulate load with kubectl run busybox --image=busybox -- /bin/sh -c "while true; do wget -q -O- http://backend:8000; done")
- Error Handling: If tests fail, invoke devops-debug-agent with logs; generate report with pass/fail per criteria
- Output: Verification report (JSON: {'overall_status': 'pass/fail', 'details': {'health': str, 'functional': list, 'security': str, 'optimizations_applied': list}})

Generate skill.md in /skills/verify-deployment.md with: detailed test suite (including Cohere integration checks), Cohere prompt templates for audits, AI tool examples (kubectl-ai "check pod readiness"), fallback manual commands, and a verification checklist aligned with spec.md acceptance criteria.