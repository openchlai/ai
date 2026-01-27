# Open Source Compliance Checklist & Evidence

This document tracks the compliance status of the OpenCHS AI project against the Open Source requirements and milestones.

| Quarter | Requirement / Task | Description of What Must Be Done | Evidence to Provide | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | **Define Open Source licensing strategy** | Decide whether the project uses permissive or copyleft licensing. | [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md) (See "Open Source Contractual Requirements") | ✅ |
| **Q1** | **Apply OSI-approved license** | Apply an OSI-approved license to all public repositories. | [`LICENSE`](./LICENSE) (GPLv3) | ✅ |
| **Q1** | **Create Project Charter** | Include vision, mission, community statement, etc. | [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md) | ✅ |
| **Q1** | **Create public GitHub repository** | Ensure Project IP repository is public and accessible. | [GitHub Repository](https://github.com/openchlai/ai) | ✅ |
| **Q1** | **Create README files** | README in English with setup instructions. | [`README.md`](./README.md) | ✅ |
| **Q1** | **List third-party OSS dependencies** | Identify all open source tools, frameworks, and libraries. | [`README.md`](./README.md#prerequisites) (Lists Redis, Celery, MinIO, etc.) | ✅ |
| **Q1** | **Create public documentation repository** | Set up docs repo and publish documentation site. | [`ai_docs/`](./ai_docs/) (Vitepress site source) | ✅ |
| **Q1** | **Enable automated documentation deployment** | Use CI to auto-deploy docs site from repo. | [`README.md`](./README.md) (Badge) & [`.github/workflows`](./.github/workflows/) | ✅ |
| **Q1** | **Establish QA process** | Define testing frameworks, test cases, and QA approach. | [`TESTING_STRATEGY.md`](./TESTING_STRATEGY.md) | ✅ |
| **Q1** | **Document user stories & test cases** | Capture functional expectations and tests. | [`Project Scope Document - OPENCHSAI.md`](./Project%20Scope%20Document%20-%20OPENCHSAI.md) | ✅ |
| **Q1** | **Adopt Code of Conduct** | Select and publish a Code of Conduct. | [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) | ✅ |
| **Q1** | **Internal CoC response process** | Document how reports will be handled internally. | [`GOVERNANCE.md`](./GOVERNANCE.md) or [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) | ✅ |
| **Q1** | **Enforce Pull Request workflow** | All code changes go through PR review. | [`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md) | ✅ |
| **Q2** | **Confirm OSI license compliance** | Ensure all repos have OSI license by end of Q2. | [`LICENSE`](./LICENSE) | ✅ |
| **Q2** | **Publish contributing guidelines** | Explain how external contributors can participate. | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | ✅ |
| **Q2** | **Create public issues/tickets** | Log planned features and known bugs publicly. | [`.github/ISSUE_TEMPLATE/`](./.github/ISSUE_TEMPLATE/) (Active Templates) | ✅ |
| **Q2** | **Use public project board** | Track progress of issues transparently. | [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md) (See "Governance" section) | ✅ |
| **Q2** | **Add developer or user documentation** | Publish either developer or user docs. | [`ai_docs/docs/developer-documentation`](./ai_docs/docs/developer-documentation) | ✅ |
| **Q2** | **Achieve minimum 15% test coverage** | Implement basic unit testing. | [`TEST_HELPLINE_COVERAGE.md`](./TEST_HELPLINE_COVERAGE.md) (75% Achieved) | ✅ |
| **Q2** | **Publish test results** | Make test results publicly accessible. | [`WORKFLOW_TEST_RESULTS.md`](./WORKFLOW_TEST_RESULTS.md) | ✅ |
| **Q3** | **Implement CI/CD pipeline** | Automated build, test, and validation on PRs. | [`ai-service-ci.yml`](./.github/workflows/ai-service-ci.yml) | ✅ |
| **Q3** | **Increase test coverage to ~40%** | Expand unit tests. | [`TEST_HELPLINE_COVERAGE.md`](./TEST_HELPLINE_COVERAGE.md) (75% Achieved) | ✅ |
| **Q3** | **Add issue & PR templates** | Standardize public contributions. | [`.github/ISSUE_TEMPLATE/`](./.github/ISSUE_TEMPLATE/) & [`PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md) | ✅ |
| **Q3** | **Create “Good First Issues”** | Label beginner-friendly tasks. | (GitHub Issues - Standard Practice) | ✅ |
| **Q3** | **Establish public communication channel** | Enable community interaction. | [`GOVERNANCE.md`](./GOVERNANCE.md) (See "Communication Channels") | ✅ |
| **Q3** | **Add remaining documentation type** | Publish both developer and user docs. | [`ai_docs/docs/user-guides`](./ai_docs/docs/user-guides) | ✅ |
| **Q3** | **Review DPG compliance** | Assess alignment with Digital Public Goods criteria. | [`DPG_GAP_ANALYSIS.md`](./DPG_GAP_ANALYSIS.md) (Application Submitted) | ✅ |
| **Q4** | **Finalize all documentation** | Ensure docs are complete and updated. | [`ai_docs/`](./ai_docs/) | ✅ |
| **Q4** | **Achieve 80% test coverage** | Meet contractual QA threshold. | [`TEST_HELPLINE_COVERAGE.md`](.https://github.com/openchlai/ai/blob/main/helplinev1/COVERAGE.md) (Currently 89%%) | ✅|
| **Q4** | **Publish final test evidence** | Make all test results public. | [`coverage.xml`](./coverage.xml) | ✅ |
| **Q4** | **Confirm perpetual public access** | Ensure all IP remains publicly accessible. | [`README.md`](./README.md) & [`LICENSE`](./LICENSE) | ✅ |
| **Q4** | **Growth & sustainability planning** | Conduct growth planning with Open Source mentor. | [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md) (See "Sustainability") | ✅ |
| **Ongoing** | **Publish all improvements & patches** | Continue open publication in perpetuity. | (Git Commit History) | ✅ |
| **Ongoing** | **Ensure interoperability** | Avoid proprietary dependencies. | [`README.md`](./README.md) (Standards-based stack) | ✅ |
