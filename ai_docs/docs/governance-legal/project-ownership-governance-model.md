# Project Ownership & Governance Model

## Overview

This document defines the ownership structure, governance model, decision-making processes, and accountability mechanisms for the OpenCHS (Open Child Helpline System) project.

---

## Table of Contents

1. [Ownership Structure](#ownership-structure)
2. [Governance Framework](#governance-framework)
3. [Decision-Making Processes](#decision-making-processes)
4. [Roles & Responsibilities](#roles--responsibilities)
5. [Committees & Working Groups](#committees--working-groups)
6. [Community Participation](#community-participation)
7. [Conflict Resolution](#conflict-resolution)
8. [Amendments & Evolution](#amendments--evolution)

---

## Ownership Structure

### Legal Ownership

**Primary Owner**: UNICEF Venture Fund  
**Legal Entity**: United Nations Children's Fund (UNICEF)  
**Project Status**: Open Source Public Good  
**License**: MIT License

### Intellectual Property Rights

1. **Copyright Holder**: UNICEF Venture Fund
   - Owns copyright to original OpenCHS codebase
   - Maintains trademark rights to "OpenCHS" name and logo
   - Grants rights via MIT License

2. **Contributor Rights**:
   - Contributors retain copyright to their contributions
   - Contributors grant license to UNICEF via Contributor License Agreement (CLA)
   - All contributions released under MIT License

3. **Derivative Works**:
   - Anyone can create derivative works under MIT License terms
   - Must maintain attribution to OpenCHS and UNICEF
   - Cannot imply UNICEF endorsement without permission

### Project Assets

| Asset Type | Owner | Access |
|------------|-------|--------|
| **Source Code** | UNICEF Venture Fund | Public (GitHub) |
| **Documentation** | UNICEF Venture Fund | Public (openchs.com) |
| **Trademark** | UNICEF | Controlled use |
| **Domain Names** | UNICEF | Controlled |
| **Social Media** | UNICEF | Controlled |
| **Infrastructure** | UNICEF / Partners | Controlled |
| **Community Forums** | UNICEF | Public |

---

## Governance Framework

### Governance Philosophy

OpenCHS follows a **benevolent dictator governance model** with **open community participation**:

- UNICEF retains ultimate decision-making authority
- Community input is actively sought and valued
- Transparent decision-making processes
- Merit-based contribution recognition
- Consensus-building preferred over decree

### Governance Principles

1. **Transparency**
   - Open decision-making processes
   - Public documentation of decisions
   - Clear communication channels

2. **Inclusivity**
   - Welcome diverse perspectives
   - Accessible participation mechanisms
   - Multiple contribution pathways

3. **Accountability**
   - Clear responsibility assignments
   - Regular reporting and reviews
   - Responsive to community feedback

4. **Sustainability**
   - Long-term project viability
   - Resource stability
   - Knowledge preservation

5. **Child Protection Focus**
   - Child welfare as paramount consideration
   - Ethical data and technology use
   - Safety and security prioritized

### Governance Structure

```
┌──────────────────────────────────────────────────┐
│         UNICEF Venture Fund (Owner)              │
│         • Final decision authority                │
│         • Strategic direction                     │
│         • Resource allocation                     │
└──────────────────┬───────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼──────────┐
│ Steering       │   │  Technical        │
│ Committee      │   │  Advisory Board   │
│                │   │                   │
│ • Strategy     │   │ • Architecture    │
│ • Priorities   │   │ • Standards       │
│ • Partnerships │   │ • Security        │
└───────┬────────┘   └────────┬──────────┘
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────▼───────────┐
        │   Core Team          │
        │                      │
        │ • Project Management │
        │ • Development        │
        │ • Operations         │
        └──────────┬───────────┘
                   │
        ┌──────────▼───────────┐
        │   Community          │
        │                      │
        │ • Contributors       │
        │ • Users              │
        │ • Implementers       │
        └──────────────────────┘
```

---

## Decision-Making Processes

### Decision Types & Authority

| Decision Type | Authority | Process | Timeline |
|--------------|-----------|---------|----------|
| **Strategic Direction** | UNICEF + Steering Committee | Proposal → Review → Approval | 30-60 days |
| **Technical Architecture** | Technical Advisory Board | RFC → Discussion → Consensus | 14-30 days |
| **Code Changes** | Core Team + Maintainers | Pull Request → Review → Merge | 3-7 days |
| **Feature Requests** | Community + Core Team | Issue → Discussion → Prioritization | Ongoing |
| **Bug Fixes** | Maintainers | Report → Fix → Deploy | 1-7 days |
| **Security Issues** | Security Team | Report → Patch → Disclosure | Immediate |
| **Policy Changes** | UNICEF + Steering Committee | Proposal → Consultation → Approval | 30-90 days |

### Request for Comments (RFC) Process

For significant technical changes:

1. **Proposal Creation**
   ```markdown
   # RFC-###: [Title]
   
   ## Summary
   Brief description of the change
   
   ## Motivation
   Why is this change needed?
   
   ## Detailed Design
   Technical specification
   
   ## Alternatives Considered
   What other approaches were evaluated?
   
   ## Impact Assessment
   - Performance impact
   - Security impact
   - User impact
   - Migration requirements
   ```

2. **Community Review** (14 days minimum)
   - Posted to GitHub Discussions
   - Announced on mailing list
   - Open for community feedback

3. **Technical Advisory Board Review**
   - Evaluation of technical merit
   - Assessment of risks
   - Recommendation to Core Team

4. **Final Decision**
   - Core Team makes final decision
   - Decision documented and published
   - Implementation timeline established

### Consensus Building

**Preferred Approach**: Lazy Consensus
- Proposal made publicly
- Reasonable time for objections (typically 72 hours for minor, 14 days for major)
- No objections = consensus
- Objections addressed through discussion

**Voting (when consensus fails)**:
- Steering Committee: Simple majority
- Technical Advisory Board: 2/3 supermajority for architecture changes
- Core Team: Simple majority

---

## Roles & Responsibilities

### UNICEF Venture Fund

**Responsibilities**:
- Overall project ownership and strategic direction
- Final decision authority on major issues
- Resource allocation and fundraising
- Partnership development
- Brand and trademark management
- Legal and compliance oversight

**Commitments**:
- Maintain project as open source public good
- Support long-term sustainability
- Foster inclusive community
- Ensure child protection focus

### Steering Committee

**Composition**:
- UNICEF Venture Fund representative (Chair)
- 2-3 implementing partner representatives
- 1-2 technical experts
- 1 child protection specialist
- Term: 2 years, renewable

**Responsibilities**:
- Strategic planning and prioritization
- Resource allocation recommendations
- Partnership approval
- Policy guidance
- Annual roadmap approval

**Meetings**: Quarterly, with special sessions as needed

### Technical Advisory Board

**Composition**:
- 5-7 technical experts
- Diverse backgrounds (ML, security, systems, UX)
- Geographic diversity
- Term: 2 years, renewable

**Responsibilities**:
- Technical architecture decisions
- Technology stack recommendations
- Security and privacy guidance
- Code quality standards
- Technical roadmap input

**Selection**: Merit-based, nominated by community or Steering Committee

**Meetings**: Monthly, with ad-hoc discussions

### Core Team

**Composition**:
- Project Manager
- Lead Developers (2-3)
- DevOps Engineer
- Community Manager
- Documentation Lead

**Responsibilities**:
- Day-to-day project management
- Code review and merging
- Release management
- Community engagement
- Documentation maintenance
- Issue triage and prioritization

**Authority**:
- Code acceptance decisions
- Bug fix prioritization
- Minor feature decisions
- Community moderation

### Maintainers

**Requirements**:
- Demonstrated expertise in relevant area
- History of quality contributions
- Commitment to project values
- Available for code review

**Responsibilities**:
- Code review and feedback
- Mentor contributors
- Maintain code quality
- Monitor security issues

**Areas of Maintenance**:
- Helpline System (PHP/MySQL)
- AI Service (Python/ML)
- Infrastructure (Docker/K8s)
- Documentation
- Testing & QA

### Contributors

**All are welcome to contribute!**

**Contribution Types**:
- Code contributions
- Bug reports
- Documentation improvements
- Translation
- Testing
- Design and UX
- Community support

**Recognition**:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Eligible for maintainer status
- Invited to community events

---

## Committees & Working Groups

### Standing Committees

#### 1. Security Committee

**Purpose**: Ensure security and privacy of OpenCHS

**Members**:
- Security Lead (Core Team)
- 2-3 Security experts
- Privacy/legal representative

**Responsibilities**:
- Security vulnerability management
- Security audits and assessments
- Security policy development
- Incident response coordination

**Reporting**: Monthly to Technical Advisory Board

#### 2. Child Protection Committee

**Purpose**: Ensure child safety and protection focus

**Members**:
- Child protection specialist (Chair)
- Social worker representative
- Ethics expert
- User representative (implementing organization)

**Responsibilities**:
- Child protection policy guidance
- Ethical review of features
- User safety considerations
- Safeguarding standards

**Reporting**: Quarterly to Steering Committee

### Working Groups

**Formation**: Ad-hoc, based on need

**Examples**:
- Localization Working Group
- AI Ethics Working Group
- Performance Optimization Working Group
- User Experience Working Group

**Process**:
1. Proposal submitted to Core Team
2. Approval based on need and resources
3. Charter developed (goals, timeline, deliverables)
4. Regular progress updates
5. Dissolution upon completion or after 12 months

---

## Community Participation

### Communication Channels

| Channel | Purpose | Access |
|---------|---------|--------|
| **GitHub** | Code, issues, discussions | Public |
| **Mailing List** | Announcements, discussions | Public (subscribe) |
| **Slack/Discord** | Real-time communication | Open registration |
| **Monthly Community Call** | Updates, Q&A | Public (virtual) |
| **Annual Conference** | In-person gathering | Open registration |
| **Website** | Documentation, news | Public |

### Community Roles

**Observer**: Anyone interested in the project
- Can view all public discussions
- Can attend community calls
- Receives announcements

**Participant**: Active community member
- Can comment on issues and discussions
- Can submit feature requests
- Can participate in working groups

**Contributor**: Makes code or content contributions
- Can submit pull requests
- Listed in CONTRIBUTORS.md
- Eligible for recognition

**Maintainer**: Trusted contributor with merge rights
- Reviews and merges contributions
- Mentors new contributors
- Represents area of expertise

### Contributor Pathway

```
Observer → Participant → Contributor → Maintainer
   ↓           ↓            ↓            ↓
 Watch     Comment      Submit      Review &
 Learn     Discuss       PRs         Merge
```

**Becoming a Maintainer**:
1. Consistent, quality contributions over 6+ months
2. Demonstrated technical expertise
3. Good communication and collaboration
4. Nomination by existing maintainer
5. Approval by Core Team

---

## Conflict Resolution

### Conflict Resolution Process

#### Level 1: Direct Resolution
- Parties attempt to resolve directly
- Good faith discussion
- Focus on project best interests

#### Level 2: Mediation
- Involve relevant committee or team lead
- Neutral party facilitates discussion
- Seek consensus solution

#### Level 3: Escalation
- Escalate to Steering Committee
- Formal review of issue
- Binding decision made

#### Level 4: Final Appeal
- Appeal to UNICEF Venture Fund
- Final decision authority
- Decision is binding

### Code of Conduct Violations

**Process**:
1. Report to conduct@openchs.com
2. Review by Community Manager + 2 committee members
3. Investigation (confidential)
4. Determination and action
5. Appeal process available

**Possible Actions**:
- Warning
- Temporary suspension
- Permanent ban
- Depending on severity

### Technical Disputes

**Disagreement on technical approach**:
1. Discussion on GitHub or mailing list
2. Technical Advisory Board review
3. RFC process if needed
4. Core Team decision
5. Appeal to Steering Committee if necessary

---

## Financial Governance

### Funding Sources

1. **UNICEF Venture Fund**: Primary funding
2. **Grants**: International development organizations
3. **Government Partnerships**: National implementations
4. **Corporate Sponsorship**: Technology and service partners
5. **Community Donations**: Optional support

### Budget Allocation

**Approved by**: Steering Committee  
**Review**: Quarterly  
**Categories**:
- Development (50%)
- Infrastructure (20%)
- Community & Documentation (15%)
- Security & Compliance (10%)
- Events & Outreach (5%)

### Financial Transparency

- Annual budget published
- Quarterly financial reports
- Major expenditures disclosed
- Audited annually

---

## Accountability Mechanisms

### Performance Reviews

**Project Performance**:
- Quarterly review by Steering Committee
- Annual comprehensive review
- Key metrics: adoption, impact, quality, community health

**Committee Performance**:
- Annual self-assessment
- Community feedback surveys
- Adjust composition or processes as needed

**Individual Performance**:
- Core Team: Annual reviews by Project Manager
- Maintainers: Peer review and contribution metrics
- Informal feedback culture

### Reporting Requirements

**To UNICEF Venture Fund** (Quarterly):
- Progress against roadmap
- Financial report
- Risk assessment
- Impact metrics

**To Community** (Monthly):
- Development updates
- Metrics dashboard
- Upcoming decisions
- Contribution opportunities

**To Implementing Partners** (As needed):
- Technical updates
- Security advisories
- Training materials
- Best practices

### External Audits

**Types**:
- **Security Audit**: Annual
- **Code Quality Audit**: Annual
- **Financial Audit**: Annual
- **Child Protection Compliance**: Biannual

**Process**:
1. Engage independent auditor
2. Audit conducted
3. Report reviewed by Steering Committee
4. Action plan developed
5. Summary published to community

---

## Succession Planning

### Leadership Transitions

**Core Team Members**:
- Notice period: 3 months preferred
- Knowledge transfer to successor
- Documentation of responsibilities
- Handoff support period

**Steering Committee**:
- Staggered terms to ensure continuity
- Vice-chair role for succession
- Regular recruitment of new members

**Maintainers**:
- Shadow period for new maintainers
- Gradual transition of responsibilities
- Emeritus status for retiring maintainers

### Project Continuity

**Key Risks**:
- Loss of UNICEF funding
- Key personnel departure
- Technology obsolescence
- Decreased adoption

**Mitigation**:
- Diverse funding sources
- Knowledge documentation
- Regular technology updates
- Strong community engagement

**Contingency Plan**:
- Documented in separate operational plan
- Reviewed annually
- Includes asset transfer procedures if needed

---

## Evolution of Governance

### Amendment Process

**Minor Changes** (clarifications, process improvements):
1. Proposal by anyone
2. Discussion (14 days)
3. Core Team approval
4. Update and publish

**Major Changes** (structural changes, new committees):
1. Proposal to Steering Committee
2. Community consultation (30 days)
3. Steering Committee review
4. UNICEF approval
5. Implementation plan
6. Communication to community

### Regular Reviews

**Annual Governance Review**:
- Effectiveness assessment
- Community feedback
- Comparative analysis (other projects)
- Recommendations for improvements

**Governance Metrics**:
- Decision-making efficiency
- Community participation rates
- Contributor satisfaction
- Conflict resolution effectiveness
- Time to resolve issues

---

## Transitional Provisions

### Current Phase (2024-2026)

**Status**: Early stage, establishing governance

**Priorities**:
- Build core team
- Establish committees
- Develop community
- Refine processes

**Reviews**: Quarterly governance reviews during this phase

### Mature Phase (2026+)

**Evolution Expectations**:
- More formalized structures
- Greater community autonomy
- Potential foundation establishment
- Expanded partnerships

### Foundation Consideration

**When**: If project reaches significant scale (2027+)

**Potential Model**: 
- OpenCHS Foundation (independent entity)
- UNICEF as founding member
- Multi-stakeholder governance
- Professional staff

**Requirements**:
- $5M+ annual budget
- 50+ active contributors
- 100+ implementations
- Sustainable funding model

---

## Appendices

### Appendix A: Contact Information

**General Inquiries**: info@openchs.com  
**Governance Questions**: governance@openchs.com  
**UNICEF Venture Fund**: ventures@unicef.org  
**Security Issues**: security@openchs.com  
**Code of Conduct**: conduct@openchs.com

### Appendix B: Key Documents

- Project Charter: https://openchs.com/charter
- Code of Conduct: https://openchs.com/conduct
- Contributing Guide: https://github.com/openchs/openchs/CONTRIBUTING.md
- Security Policy: https://github.com/openchs/openchs/SECURITY.md
- License: https://github.com/openchs/openchs/LICENSE

### Appendix C: Meeting Schedules

| Body | Frequency | Day/Time | Format |
|------|-----------|----------|--------|
| Steering Committee | Quarterly | First Tuesday, 14:00 UTC | Virtual |
| Technical Advisory Board | Monthly | Third Thursday, 15:00 UTC | Virtual |
| Core Team Sync | Weekly | Monday, 10:00 UTC | Virtual |
| Community Call | Monthly | Last Friday, 16:00 UTC | Virtual (Public) |
| Security Committee | Monthly | Second Wednesday, 13:00 UTC | Virtual |

### Appendix D: Decision Log Template

```markdown
# Decision Log Entry

**ID**: DEC-YYYY-NNN  
**Date**: YYYY-MM-DD  
**Decision Maker**: [Committee/Team]  
**Status**: [Proposed/Approved/Implemented/Superseded]

## Context
[Background and problem statement]

## Decision
[What was decided]

## Rationale
[Why this decision was made]

## Alternatives Considered
[Other options evaluated]

## Consequences
[Expected outcomes and impacts]

## Implementation
[How and when decision will be implemented]

## Review Date
[When decision should be reviewed]
```

---

## Glossary

**Benevolent Dictator**: Governance model where ultimate authority rests with one entity (UNICEF) but community input is valued

**Consensus**: Agreement reached through discussion without formal voting

**Lazy Consensus**: Consensus assumed if no objections raised within specified time

**Maintainer**: Trusted contributor with code merge privileges

**RFC**: Request for Comments - formal proposal for significant changes

**Steering Committee**: Strategic oversight body

**Technical Advisory Board**: Technical guidance and architecture decisions body

---

## Version History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0 | January 2025 | Initial version | UNICEF Venture Fund |

---

**Last Updated**: January 2025  
**Next Review**: January 2026  
**Document Owner**: UNICEF Venture Fund  
**Contact**: governance@openchs.com