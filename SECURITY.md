# Security Policy

## Supported Versions

This project follows a **rolling development model**.

Only the **latest version on the `main` branch** is actively supported with
security updates.

| Version / Branch | Supported |
| ---------------- | --------- |
| `main` (latest)  | ✅ Yes    |
| Older commits    | ❌ No     |
| Forked versions  | ❌ No     |

Users are strongly encouraged to stay up to date with the latest changes.

---

## Security Principles

Jarvis-IA is designed with the following security principles in mind:

- **Local-first architecture** (no mandatory external APIs)
- **No telemetry or data exfiltration**
- **Explicit permission control** for actions (Permission Gate)
- **Clear separation** between core logic, providers, and skills
- **Fail-safe defaults** (mock mode, restricted execution)

The project intentionally avoids automatic execution of sensitive actions
without explicit approval.

---

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to report

- **Do not open a public issue** for security vulnerabilities.
- Use **GitHub Security Advisories** (preferred), or
- Contact the maintainer directly via private communication.

When reporting, please include:
- A clear description of the issue
- Steps to reproduce (if applicable)
- Potential impact
- Environment details (OS, Python version, configuration)

---

## Response Timeline

You can expect:
- **Initial acknowledgement** within **72 hours**
- **Status update** within **7 days**
- A fix or mitigation plan if the issue is confirmed

Timelines may vary depending on severity and complexity.

---

## Scope

This security policy applies to:
- The backend codebase
- Local LLM provider integrations (e.g. Ollama)
- Permission and approval mechanisms
- Memory and skill execution logic

It does **not** cover:
- User-modified deployments
- Third-party forks
- External models or binaries (e.g. Ollama itself)

---

## Responsible Disclosure

We value responsible disclosure and collaboration.
Security researchers acting in good faith will be acknowledged when appropriate.

Thank you for helping keep Jarvis-IA secure.
