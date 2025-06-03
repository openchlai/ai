# 🔒 Security Policy

## 🎯 Supported Versions

We provide security updates for the following versions:

| Version   | Supported          |
|-----------|---------------------|
| `1.x`     | ✅ Security patches |
| `<1.0`    | ❌ No longer supported |

---

## 🔍 Reporting a Vulnerability

We take security seriously! If you find a vulnerability, **please DO NOT open a public issue**. Instead, follow these steps:

1. 📩 **Email us:** Send an email to **[your-security-email@example.com]** with:
   - A detailed description of the vulnerability.
   - Steps to reproduce the issue (if possible).
   - Any potential fixes or recommendations (optional).

2. 🔒 **Encrypt the report (optional):**  
   If you prefer, you can encrypt your email using our PGP key (provide your public key or link to it).

3. 🛠️ **Response Time:**  
   We aim to respond to security reports **within 48 hours** and resolve valid vulnerabilities **within 7 days** — depending on severity.

4. 🏅 **Acknowledgment:**  
   We appreciate responsible disclosures. With your consent, we'll publicly acknowledge you in the project's release notes.

---

## 🔧 Security Best Practices

We recommend contributors and users follow these best practices:

- ✅ **Keep Django and dependencies updated.**
- ✅ **Use environment variables** for sensitive data like API keys and passwords.
- ✅ **Avoid running the project with `DEBUG=True` in production.**
- ✅ **Regularly audit third-party packages** for vulnerabilities (`pip audit`).
- ✅ **Enable HTTPS** in production environments.

---

## 🤝 Credits

Special thanks to all contributors and security researchers who help keep this project safe!

