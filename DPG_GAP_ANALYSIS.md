# DPG Anti-Gap Review Matrix (Review & Readiness Tool)

**Purpose:** To systematically identify, evidence, score, and close gaps against the Digital Public Goods (DPG) Standard.

**DPG Application Status:** 🚀 **Submitted**
**DPG Registry Link:** [Insert DPG Registry Link Here]

## Anti-Gap DPG Review Matrix

| DPG Area | Requirement | Current State | Evidence (Link / Doc) | Gap Identified? (Y/N) | Corrective Action Required | Owner | Deadline | Review Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Licensing** | OSI-approved license applied | ✅ Present | [`LICENSE`](./LICENSE) | N | None | - | - | Ready |
| **Licensing** | License compatibility across dependencies | ⚠️ Unverified | - | Y | Run dependency license audit & generate report | Tech Lead | TBD | Pending |
| **Accessibility** | Public repository accessible | ✅ Present | [GitHub Repository](https://github.com/openchlai/ai) | N | None | - | - | Ready |
| **Accessibility** | Repo accessible without login/paywall | ✅ Verified | [GitHub Repository](https://github.com/openchlai/ai) | N | None | - | - | Ready |
| **Interoperability** | Uses open standards (APIs, formats) | ⚠️ Partial | [`ai_docs/docs/developer-documentation/api.md`](./ai_docs/docs/developer-documentation/api.md) | Y | Create `ARCHITECTURE.md` with diagrams | Architect | TBD | Pending |
| **Interoperability** | No proprietary/paid dependencies | ✅ Verified | [`README.md`](./README.md) (Standard OSS stack) | N | None | - | - | Ready |
| **Portability** | Deployable on multiple environments | ✅ Present | [`ai_docs/docs/deployment-administration/installation`](./ai_docs/docs/deployment-administration/installation) | N | None | - | - | Ready |
| **Documentation** | User documentation published | ✅ Present | [`ai_docs/docs/user-guides`](./ai_docs/docs/user-guides) | N | None | - | - | Ready |
| **Documentation** | Developer documentation published | ✅ Present | [`ai_docs/docs/developer-documentation`](./ai_docs/docs/developer-documentation) | N | None | - | - | Ready |
| **Governance** | CONTRIBUTING guidelines exist | ✅ Present | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | N | None | - | - | Ready |
| **Governance** | Code of Conduct published | ✅ Present | [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) | N | None | - | - | Ready |
| **QA** | CI pipeline implemented | ✅ Present | [`.github/workflows/ai-service-ci.yml`](./.github/workflows/ai-service-ci.yml) | N | None | - | - | Ready |
| **QA** | Test coverage ≥ required threshold | ⚠️ 75% vs 80% | [`TEST_HELPLINE_COVERAGE.md`](./TEST_HELPLINE_COVERAGE.md) | Y | Increase test coverage to 80% | QA Lead | TBD | Pending |
| **QA** | Test results publicly available | ✅ Present | [`WORKFLOW_TEST_RESULTS.md`](./WORKFLOW_TEST_RESULTS.md) | N | None | - | - | Ready |
| **Privacy** | Privacy policy documented | ✅ Present | [`PRIVACY_POLICY.md`](./PRIVACY_POLICY.md) | N | None | - | - | Ready |
| **Privacy** | Data minimization enforced | ⚠️ Unknown | - | Y | Create Data Flow Diagram / Privacy Map | Data Lead | TBD | Pending |
| **Security** | Basic threat model documented | ✅ Present | [`.github/SECURITY.md`](./.github/SECURITY.md) | N | Review & Expand if necessary | Sec Lead | - | Ready |
| **AI Ethics** | Model card available | ❌ Missing | - | Y | Create Model Cards in `models/` directory | AI/ML Lead | TBD | Pending |
| **AI Ethics** | Bias & risk mitigation documented | ✅ Present | [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md) (Ethical Considerations) | N | None | - | - | Ready |
| **Sustainability** | Community contribution enabled | ✅ Present | [GitHub Issues](https://github.com/openchlai/ai/issues) | N | None | - | - | Ready |
| **Sustainability** | Roadmap publicly visible | ❌ Missing | - | Y | Create `ROADMAP.md` | Product Owner | TBD | Pending |

## Anti-Gravity Rules (Non-Negotiable)

1.  **No Evidence = Non-Compliant**: Statements without links or documents are invalid.
2.  **Every Gap Must Have an Owner**: Unowned gaps automatically fail internal review.
3.  **Fail Fast Principle**: Any “Yes” in Gap Identified must block DPG submission until resolved.

## Minimum Passing Condition (Internal Gate)

You are DPG-Review Ready only if:
- All rows show **Gap Identified = No**
- Final sign-off recorded by DPG Compliance Lead
