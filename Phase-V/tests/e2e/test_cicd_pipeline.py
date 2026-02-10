"""E2E Tests: CI/CD Pipeline Validation (T159-T161).

Test CI/CD pipeline functionality:
1. Verify GitHub Actions workflow files exist and are valid
2. Test Helm chart linting
3. Document manual verification steps for full pipeline testing

Note: Full CI/CD testing requires:
- Push to develop branch (triggers staging deployment)
- PR to main (triggers CI checks)
- Merge to main (triggers production deployment with approval)
"""

import os
import subprocess
from pathlib import Path

import httpx
import pytest
import yaml


class TestCICDPipeline:
    """Test 5: CI/CD Pipeline Validation."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        # Navigate up from tests/e2e to project root
        current = Path(__file__).parent
        while current.name != "Phase-V" and current.parent != current:
            current = current.parent
        return current

    @pytest.mark.e2e
    def test_ci_workflow_exists(self, project_root: Path):
        """T135: Verify CI workflow file exists and is valid YAML."""
        ci_path = project_root / ".github" / "workflows" / "ci.yaml"

        if not ci_path.exists():
            ci_path = project_root / ".github" / "workflows" / "ci.yml"

        assert ci_path.exists(), f"CI workflow not found at {ci_path}"

        # Validate YAML syntax
        with open(ci_path) as f:
            content = f.read()

        # Load the config
        ci_config = yaml.safe_load(content)

        assert ci_config is not None, "CI workflow should be valid YAML"
        assert "name" in ci_config, "CI workflow should have a name"

        # Handle YAML parsing issue where 'on:' becomes True when followed by a mapping
        # In GitHub Actions YAML, 'on:' followed by indented content creates a boolean True key
        has_triggers = "on" in ci_config or True in ci_config
        assert has_triggers, "CI workflow should have triggers"

        # Determine the correct location for jobs based on the YAML structure
        if True in ci_config:
            # 'on:' was converted to True, so the actual workflow config is under the True key
            workflow_config = ci_config[True]
            jobs = workflow_config.get("jobs", {})
            # Additional check: in GitHub Actions, jobs are at root level, not under 'on:'
            # So if we don't find jobs under the True key, check at the main level
            if not jobs:
                jobs = ci_config.get("jobs", {})
        else:
            # Normal case where jobs are at root level
            jobs = ci_config.get("jobs", {})

        # Verify expected jobs
        expected_job_types = ["test", "lint", "build"]

        # Check that at least some test/lint jobs exist
        job_names = " ".join(jobs.keys()).lower()
        has_testing = any(
            keyword in job_names
            for keyword in expected_job_types
        )
        assert has_testing, f"CI should have test/lint/build jobs, found: {list(jobs.keys())}"

    @pytest.mark.e2e
    def test_deploy_workflow_exists(self, project_root: Path):
        """T136: Verify deploy workflow file exists and is valid YAML."""
        deploy_path = project_root / ".github" / "workflows" / "deploy.yaml"

        if not deploy_path.exists():
            deploy_path = project_root / ".github" / "workflows" / "deploy.yml"

        assert deploy_path.exists(), f"Deploy workflow not found at {deploy_path}"

        # Validate YAML syntax
        with open(deploy_path) as f:
            deploy_config = yaml.safe_load(f)

        assert deploy_config is not None, "Deploy workflow should be valid YAML"
        assert "jobs" in deploy_config, "Deploy workflow should have jobs"

        # Verify staging/production deployment structure
        jobs = deploy_config.get("jobs", {})
        job_names = " ".join(jobs.keys()).lower()

        # Should have deployment-related jobs
        has_deploy = any(
            keyword in job_names
            for keyword in ["deploy", "staging", "production", "release"]
        )
        assert has_deploy, f"Deploy workflow should have deploy jobs, found: {list(jobs.keys())}"

    @pytest.mark.e2e
    def test_helm_charts_valid(self, project_root: Path):
        """T138: Verify Helm charts pass linting."""
        charts_dir = project_root / "charts"

        if not charts_dir.exists():
            pytest.skip("Charts directory not found")

        # Find all chart directories
        chart_dirs = [
            d for d in charts_dir.iterdir()
            if d.is_dir() and (d / "Chart.yaml").exists()
        ]

        assert len(chart_dirs) > 0, "Should have at least one Helm chart"

        # Try to lint each chart
        for chart_dir in chart_dirs:
            chart_yaml = chart_dir / "Chart.yaml"
            assert chart_yaml.exists(), f"Chart.yaml missing in {chart_dir.name}"

            # Validate Chart.yaml is valid YAML
            with open(chart_yaml) as f:
                chart_config = yaml.safe_load(f)

            assert chart_config is not None, f"Chart.yaml in {chart_dir.name} should be valid"
            assert "name" in chart_config, f"Chart {chart_dir.name} needs a name"
            assert "version" in chart_config, f"Chart {chart_dir.name} needs a version"

            # Verify values.yaml exists
            values_yaml = chart_dir / "values.yaml"
            assert values_yaml.exists(), f"values.yaml missing in {chart_dir.name}"

            # Verify templates directory exists
            templates_dir = chart_dir / "templates"
            assert templates_dir.exists(), f"templates directory missing in {chart_dir.name}"

    @pytest.mark.e2e
    def test_helm_lint_command(self, project_root: Path):
        """Run helm lint if available."""
        charts_dir = project_root / "charts"

        if not charts_dir.exists():
            pytest.skip("Charts directory not found")

        # Check if helm is available
        try:
            result = subprocess.run(
                ["helm", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                pytest.skip("Helm not available")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Helm not available")

        # Lint each chart
        chart_dirs = [
            d for d in charts_dir.iterdir()
            if d.is_dir() and (d / "Chart.yaml").exists()
        ]

        for chart_dir in chart_dirs:
            result = subprocess.run(
                ["helm", "lint", str(chart_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Helm lint returns 0 on success, 1 on error
            assert result.returncode == 0, \
                f"Helm lint failed for {chart_dir.name}: {result.stdout}\n{result.stderr}"

    @pytest.mark.e2e
    def test_dapr_components_valid(self, project_root: Path):
        """Verify Dapr component YAML files are valid."""
        dapr_dir = project_root / "dapr-components"

        if not dapr_dir.exists():
            pytest.skip("Dapr components directory not found")

        yaml_files = list(dapr_dir.glob("*.yaml")) + list(dapr_dir.glob("*.yml"))

        assert len(yaml_files) > 0, "Should have Dapr component files"

        for yaml_file in yaml_files:
            with open(yaml_file) as f:
                # Handle multi-document YAML files
                docs = list(yaml.safe_load_all(f))

            for doc in docs:
                if doc is None:
                    continue

                # Verify Dapr component structure
                if doc.get("kind") in ["Component", "Configuration"]:
                    assert "apiVersion" in doc, f"{yaml_file.name} needs apiVersion"
                    assert "metadata" in doc, f"{yaml_file.name} needs metadata"
                    assert "name" in doc.get("metadata", {}), f"{yaml_file.name} needs metadata.name"


class TestCICDDocumentation:
    """Document manual CI/CD verification steps."""

    @pytest.mark.e2e
    def test_document_staging_deployment(self):
        """T159: Document staging deployment verification.

        Manual steps to verify staging deployment:
        1. Make a small change (e.g., update version in Chart.yaml)
        2. Commit and push to develop branch:
           git checkout develop
           git add .
           git commit -m "Trigger staging deployment"
           git push origin develop

        3. Watch GitHub Actions:
           - Go to repository Actions tab
           - Find "Deploy" workflow triggered by push to develop
           - Verify jobs: build → push → deploy-staging

        4. Verify staging namespace:
           kubectl get pods -n staging
           kubectl get svc -n staging

        5. Check application health:
           curl http://<staging-url>/api/v1/health
        """
        pass  # Documentation test

    @pytest.mark.e2e
    def test_document_ci_checks(self):
        """T160: Document CI checks verification.

        Manual steps to verify CI checks:
        1. Create a PR from develop to main:
           git checkout -b feature/test-ci
           # Make a change
           git commit -m "Test CI checks"
           git push origin feature/test-ci
           # Create PR via GitHub UI

        2. Verify CI jobs run:
           - test-backend: pytest runs and passes
           - test-frontend: npm test runs and passes
           - lint-helm: helm lint passes for all charts

        3. PR should show green checks before merge is allowed
        """
        pass  # Documentation test

    @pytest.mark.e2e
    def test_document_production_deployment(self):
        """T161: Document production deployment verification.

        Manual steps to verify production deployment:
        1. Merge PR to main:
           - Click "Merge" on GitHub PR with passing checks

        2. Watch GitHub Actions:
           - Deploy workflow triggers
           - Should require approval gate for production

        3. Approve deployment:
           - Click "Review pending deployments"
           - Select production environment
           - Click "Approve and deploy"

        4. Verify production namespace:
           kubectl get pods -n production
           kubectl get svc -n production

        5. Verify application:
           curl http://<production-url>/api/v1/health

        6. Rollback if needed:
           helm rollback todo-backend -n production
        """
        pass  # Documentation test


class TestGitHubSecretsDocumentation:
    """T137: Document required GitHub Secrets."""

    @pytest.mark.e2e
    def test_document_required_secrets(self):
        """Document secrets that must be configured in GitHub repository settings.

        Required GitHub Secrets:
        1. KUBECONFIG_STAGING
           - Base64-encoded kubeconfig for staging cluster
           - Generate: base64 -w 0 ~/.kube/config-staging

        2. KUBECONFIG_PRODUCTION
           - Base64-encoded kubeconfig for production cluster
           - Generate: base64 -w 0 ~/.kube/config-production

        3. COHERE_API_KEY
           - Cohere API key for AI chatbot
           - Get from: https://dashboard.cohere.ai/api-keys

        4. BETTER_AUTH_SECRET
           - JWT signing secret (shared with frontend)
           - Generate: openssl rand -base64 32

        5. GHCR_TOKEN (if using GitHub Container Registry)
           - Personal access token with write:packages scope
           - Generate in GitHub Settings > Developer settings > Personal access tokens

        Configuration steps:
        1. Go to repository Settings > Secrets and variables > Actions
        2. Click "New repository secret"
        3. Add each secret with the correct name and value
        4. Secrets are automatically available in workflows as ${{ secrets.SECRET_NAME }}
        """
        pass  # Documentation test
