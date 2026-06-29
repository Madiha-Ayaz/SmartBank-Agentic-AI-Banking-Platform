# Security Policy

SmartBank takes the security of our platform, our customers' data, and our users' privacy seriously. This document outlines our security practices, supported versions, and procedures for reporting vulnerabilities.

---

## Supported Versions

The SmartBank team provides security patches for the following versions:

| Version | Supported | Notes |
|---------|-----------|-------|
| 2.x (latest) | ✅ Supported | Active development — receives security patches within 48 hours of confirmation |
| 1.x | ⚠️ Limited | Critical patches only — customers must upgrade to 2.x for full support |
| < 1.0 | ❌ Unsupported | No security patches — upgrade immediately |

When a new major version is released, the previous major version enters a 90-day end-of-life (EOL) grace period during which only critical security patches are issued. After the EOL date, no further patches will be provided and users must upgrade.

---

## Vulnerability Reporting Process

### Reporting a Vulnerability

If you discover a security vulnerability in SmartBank, please report it privately. **Do not disclose the issue publicly** until we have had an opportunity to investigate and release a fix.

Send your report to: **security@smartbank.ai**

We aim to acknowledge receipt within **24 hours** and provide an initial assessment within **72 hours**.

### What to Include

To help us respond quickly, please include:

1. **Type of vulnerability** (e.g. SQL injection, authentication bypass, XXE, privilege escalation)
2. **Affected component** (specific module, file, endpoint, or version)
3. **Steps to reproduce** — a minimal, complete, and reproducible test case
4. **Proof of concept** — screenshots, logs, or code snippets demonstrating the issue
5. **Impact assessment** — what an attacker could achieve
6. **Your contact information** for follow-up questions

### PGP Encryption

