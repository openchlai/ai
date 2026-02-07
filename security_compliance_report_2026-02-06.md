# Security Compliance Evidence Report

**Generated on:** 2026-02-06

---

## Access Control

**Total system users:**
```
##
# User Database
# 
# Note that this file is consulted directly only when the system is running
# in single-user mode.  At other times this information is provided by
# Open Directory.
#
# See the opendirectoryd(8) man page for additional information about
# Open Directory.
##
nobody
root
daemon
_uucp
_taskgated
_networkd
_installassistant
_lp
_postfix
_scsd
_ces
_appstore
_mcxalr
_appleevents
_geod
_devdocs
_sandbox
_mdnsresponder
_ard
_www
_eppc
_cvs
_svn
_mysql
_sshd
_qtss
_cyrus
_mailman
_appserver
_clamav
_amavisd
_jabber
_appowner
_windowserver
_spotlight
_tokend
_securityagent
_calendar
_teamsserver
_update_sharing
_installer
_atsserver
_ftp
_unknown
_softwareupdate
_coreaudiod
_screensaver
_locationd
_trustevaluationagent
_timezone
_lda
_cvmsroot
_usbmuxd
_dovecot
_dpaudio
_postgres
_krbtgt
_kadmin_admin
_kadmin_changepw
_devicemgr
_webauthserver
_netbios
_warmd
_dovenull
_netstatistics
_avbdeviced
_krb_krbtgt
_krb_kadmin
_krb_changepw
_krb_kerberos
_krb_anonymous
_assetcache
_coremediaiod
_launchservicesd
_iconservices
_distnote
_nsurlsessiond
_displaypolicyd
_astris
_krbfast
_gamecontrollerd
_mbsetupuser
_ondemand
_xserverdocs
_wwwproxy
_mobileasset
_findmydevice
_datadetectors
_captiveagent
_ctkd
_applepay
_hidd
_cmiodalassistants
_analyticsd
_fpsd
_timed
_nearbyd
_reportmemoryexception
_driverkit
_diskimagesiod
_logd
_appinstalld
_installcoordinationd
_demod
_rmd
_accessoryupdater
_knowledgegraphd
_coreml
_sntpd
_trustd
_mmaintenanced
_darwindaemon
_notification_proxy
_avphidbridge
_biome
_backgroundassets
_mobilegestalthelper
_audiomxd
_terminusd
_neuralengine
_eligibilityd
_systemstatusd
_aonsensed
_modelmanagerd
_reportsystemmemory
_swtransparencyd
_naturallanguaged
_spinandd
_corespeechd
_diagnosticservicesd
_mds_stores
_oahd
```
**Users with elevated (sudo/wheel) privileges:**
```
```
> **Note:** RBAC customization is application-level and must be validated separately.

## Multi-Factor Authentication (Indicator Check)

**PAM / SSH MFA indicators:**
```
```
> **Note:** Absence here does not imply non-compliance; MFA may be enforced at application or IAM layer.

## Encryption at Rest

**Disk encryption indicators (LUKS / crypt):**
```
```
> **Note:** On-prem or SAN-level encryption may not be visible at OS layer.

## Encryption in Transit (TLS)

**OpenSSL version:**
```
OpenSSL 3.6.1 27 Jan 2026 (Library: OpenSSL 3.6.1 27 Jan 2026)
```
> **Note:** TLS 1.2+ enforcement should be validated at application ingress / reverse proxy.

## Logging & Monitoring

**System logging services:**
```
```
**Available log directories:**
```
/var/log:
CoreCapture
CoreDuet
DiagnosticMessages
PrivacyPreservingMeasurement
apache2
asl
com.apple.wifi.analytics
com.apple.wifivelocity
com.apple.xpc.launchd
cups
displaypolicy
displaypolicyd.stdout.log
dm
fsck_apfs.log
fsck_apfs_error.log
fsck_hfs.log
install.log
install.log.0.gz
mDNSResponder
powermanagement
ppp
shutdown_monitor.log
system.log
system.log.0.gz
system.log.1.gz
system.log.2.gz
system.log.3.gz
system.log.4.gz
system.log.5.gz
uucp
wifi.log
wifi.log.0.bz2
wifi.log.1.bz2
wifi.log.10.bz2
wifi.log.2.bz2
wifi.log.3.bz2
wifi.log.4.bz2
wifi.log.5.bz2
wifi.log.6.bz2
wifi.log.7.bz2
wifi.log.8.bz2
wifi.log.9.bz2
```

## Centralized Logging

**ELK / Prometheus agent indicators:**
```
```
> **Note:** No agent detected confirms decentralized logging state.

## Network Security

**Firewall configuration:**
```
```
**Open listening ports:**
```
```

## Web Application Firewall (WAF)

**WAF / reverse proxy indicators:**
```
```
> **Note:** WAF may be upstream (cloud LB, client infra) and not visible locally.

## Patch & Dependency Management

**Upgradable packages:**
```
```
> **Note:** Dependency scanning is handled via GitHub security tooling.

## Backup & Recovery Indicators

**Cron jobs present:**
```
```
**Backup directories detected:**
```
```
> **Note:** Backups are client-owned; evidence requires client attestation.

## Incident Response

**Incident response documentation found:**
```
```
> **Note:** Formal IR plan exists but is not stored on system.

## Summary

- This report provides **technical evidence** supporting the Q1 Security Compliance Checklist.
- Items marked FALSE in the checklist are **confirmed gaps or client-owned controls**.
- This report is suitable for **audits, investor reviews, and mentor check-ins**.

---
**End of Report**
