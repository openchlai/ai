# Open Source License

## Overview

OpenCHS is an open-source project supported by the UNICEF Venture Fund and released under a permissive open-source license to maximize its impact on child protection and social services globally.

---

## Table of Contents

1. [License Summary](#license-summary)
2. [MIT License Text](#mit-license-text)
3. [License Rationale](#license-rationale)
4. [Third-Party Licenses](#third-party-licenses)
5. [Contribution License](#contribution-license)
6. [Commercial Use](#commercial-use)
7. [UNICEF Attribution](#unicef-attribution)

---

## License Summary

**License**: MIT License  
**SPDX Identifier**: MIT  
**Copyright Holder**: UNICEF Venture Fund  
**Project**: OpenCHS (Open Child Helpline System)

### Key Permissions

✅ **Commercial Use**: Can be used commercially  
✅ **Modification**: Can be modified  
✅ **Distribution**: Can be distributed  
✅ **Private Use**: Can be used privately  
✅ **Patent Use**: Patent use allowed

### Conditions

📋 **License and Copyright Notice**: Must include original license and copyright notice  
📋 **State Changes**: Document modifications to the original code

### Limitations

⚠️ **Liability**: No liability for damages  
⚠️ **Warranty**: No warranty provided

---

## MIT License Text

```
MIT License

Copyright (c) 2024-2025 UNICEF Venture Fund

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## License Rationale

### Why MIT License?

OpenCHS uses the MIT License for several strategic reasons:

1. **Maximum Accessibility**
   - Minimal restrictions on use
   - Easy to understand and comply with
   - Compatible with most other licenses

2. **Commercial Adoption**
   - Allows commercial use without copyleft requirements
   - Enables organizations to build sustainable business models
   - Facilitates integration into proprietary systems

3. **Global Impact**
   - Removes barriers to adoption in different jurisdictions
   - Allows adaptation for local contexts
   - Enables both NGO and government implementations

4. **Innovation Encouragement**
   - Freedom to modify and improve
   - Can be integrated into larger systems
   - Encourages derivative works and enhancements

5. **UNICEF Mission Alignment**
   - Supports UNICEF's open innovation principles
   - Facilitates rapid scaling globally
   - Enables local customization for child protection needs

### Open Source Principles

OpenCHS adheres to the **Open Source Definition** (OSD) by the Open Source Initiative:

1. **Free Redistribution**: No restrictions on selling or giving away
2. **Source Code**: Source code must be included or easily obtainable
3. **Derived Works**: Modifications and derived works allowed
4. **Integrity of Author's Source Code**: Original source clearly identified
5. **No Discrimination**: Against persons, groups, or fields of endeavor
6. **License Distribution**: Rights apply to all recipients
7. **License Not Product-Specific**: Rights not dependent on distribution
8. **License Not Restrictive**: Cannot restrict other software
9. **License Technologically Neutral**: Not specific to any technology

---

## Third-Party Licenses

OpenCHS incorporates various open-source components. Below is a comprehensive list of third-party licenses:

### Backend (Helpline System - PHP)

| Component | License | Purpose |
|-----------|---------|---------|
| PHP | PHP License v3.01 | Programming language |
| MySQL | GPL v2 | Database system |
| Nginx | BSD-2-Clause | Web server |
| Laravel Framework | MIT | PHP framework (if used) |
| Composer Dependencies | Various (MIT, BSD, Apache) | PHP package manager |

### AI Service (Python)

| Component | License | Purpose |
|-----------|---------|---------|
| Python | PSF License | Programming language |
| FastAPI | MIT | Web framework |
| PyTorch | BSD-3-Clause | Machine learning framework |
| Transformers (HuggingFace) | Apache 2.0 | NLP models |
| Celery | BSD-3-Clause | Task queue |
| Redis | BSD-3-Clause | In-memory database |
| OpenAI Whisper | MIT | Speech recognition |
| spaCy | MIT | NLP library |
| Librosa | ISC License | Audio processing |

### Frontend (if applicable)

| Component | License | Purpose |
|-----------|---------|---------|
| Vue.js | MIT | JavaScript framework |
| Node.js | MIT | JavaScript runtime |
| Tailwind CSS | MIT | CSS framework |
| Various npm packages | MIT, Apache 2.0, BSD | Various utilities |

### Infrastructure

| Component | License | Purpose |
|-----------|---------|---------|
| Docker | Apache 2.0 | Containerization |
| Kubernetes | Apache 2.0 | Container orchestration |
| Linux (Ubuntu) | GPL v2 | Operating system |

### Full Dependency List

For a complete and up-to-date list of dependencies and their licenses, see:
- **Helpline System**: `composer.json` and `composer.lock`
- **AI Service**: `requirements.txt` and `pip list --format=json`
- **License Report**: Generated using `license-checker` or similar tools

```bash
# Generate license report for Python dependencies
pip-licenses --format=markdown --output-file=LICENSES-PYTHON.md

# Generate license report for PHP dependencies (using composer-license-checker)
composer licenses --format=json > licenses-php.json
```

---

## Contribution License

### Contributor License Agreement (CLA)

Contributors to OpenCHS agree to the following terms:

1. **Grant of Copyright License**
   - Contributors grant UNICEF Venture Fund a perpetual, worldwide, non-exclusive, royalty-free license to their contributions
   - Contributions can be used, reproduced, modified, and distributed

2. **Grant of Patent License**
   - Contributors grant a patent license covering their contributions
   - Ensures freedom to operate for all users

3. **Original Work**
   - Contributors confirm they have the right to grant these licenses
   - Contributions are original work or properly attributed

4. **No Warranty**
   - Contributions provided "as is" without warranties
   - Contributors not liable for damages

### How to Contribute

See [CONTRIBUTING.md](https://github.com/openchs/openchs/blob/main/CONTRIBUTING.md) for:
- Contribution guidelines
- Code of conduct
- Development setup
- Pull request process

```markdown
# Example Contribution

By submitting a pull request, you acknowledge and agree that:

1. Your contribution is your original work
2. You grant UNICEF Venture Fund the rights described in the CLA
3. You have read and agree to follow the Code of Conduct
4. You agree to the MIT License terms for your contribution

Signed: [Your Name]
Date: [Date]
GitHub Username: [@username]
```

---

## Commercial Use

### Commercial Use Policy

OpenCHS explicitly permits commercial use under the MIT License:

#### ✅ Allowed Commercial Activities

1. **Service Delivery**
   - Deploy OpenCHS to provide paid helpline services
   - Offer hosted OpenCHS solutions
   - Provide technical support services

2. **Integration & Customization**
   - Integrate OpenCHS into commercial products
   - Develop paid custom features
   - Offer consulting services for OpenCHS

3. **Training & Education**
   - Provide paid training on OpenCHS
   - Create commercial training materials
   - Offer certification programs

4. **Derivative Works**
   - Create and sell derivative products
   - Build proprietary extensions
   - Develop white-label solutions

#### 📋 Requirements for Commercial Use

1. **License Compliance**
   - Include MIT License text in distributions
   - Maintain copyright notices
   - Document modifications

2. **Attribution**
   - Acknowledge OpenCHS and UNICEF in documentation
   - Link to https://openchs.com where appropriate
   - Use trademark appropriately (see below)

3. **Good Faith**
   - Use in ways that don't harm vulnerable populations
   - Maintain ethical standards in child protection
   - Report security vulnerabilities responsibly

#### ❌ Not Allowed

1. **Misrepresentation**
   - Cannot claim UNICEF endorsement without permission
   - Cannot imply official UNICEF partnership without agreement
   - Cannot misrepresent the nature of modifications

2. **Trademark Infringement**
   - Cannot use UNICEF trademarks without permission
   - Cannot use "OpenCHS" trademark improperly
   - Follow trademark guidelines below

### Commercial Support

Organizations seeking commercial support can:
- Contact UNICEF Venture Fund: ventures@unicef.org
- Engage with approved OpenCHS service providers
- Join the OpenCHS commercial ecosystem

---

## UNICEF Attribution

### Proper Attribution

When using OpenCHS, please provide attribution:

#### Required Attribution

```markdown
This product uses OpenCHS, an open-source child helpline system 
developed with support from the UNICEF Venture Fund.
https://openchs.com
```

#### Recommended Attribution (for websites)

```html
<div class="attribution">
  <p>Powered by <a href="https://openchs.com">OpenCHS</a></p>
  <p>Supported by <a href="https://www.unicef.org/innovation/venturefund">UNICEF Venture Fund</a></p>
</div>
```

#### Logo Usage

**UNICEF Logo**: 
- ❌ Cannot use without explicit permission
- Contact UNICEF for logo usage rights
- Follow UNICEF brand guidelines strictly

**OpenCHS Logo**:
- ✅ Can use to indicate OpenCHS usage
- Must maintain logo integrity
- Cannot modify or create derivatives
- Download from: https://openchs.com/brand

### Trademark Policy

**"OpenCHS"** is a trademark of UNICEF Venture Fund.

#### ✅ Permitted Trademark Use

1. **Factual References**
   - "Built with OpenCHS"
   - "Compatible with OpenCHS"
   - "OpenCHS implementation"

2. **Community References**
   - "OpenCHS User Group"
   - "OpenCHS Conference"
   - "OpenCHS Contributor"

3. **Educational Use**
   - "OpenCHS Training"
   - "Learn OpenCHS"
   - "OpenCHS Tutorial"

#### ❌ Prohibited Trademark Use

1. **Product Names**
   - Cannot name products "OpenCHS [Something]" without permission
   - Cannot use in domain names without permission
   - Cannot create confusion with official project

2. **Endorsement Implications**
   - Cannot imply UNICEF endorsement
   - Cannot suggest official partnership
   - Cannot claim certification without authorization

3. **Misrepresentation**
   - Cannot use in misleading ways
   - Cannot modify and still call it "OpenCHS" without clear distinction

### Trademark Guidelines

For detailed trademark guidelines, visit: https://openchs.com/trademark

For trademark permission requests: trademark@openchs.com

---

## License Compatibility

### Compatible Licenses

OpenCHS (MIT) is compatible with:

✅ **More Permissive**:
- BSD licenses (2-Clause, 3-Clause)
- Apache License 2.0
- ISC License
- Public Domain (CC0)

✅ **Copyleft (One-Way)**:
- GPL v2, v3 (can include MIT code)
- LGPL v2.1, v3
- AGPL v3
- Mozilla Public License 2.0

### Incompatible Licenses

⚠️ **Generally Incompatible**:
- Proprietary licenses (unless specifically allowing MIT integration)
- Some Creative Commons licenses (NC, ND variants)
- Custom restrictive licenses

### Integration Guidance

When integrating OpenCHS with other software:

1. **Check License Compatibility**: Review all dependency licenses
2. **Document Dependencies**: Maintain LICENSES.md or similar
3. **Respect Copyleft**: If using GPL components, understand implications
4. **Maintain Notices**: Keep all copyright and license notices
5. **Consult Legal**: When in doubt, seek legal advice

---

## License Enforcement

### Compliance Monitoring

UNICEF Venture Fund monitors OpenCHS license compliance:

1. **Public Repositories**: GitHub scans for license violations
2. **Community Reports**: Encourage reporting of violations
3. **Periodic Audits**: Review major deployments
4. **Education First**: Prefer education over enforcement

### Violation Response

If license violations are identified:

1. **Contact**: Reach out to the violator
2. **Education**: Explain compliance requirements
3. **Remedy**: Allow time to correct violations
4. **Legal Action**: Reserved for serious or repeated violations

### Reporting Violations

To report license violations:
- Email: legal@openchs.com
- Include: Description, evidence, contact information
- Response time: Within 5 business days

---

## Frequently Asked Questions

### General Questions

**Q: Can I use OpenCHS for my commercial helpline service?**  
A: Yes! The MIT License explicitly permits commercial use.

**Q: Do I need to pay UNICEF to use OpenCHS?**  
A: No, OpenCHS is completely free to use, modify, and distribute.

**Q: Can I modify OpenCHS and sell my modified version?**  
A: Yes, you can modify and sell it, but must include the original MIT License.

**Q: Do I need to share my modifications?**  
A: No, the MIT License doesn't require you to share modifications, but we encourage it!

### Attribution Questions

**Q: How should I credit OpenCHS?**  
A: Include copyright notice, link to https://openchs.com, and mention UNICEF support.

**Q: Can I use the UNICEF logo?**  
A: Not without explicit permission from UNICEF. Contact them directly.

**Q: Can I call my product "OpenCHS Pro"?**  
A: No, this could cause trademark confusion. Use "Powered by OpenCHS" instead.

### Technical Questions

**Q: Are all OpenCHS dependencies MIT licensed?**  
A: No, dependencies have various licenses (MIT, Apache, BSD, etc.), all compatible.

**Q: Can I integrate OpenCHS into GPL software?**  
A: Yes, MIT is compatible with GPL (but the combined work becomes GPL).

**Q: What if I find a dependency with an incompatible license?**  
A: Report it immediately to security@openchs.com so we can address it.

---

## Resources

### Official Resources

- **OpenCHS Website**: https://openchs.com
- **OpenCHS Documentation**: https://docs.openchs.com
- **GitHub Repository**: https://github.com/openchs/openchs
- **License File**: https://github.com/openchs/openchs/blob/main/LICENSE

### UNICEF Resources

- **UNICEF Venture Fund**: https://www.unicef.org/innovation/venturefund
- **UNICEF Innovation**: https://www.unicef.org/innovation
- **Open Source at UNICEF**: https://unicef.github.io

### Legal Resources

- **MIT License**: https://opensource.org/licenses/MIT
- **Open Source Initiative**: https://opensource.org
- **SPDX License List**: https://spdx.org/licenses/

### Contact

- **General Inquiries**: info@openchs.com
- **License Questions**: legal@openchs.com
- **UNICEF Partnership**: ventures@unicef.org

---

**Last Updated**: January 2025  
**Version**: 1.0  
**License Version**: MIT (Unmodified)

---

## Appendix: License Headers

### Recommended File Headers

**For Source Code Files:**

```php
<?php
/**
 * OpenCHS - Open Child Helpline System
 * 
 * Copyright (c) 2024-2025 UNICEF Venture Fund
 * Licensed under the MIT License
 * 
 * https://openchs.com
 * https://github.com/openchs/openchs
 */
```

```python
"""
OpenCHS - Open Child Helpline System

Copyright (c) 2024-2025 UNICEF Venture Fund
Licensed under the MIT License

https://openchs.com
https://github.com/openchs/openchs
"""
```

```javascript
/**
 * OpenCHS - Open Child Helpline System
 * 
 * Copyright (c) 2024-2025 UNICEF Venture Fund
 * Licensed under the MIT License
 * 
 * https://openchs.com
 * https://github.com/openchs/openchs
 */
```

**For Documentation:**

```markdown
---
title: [Document Title]
project: OpenCHS
copyright: Copyright (c) 2024-2025 UNICEF Venture Fund
license: MIT License
website: https://openchs.com
---
```