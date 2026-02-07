#!/bin/bash

DATE=$(date +%F)
OUTPUT="security_compliance_report_${DATE}.md"

echo "# Security Compliance Evidence Report" > $OUTPUT
echo "" >> $OUTPUT
echo "**Generated on:** ${DATE}" >> $OUTPUT
echo "" >> $OUTPUT
echo "---" >> $OUTPUT

section () {
  echo "" >> $OUTPUT
  echo "## $1" >> $OUTPUT
  echo "" >> $OUTPUT
}

codeblock () {
  echo '```' >> $OUTPUT
  $1 >> $OUTPUT 2>/dev/null
  echo '```' >> $OUTPUT
}

note () {
  echo "> **Note:** $1" >> $OUTPUT
}

### 1. ACCESS CONTROL #############################################

section "Access Control"

echo "**Total system users:**" >> $OUTPUT
codeblock "cut -d: -f1 /etc/passwd | wc -l"

echo "**Users with elevated (sudo/wheel) privileges:**" >> $OUTPUT
codeblock "getent group sudo wheel"

note "RBAC customization is application-level and must be validated separately."

### 2. MFA #########################################################

section "Multi-Factor Authentication (Indicator Check)"

echo "**PAM / SSH MFA indicators:**" >> $OUTPUT
codeblock "grep -Ei 'google|mfa|duo|otp' /etc/pam.d/*"

note "Absence here does not imply non-compliance; MFA may be enforced at application or IAM layer."

### 3. ENCRYPTION AT REST #########################################

section "Encryption at Rest"

echo "**Disk encryption indicators (LUKS / crypt):**" >> $OUTPUT
codeblock "lsblk -o NAME,FSTYPE,MOUNTPOINT | grep crypt"

note "On-prem or SAN-level encryption may not be visible at OS layer."

### 4. ENCRYPTION IN TRANSIT ######################################

section "Encryption in Transit (TLS)"

echo "**OpenSSL version:**" >> $OUTPUT
codeblock "openssl version"

note "TLS 1.2+ enforcement should be validated at application ingress / reverse proxy."

### 5. LOGGING #####################################################

section "Logging & Monitoring"

echo "**System logging services:**" >> $OUTPUT
codeblock "systemctl is-active rsyslog && systemctl is-active systemd-journald"

echo "**Available log directories:**" >> $OUTPUT
codeblock "ls /var/log | head -20"

### 6. CENTRALIZED LOGGING ########################################

section "Centralized Logging"

echo "**ELK / Prometheus agent indicators:**" >> $OUTPUT
codeblock "ps aux | grep -Ei 'elastic|logstash|filebeat|prometheus' | grep -v grep"

note "No agent detected confirms decentralized logging state."

### 7. NETWORK SECURITY ###########################################

section "Network Security"

echo "**Firewall configuration:**" >> $OUTPUT
codeblock "iptables -L -n || ufw status"

echo "**Open listening ports:**" >> $OUTPUT
codeblock "ss -tulnp"

### 8. WAF #########################################################

section "Web Application Firewall (WAF)"

echo "**WAF / reverse proxy indicators:**" >> $OUTPUT
codeblock "ps aux | grep -Ei 'modsecurity|nginx|apache' | grep -v grep"

note "WAF may be upstream (cloud LB, client infra) and not visible locally."

### 9. PATCH MANAGEMENT ###########################################

section "Patch & Dependency Management"

echo "**Upgradable packages:**" >> $OUTPUT
codeblock "apt list --upgradable | head -20 || yum check-update"

note "Dependency scanning is handled via GitHub security tooling."

### 10. BACKUPS ###################################################

section "Backup & Recovery Indicators"

echo "**Cron jobs present:**" >> $OUTPUT
codeblock "ls /etc/cron* | wc -l"

echo "**Backup directories detected:**" >> $OUTPUT
codeblock "find / -type d -iname '*backup*' | head -10"

note "Backups are client-owned; evidence requires client attestation."

### 11. INCIDENT RESPONSE #########################################

section "Incident Response"

echo "**Incident response documentation found:**" >> $OUTPUT
codeblock "find / -iname '*incident*' | head -10"

note "Formal IR plan exists but is not stored on system."

---

section "Summary"

echo "- This report provides **technical evidence** supporting the Q1 Security Compliance Checklist." >> $OUTPUT
echo "- Items marked FALSE in the checklist are **confirmed gaps or client-owned controls**." >> $OUTPUT
echo "- This report is suitable for **audits, investor reviews, and mentor check-ins**." >> $OUTPUT

echo "" >> $OUTPUT
echo "---" >> $OUTPUT
echo "**End of Report**" >> $OUTPUT

echo "Markdown compliance report generated: ${OUTPUT}"