For sensitive vulnerability reports, you may encrypt your message using our PGP key:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGdo7YwBEAD... (full key available at https://smartbank.ai/security/pgp-key.asc)
-----END PGP PUBLIC KEY BLOCK-----
```

- **Fingerprint:** `A1B2 C3D4 E5F6 7890 ABCD 1234 5678 90AB CDEF 0123`
- **Key ID:** `0xABCDEF0123456789`
- **Keyserver:** `https://keys.openpgp.org`

### Response Timeline

| Stage | Target Time | Description |
|-------|-------------|-------------|
| Acknowledgement | < 24 hours | Automated acknowledgement + assigned tracking ID |
| Initial Assessment | < 72 hours | Severity rating, affected versions, and mitigation plan |
| Patch Development | < 7 days (Critical) / < 30 days (High) / Next release (Medium/Low) | Fix development and internal testing |
| Patch Release | Coordinated with reporter | Public CVE disclosure + release of patched version |
| Public Acknowledgement | After patch release | Credit to reporter (if desired) in release notes |

### Severity Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **Critical** | Remote code execution, authentication bypass, data exfiltration, privilege escalation to admin | Patch within 7 days |
| **High** | Cross-site scripting (XSS) with impact, SQL injection, IDOR exposing customer PII, encryption bypass | Patch within 14 days |
| **Medium** | Limited XSS, CSRF, information disclosure (non-PII), rate-limiting bypass | Patch within 30 days |
| **Low** | Logging excessive data, missing security headers, minor information leakage | Patch within next release cycle |

---

## Security Best Practices Used in SmartBank

### Authentication & Authorization

- **OAuth 2.0 + PKCE** for all customer-facing authentication — no client secrets stored on devices
- **mTLS** required for all Card group API endpoints — client certificates verified against SmartBank CA
- **JWT tokens** with 15-minute TTL, automatically rotated refresh tokens
- **SPIFFE/SPIRE** workload identity for inter-service authentication within the service mesh
- Rate limiting per IP, per user, and per endpoint (Kong/Redis-backed)

### Encryption

- **Data in transit:** TLS 1.3 with `TLS_AES_256_GCM_SHA384` cipher suite — HSTS enabled with preload
- **Data at rest (DB):** AES-256-GCM with per-table keys stored in HashiCorp Vault, rotated daily
- **Data at rest (Object Store):** AES-256-SSE with KMS-managed CMK
- **Application-level PII:** Field-level envelope encryption using Google Tink — CNIC, phone, DOB fields encrypted before storage
- **Secrets:** All secrets (DB passwords, API keys, JWT signing keys) rotated automatically every 90 days via HashiCorp Vault with zero-downtime rotation

### Audit & Integrity

- **Immutable audit log:** SHA-256 hash chain — each entry contains the hash of the previous entry, making tampering detectable
- **Append-only storage:** Audit logs written to immutable buckets in MinIO Data Lake with WORM compliance
- **Cryptographic signatures:** All identity document update requests must be signed with the customer's RSA-SHA256 private key for non-repudiation
- **Request idempotency:** All mutating API endpoints require an `X-Idempotency-Key` header to prevent duplicate processing

### Input Validation & Output Encoding

- **API Gateway:** OWASP Core Rule Set v3.3 WAF (SQL injection, XSS, path traversal)
- **Content Security Policy:** `default-src 'none'; frame-ancestors 'none'; base-uri 'none'`
- **Response headers:** X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: no-referrer
- **PII masking:** All API responses mask sensitive data — phone numbers show last 4 digits, email addresses are partially masked, identity document numbers are truncated
- **Document sanitisation:** Uploaded document images are scanned for malware, validated for expected format, and run through fraud detection before processing

### Operational Security

- **Secrets management:** All credentials stored in HashiCorp Vault — never in code, config files, or environment dumps
- **Zero-trust networking:** Istio service mesh with mTLS for all inter-service communication. Workload identities via SPIFFE/SPIRE
- **CI/CD security:** GitHub Actions with OIDC-based access to cloud providers. All deployments require passing quality gates (lint, test, validate, build)
- **Container security:** All container images scanned with Trivy for CVEs before deployment. Base images are minimal (distroless where possible)
- **Dependency management:** Automated Dependabot alerts for vulnerable dependencies. Monthly review of all third-party libraries

### Compliance

- **PCI-DSS v4.0:** Card data never touches application servers. All payment tokens handled via PCI-certified token vault. Full audit logging of cardholder data environment (CDE) access
- **SBP (State Bank of Pakistan) Regulations:** Real-time transaction reporting. AML screening against UNSC sanctions list. Mandatory 5-year data retention in immutable data lake
- **PSD2 / Open Banking:** Strong Customer Authentication (SCA) via biometric + OTP. Consent management with revocation API. Third-party access logs available to customer
- **Data Privacy:** GDPR / PDPA compliance — right to erasure, data portability API, anonymization of analytical datasets

---

## Responsible Disclosure Policy

We ask that security researchers and reporters follow these guidelines:

1. **Report vulnerabilities privately** via `security@smartbank.ai` — do not post to public forums, issue trackers, or social media
2. **Allow reasonable time** for investigation and remediation — we commit to our response timeline above but may request additional time for complex issues
3. **Do not access or modify production data** — test against your own instance or our staging environment at `staging-api.smartbank.ai`
4. **Do not perform tests that cause denial of service** or disrupt production systems
5. **Do not use social engineering** against SmartBank employees, contractors, or customers
6. **Do not store or exfiltrate customer data** — use test accounts with synthetic data

### What We Commit

- We will acknowledge receipt of your report within 24 hours
- We will provide an initial severity assessment within 72 hours
- We will keep you informed of progress throughout the remediation process
- We will credit you in release notes and our security acknowledgements page (unless you prefer to remain anonymous)
- We will not pursue legal action against researchers who follow this disclosure policy

### Hall of Fame

We maintain a security researcher hall of fame on our website at `https://smartbank.ai/security/hall-of-fame`. If you would like to be included, let us know when you submit your report.

---

*This security policy is reviewed and updated quarterly. Last updated: June 2026.*

*For questions about this policy, contact security@smartbank.ai.*
