Define a new skill blueprint for containerizing applications in Phase IV.

Skill name: containerize-app

Description: This skill generates and builds Dockerfiles for frontend/Next.js and backend/FastAPI+Cohere, using Gordon (Docker AI) if available, otherwise standard best practices.

Inputs: App type (frontend or backend), spec reference (@specs/features/local-kubernetes-deployment.md)
Process:
- If Gordon available: Generate prompt like 'docker ai "Generate a multi-stage Dockerfile for a Next.js app with Tailwind and Cohere-integrated ChatKit"'
- Fallback: Use Claude Code to output Dockerfile content (multi-stage, non-root, minimal)
- Cohere role: Use Cohere to review/optimize Dockerfile (e.g., "Analyze this Dockerfile for security: {code}")
- Output: Dockerfile path, build command, test instructions (docker run with COHERE_API_KEY env)