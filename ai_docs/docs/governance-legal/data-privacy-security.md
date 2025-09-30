# Data Privacy & Security

## Overview

OpenCHS is committed to protecting the privacy and security of sensitive data, particularly information related to children and vulnerable populations. This document outlines the data privacy and security measures implemented in OpenCHS, aligned with international standards and best practices.

---

## Table of Contents

1. [Privacy Principles](#privacy-principles)
2. [Data Protection Framework](#data-protection-framework)
3. [Security Architecture](#security-architecture)
4. [Data Classification](#data-classification)
5. [Access Control](#access-control)
6. [Data Handling Procedures](#data-handling-procedures)
7. [Compliance & Standards](#compliance--standards)
8. [Incident Response](#incident-response)

---

## Privacy Principles

### Core Principles

OpenCHS adheres to internationally recognized privacy principles:

1. **Lawfulness, Fairness, and Transparency**
   - Data processing is lawful and transparent
   - Clear communication about data use
   - Documented legal basis for processing

2. **Purpose Limitation**
   - Data collected only for specified, explicit purposes
   - No further processing incompatible with original purpose
   - Clear documentation of processing purposes

3. **Data Minimization**
   - Only necessary data is collected
   - Regular review of data collection practices
   - Automatic deletion of unnecessary data

4. **Accuracy**
   - Reasonable steps to ensure data accuracy
   - Mechanisms for data subjects to correct information
   - Regular data quality reviews

5. **Storage Limitation**
   - Data retained only as long as necessary
   - Clear retention schedules
   - Automatic deletion after retention period

6. **Integrity and Confidentiality**
   - Appropriate security measures
   - Protection against unauthorized access
   - Regular security assessments

7. **Accountability**
   - Documented compliance measures
   - Regular audits and reviews
   - Clear responsibility assignments

### Child Data Protection

Special protections for data concerning children:

- **Enhanced Consent**: Additional safeguards for child data processing
- **Age-Appropriate Communication**: Clear, simple language in privacy notices
- **Parental Rights**: Mechanisms for guardian involvement
- **Best Interests**: Child's best interests as primary consideration
- **Minimal Data Collection**: Strict adherence to data minimization
- **Secure Processing**: Enhanced security measures for child data

---

## Data Protection Framework

### Legal Basis for Processing

OpenCHS processes personal data under the following legal bases:

1. **Legitimate Interests**
   - Protecting children and vulnerable populations
   - Providing crisis intervention services
   - Improving child protection systems

2. **Public Interest**
   - Fulfilling child protection mandates
   - Supporting government social services
   - Contributing to public health and safety

3. **Vital Interests**
   - Protecting life and safety in emergencies
   - Immediate crisis response

4. **Legal Obligation**
   - Compliance with mandatory reporting requirements
   - Adherence to child protection laws

### Data Subject Rights

OpenCHS respects the following data subject rights:

| Right | Description | Implementation |
|-------|-------------|----------------|
| **Right to Information** | Clear information about data processing | Privacy notices, documentation available at openchs.com |
| **Right of Access** | Access to personal data | Data access request process |
| **Right to Rectification** | Correction of inaccurate data | User profile editing, case correction workflows |
| **Right to Erasure** | Deletion of data (where applicable) | Data deletion procedures with legal safeguards |
| **Right to Restriction** | Limitation of processing | Processing restriction flags |
| **Right to Data Portability** | Receive data in portable format | Data export functionality |
| **Right to Object** | Object to certain processing | Opt-out mechanisms (where applicable) |

### Privacy by Design

OpenCHS implements Privacy by Design principles:

- **Proactive not Reactive**: Privacy embedded from design stage
- **Privacy as Default**: Highest privacy settings by default
- **Full Functionality**: Privacy without compromising functionality
- **End-to-End Security**: Protection throughout data lifecycle
- **Visibility and Transparency**: Clear privacy operations
- **User-Centric**: Respect for user privacy

---

## Security Architecture

### Multi-Layer Security

```
┌─────────────────────────────────────────────────┐
│           Application Layer Security            │
│  • Authentication & Authorization               │
│  • Input Validation                            │
│  • Session Management                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Transport Layer Security              │
│  • TLS 1.3 Encryption                          │
│  • Certificate Pinning                         │
│  • Secure Communication Channels               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Data Layer Security                   │
│  • Encryption at Rest                          │
│  • Database Access Controls                    │
│  • Audit Logging                               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         Infrastructure Security                 │
│  • Firewall Rules                              │
│  • Network Segmentation                        │
│  • Intrusion Detection                         │
└─────────────────────────────────────────────────┘
```

### Encryption Standards

**Data in Transit:**
- TLS 1.3 for all network communications
- Perfect Forward Secrecy (PFS)
- Strong cipher suites only
- Certificate-based authentication

**Data at Rest:**
- AES-256 encryption for sensitive data
- Encrypted database fields for PII
- Encrypted backups
- Secure key management

**Implementation Example:**

```sql
-- Encrypted fields in database
CREATE TABLE helpline.contact (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(255),  -- Encrypted
    email VARCHAR(255),  -- Encrypted
    name_encrypted BLOB, -- AES-256 encrypted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Authentication & Authorization

**Multi-Factor Authentication (MFA):**
- Required for administrative accounts
- Optional for regular users
- TOTP (Time-based One-Time Password) support
- SMS-based authentication option

**Role-Based Access Control (RBAC):**
- Principle of least privilege
- Granular permissions
- Regular access reviews
- Automatic session expiration

**Password Security:**
- Minimum 12 characters for admin accounts
- Complexity requirements (uppercase, lowercase, numbers, symbols)
- Bcrypt hashing (work factor 10+)
- Password history (last 5 passwords)
- Account lockout after 5 failed attempts
- 90-day password expiration for sensitive roles

---

## Data Classification

### Classification Levels

| Level | Description | Examples | Security Requirements |
|-------|-------------|----------|----------------------|
| **Critical** | Highly sensitive child protection data | Child identity, abuse details, medical information | Encrypted at rest and in transit, strict access control, audit logging |
| **High** | Personal identifiable information | Names, phone numbers, emails, addresses | Encrypted at rest, TLS in transit, role-based access |
| **Medium** | Case metadata | Case status, category, timestamps | TLS in transit, access control |
| **Low** | Non-sensitive operational data | System logs, aggregated statistics | Basic access control |
| **Public** | Information intended for public access | Documentation, public reports | No special restrictions |

### Data Handling by Classification

**Critical Data Handling:**
```python
# Example: Handling critical child data
from cryptography.fernet import Fernet

class ChildDataHandler:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_sensitive_data(self, data):
        """Encrypt critical child protection data"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt with audit logging"""
        # Log access attempt
        audit_log.record({
            'action': 'decrypt_sensitive_data',
            'user_id': current_user.id,
            'timestamp': datetime.now(),
            'data_type': 'child_protection'
        })
        return self.cipher.decrypt(encrypted_data).decode()
```

---

## Access Control

### Access Control Matrix

| Role | View Cases | Edit Cases | Delete Cases | View Reports | Export Data | System Admin |
|------|-----------|-----------|-------------|-------------|------------|-------------|
| **Viewer** | Own/Assigned | ❌ | ❌ | Limited | ❌ | ❌ |
| **Counselor** | Own/Assigned | Own/Assigned | ❌ | Own | ❌ | ❌ |
| **Supervisor** | Team | Team | ❌ | Team | Team | ❌ |
| **Administrator** | All | All | All | All | All | ❌ |
| **Super Admin** | All | All | All | All | All | ✅ |

### Access Audit Trail

All data access is logged:

```sql
-- Audit log structure
CREATE TABLE helpline.data_access_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT UNSIGNED NOT NULL,
    action VARCHAR(50) NOT NULL,  -- view, edit, delete, export
    resource_type VARCHAR(50) NOT NULL,
    resource_id INT UNSIGNED,
    ip_address VARCHAR(45),
    user_agent TEXT,
    data_classification VARCHAR(20),
    justification TEXT,  -- Required for critical data access
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_resource (resource_type, resource_id)
);
```

### Need-to-Know Principle

Access granted only when:
1. User role permits access
2. Access is necessary for job function
3. Data is relevant to assigned cases
4. Access is logged and auditable

---

## Data Handling Procedures

### Data Collection

**Minimal Data Collection:**
```javascript
// Example: Collect only necessary information
const caseData = {
    // Required fields only
    contact_method: 'phone',  // phone, chat, email
    issue_category: 'mental_health',
    priority: 'high',
    
    // Optional fields - collect only if relevant
    age_range: '13-17',  // Age range instead of exact age
    location: 'Nairobi',  // General location, not exact address
    
    // Never collect unless absolutely necessary:
    // - Full names (use initials or case IDs)
    // - Exact addresses
    // - Identification numbers
    // - Unnecessary demographic details
};
```

### Data Anonymization

**De-identification Techniques:**

1. **Pseudonymization**: Replace identifiers with pseudonyms
   ```sql
   -- Replace actual phone number with hash
   UPDATE helpline.contact
   SET phone_pseudonym = SHA2(phone, 256),
       phone = NULL
   WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);
   ```

2. **Aggregation**: Report only aggregate statistics
   ```sql
   -- Aggregate reporting (no individual identification)
   SELECT 
       DATE_FORMAT(created_at, '%Y-%m') as month,
       issue_category,
       COUNT(*) as case_count,
       AVG(resolution_time) as avg_resolution_time
   FROM helpline.kase
   GROUP BY month, issue_category;
   ```

3. **Data Masking**: Mask sensitive information in logs
   ```python
   # Mask sensitive data in logs
   def mask_phone(phone):
       if len(phone) > 4:
           return f"***-***-{phone[-4:]}"
       return "***"
   
   logger.info(f"Call received from {mask_phone(caller_phone)}")
   ```

### Data Retention

**Retention Schedule:**

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| Active case data | Duration of case + 2 years | Anonymization then deletion |
| Closed case summaries | 5 years | Secure deletion |
| Audit logs | 7 years | Secure archival then deletion |
| System logs | 90 days | Automatic deletion |
| Backups | 30 days | Secure overwrite |
| AI processing recordings | 24 hours (unless case-linked) | Secure deletion |

**Automated Retention Enforcement:**

```bash
#!/bin/bash
# /usr/local/bin/enforce-data-retention.sh

# Delete old AI processing files (24 hours)
find /opt/openchs-ai/uploads -type f -mtime +1 -delete

# Anonymize old case data (2 years)
mysql helpline -e "
    UPDATE contact
    SET phone = NULL,
        email = NULL,
        name = 'ANONYMIZED'
    WHERE id IN (
        SELECT contact_id FROM kase
        WHERE status = 'closed'
        AND updated_at < DATE_SUB(NOW(), INTERVAL 2 YEAR)
    );
"

# Delete very old audit logs (7 years)
mysql helpline -e "
    DELETE FROM audit_log
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL 7 YEAR);
"

echo "Data retention policy enforced: $(date)" >> /var/log/openchs/retention.log
```

### Data Transfer

**Secure Data Transfer Protocols:**

1. **Internal Transfer**: TLS 1.3 within system
2. **External Transfer**: 
   - Encrypted archives (AES-256)
   - Secure file transfer (SFTP/SCP)
   - Password-protected with separate password transmission
   - Minimal data transfer (only what's necessary)

3. **Cross-Border Transfer**: 
   - Documented data transfer agreements
   - Adequate protection mechanisms
   - Regular compliance reviews

---

## Compliance & Standards

### Regulatory Compliance

OpenCHS complies with:

1. **GDPR (General Data Protection Regulation)**
   - EU data protection standards
   - Privacy by design
   - Data subject rights

2. **Child Online Privacy Protection (COPPA-inspired)**
   - Enhanced protections for child data
   - Parental notification mechanisms
   - Minimal data collection

3. **ISO/IEC 27001** (Information Security Management)
   - Security controls
   - Risk management
   - Continuous improvement

4. **Local Data Protection Laws**
   - Kenya Data Protection Act
   - Country-specific requirements
   - Regional compliance

### UNICEF Data Protection Standards

OpenCHS aligns with UNICEF's Procedure on Ethical Standards in Research, Evaluation, Data Collection and Analysis:

- **Do No Harm**: Ensure data use doesn't cause harm
- **Best Interests of Child**: Child welfare paramount
- **Non-Discrimination**: Equitable data practices
- **Informed Consent**: Clear consent mechanisms
- **Confidentiality**: Strong confidentiality protections

### Security Certifications

**Target Certifications:**
- ISO 27001 (Information Security Management)
- SOC 2 Type II (Service Organization Control)
- Cloud Security Alliance STAR

**Assessment Schedule:**
- Annual security audits
- Quarterly vulnerability assessments
- Continuous monitoring

---

## Incident Response

### Data Breach Response Plan

**Phase 1: Detection & Assessment (0-24 hours)**
1. Detect and confirm breach
2. Activate incident response team
3. Assess scope and impact
4. Contain the breach

**Phase 2: Notification (24-72 hours)**
1. Notify supervisory authority (within 72 hours)
2. Notify affected data subjects (without undue delay)
3. Document breach details
4. Prepare public statement if necessary

**Phase 3: Investigation & Remediation (72 hours - 30 days)**
1. Conduct forensic investigation
2. Implement remediation measures
3. Review and update security controls
4. Document lessons learned

**Phase 4: Post-Incident Review (30+ days)**
1. Comprehensive incident report
2. Update policies and procedures
3. Staff training on new measures
4. External audit if required

### Incident Response Team

| Role | Responsibility |
|------|---------------|
| **Incident Manager** | Overall coordination, decision making |
| **Technical Lead** | Technical investigation, remediation |
| **Legal Counsel** | Legal obligations, notifications |
| **Communications Lead** | Internal/external communications |
| **Data Protection Officer** | Privacy compliance, authority liaison |

### Breach Notification Template

```markdown
SUBJECT: Data Security Incident Notification

Dear [Data Subject/Authority],

We are writing to inform you of a data security incident involving OpenCHS.

INCIDENT DETAILS:
- Date of Incident: [DATE]
- Discovery Date: [DATE]
- Type of Data Affected: [DESCRIPTION]
- Number of Individuals Affected: [NUMBER]

ACTIONS TAKEN:
- [Description of containment measures]
- [Description of remediation steps]
- [Security enhancements implemented]

YOUR RIGHTS:
- [Information about data subject rights]
- [Steps individuals can take]

CONTACT INFORMATION:
Data Protection Officer: dpo@openchs.com
Support: support@openchs.com

We sincerely apologize for this incident and are committed to protecting your data.

OpenCHS Team
```

---

## Security Best Practices

### For Administrators

1. **Regular Security Updates**
   - Apply security patches within 48 hours
   - Keep all systems updated
   - Monitor security advisories

2. **Access Reviews**
   - Quarterly user access reviews
   - Remove unnecessary privileges
   - Document access justifications

3. **Security Monitoring**
   - Daily review of security logs
   - Alert on suspicious activities
   - Investigate anomalies promptly

4. **Backup Verification**
   - Weekly backup tests
   - Verify backup integrity
   - Test restoration procedures

### For Users

1. **Strong Authentication**
   - Use strong, unique passwords
   - Enable MFA where available
   - Never share credentials

2. **Secure Devices**
   - Keep devices updated
   - Use device encryption
   - Lock screens when away

3. **Data Handling**
   - Only access necessary data
   - Never email sensitive data
   - Use secure channels for communication

4. **Incident Reporting**
   - Report suspicious activities immediately
   - Don't attempt to investigate yourself
   - Follow incident reporting procedures

---

## Privacy Impact Assessment

OpenCHS conducts regular Privacy Impact Assessments (PIA):

### PIA Components

1. **Data Flow Analysis**
   - Map data collection points
   - Trace data processing
   - Identify data transfers
   - Document data storage

2. **Risk Assessment**
   - Identify privacy risks
   - Assess likelihood and impact
   - Evaluate existing controls
   - Recommend improvements

3. **Compliance Review**
   - Check legal requirements
   - Verify policy adherence
   - Review consent mechanisms
   - Assess data subject rights

4. **Stakeholder Consultation**
   - User feedback
   - Expert review
   - Legal counsel input
   - Management approval

---

## Contact Information

### Data Protection

**Data Protection Officer**
- Email: dpo@openchs.com
- Website: https://openchs.com/privacy

**Security Team**
- Email: security@openchs.com
- Emergency: Available 24/7 for critical incidents

**UNICEF Partnership**
- UNICEF Venture Fund: ventures@unicef.org
- Website: https://www.unicef.org/innovation/venturefund

---

## References

- OpenCHS Privacy Policy: https://openchs.com/privacy
- OpenCHS Security Documentation: https://docs.openchs.com/security
- UNICEF Data Protection: https://www.unicef.org/legal/data-protection
- GDPR Official Text: https://gdpr.eu
- Kenya Data Protection Act: http://kenyalaw.org/kl/fileadmin/pdfdownloads/Acts/2019/TheDataProtectionAct_No24of2019.pdf

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Review Schedule**: Annually or as needed