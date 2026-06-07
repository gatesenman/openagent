# Security

## Overview

OpenAgent implements defense-in-depth security across multiple layers: agent execution, code analysis, data protection, and compliance.

## Codex Security Engine

Enterprise-grade code security analysis engine with 8 capabilities:

### SAST (Static Application Security Testing)
- 12 detection rules covering 12 CWE categories
- Languages: Python, JavaScript, TypeScript, Java, Go, PHP
- Key detections: SQL Injection (CWE-89), XSS (CWE-79), Command Injection (CWE-78), SSRF (CWE-918), Insecure Deserialization (CWE-502)

### SCA (Software Composition Analysis)
- Scans package manifests: PyPI, npm, Maven, Go, Cargo
- CVE database matching for known vulnerabilities
- CVSS score thresholds for policy gating

### Secret Detection
- 17 regex patterns for hardcoded credentials
- Providers: AWS, GitHub PAT, Stripe, OpenAI, Anthropic, Google Cloud, Azure
- Formats: RSA keys, JWT tokens, database connection strings, generic passwords

### License Compliance
- 14 license types categorized: permissive, copyleft, restricted
- Policy-driven blocking for incompatible licenses
- SPDX identifier mapping

### IaC Security
- 7 rules for Docker, Kubernetes, Terraform
- Detects: root user in containers, `latest` tags, privileged mode, hardcoded secrets, `host` network mode

### SBOM (Software Bill of Materials)
- CycloneDX 1.5 format
- Package URL (PURL) identifiers
- SHA-256 hash verification

### Compliance Frameworks

| Framework | Controls | Status |
|-----------|----------|--------|
| SOC 2 | 7 | Active |
| ISO 27001 | 5 | Active |
| GDPR | 3 | Active |
| HIPAA | 3 | Active |
| PCI DSS | 5 | Planned |
| NIST 800-53 | 6 | Planned |

## OWASP LLM Top 10 (2025)

| ID | Risk | Protection |
|----|------|------------|
| LLM01 | Prompt Injection | Input sanitization, system prompt isolation, 6 detection rules |
| LLM02 | Insecure Output Handling | Output validation, encoding, 5 detection rules |
| LLM03 | Training Data Poisoning | Monitoring, data provenance tracking |
| LLM04 | Model Denial of Service | Token budget limits, rate limiting, 3 detection rules |
| LLM05 | Supply Chain Vulnerabilities | SCA scanning, SBOM generation, 5 detection rules |
| LLM06 | Sensitive Info Disclosure | Secret detection, PII filtering, 4 detection rules |
| LLM07 | System Prompt Leakage | Prompt isolation, output filtering, 3 detection rules |
| LLM08 | Vector/Embedding Weakness | Planned: embedding integrity checks |
| LLM09 | Misinformation | Anti-hallucination pipeline, 2 detection rules |
| LLM10 | Unbounded Consumption | Resource quotas, billing limits, 2 detection rules |

## Sandbox Security

- Per-session Docker container isolation
- Network isolation (agent cannot access host network)
- Dangerous command interception (14 patterns: `rm -rf`, `DROP TABLE`, `chmod 777`, `curl | bash`, etc.)
- Sensitive file protection (16 patterns: `.env`, `id_rsa`, `credentials.json`, etc.)
- Resource limits (CPU, memory, disk)

## Authentication & Authorization

- JWT-based authentication
- RBAC with 3 roles: Admin, Member, Viewer
- 14 fine-grained permissions
- API key support for service-to-service communication
- Audit logging for all operations
