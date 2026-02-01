# Contributing to Vylt

Thank you for your interest in contributing to **Vylt – Vault Encryption Engine**. 🎉
Vylt is a **privacy-first, security-critical** project. Contributions are welcome, but they must follow strict engineering, security, and ethical standards.

---

## Philosophy

Vylt exists because:

* Users deserve **full control over their data**
* Encryption must remain **local, transparent, and trustless**
* There must be **no backdoors, telemetry, or silent data flow**

Every contribution must respect these principles.

---

## What You Can Contribute

You are welcome to contribute in the following areas:

* 🛠️ Bug fixes (especially edge cases and platform issues)
* 🔐 Security hardening and correctness improvements
* ⚙️ Performance optimizations (CPU, memory, IO)
* 📦 Packaging improvements (PyPI, Termux, Linux)
* 🧪 Tests, benchmarks, and reproducibility scripts
* 📖 Documentation (README, specs, diagrams)
* 💡 Feature proposals (via discussion first)

---

## What Will NOT Be Accepted

The following will be rejected immediately:

* ❌ Any form of backdoor, hidden access, or key leakage
* ❌ Telemetry, analytics, or network calls without explicit opt-in
* ❌ Weakening cryptography or security assumptions
* ❌ Obfuscation meant to hide behavior from users
* ❌ Copy-pasted crypto code without clear provenance

Vylt is **user-trust software**. Violating trust is unacceptable.

---

## Contribution Workflow

### 1. Fork the Repository

```bash
git clone https://github.com/ankit-chaubey/vylt.git
cd vylt
```

Create a feature branch:

```bash
git checkout -b feature/your-change
```

---

### 2. Development Guidelines

* Follow existing project structure
* Keep code **readable and explicit** over clever
* Prefer clarity over abstraction
* Avoid global state
* Handle errors explicitly

For encryption paths:

* Never reuse buffers incorrectly
* Never assume fixed sizes unless defined in the spec
* Always validate lengths before reading/writing

---

### 3. Testing Requirements

All changes must pass:

* ✅ No-shield encryption/decryption
* ✅ Shielded (sealed metadata) encryption/decryption
* ✅ Multi-file and nested directory encryption
* ✅ Integrity verification (hash match)
* ✅ Diagnostics & benchmark (`vylt setup`)

Run the full test suite:

```bash
chmod +x vylt_test.sh
./vylt_test.sh
```

If tests are missing for your change, **add them**.

---

### 4. Commit Standards

* Write clear, meaningful commit messages

Examples:

```
fix: correct metadata length handling in shield mode
perf: reduce temporary file IO during encryption
docs: clarify sealed metadata behavior
```

Avoid vague messages like:

```
update
fix bug
changes
```

---

### 5. Pull Request Process

Before opening a PR:

* Rebase on latest `main`
* Ensure all tests pass
* Update documentation if behavior changes
* Clearly explain *why* the change is needed

Your PR description **must include**:

* Problem statement
* Solution overview
* Security impact (explicitly stated)
* Testing performed

PRs without security consideration will not be merged.

---

## Security Contributions

If you find:

* Vulnerabilities
* Cryptographic weaknesses
* Memory safety issues
* Integrity bypasses

**DO NOT open a public issue.**
Follow the process in `SECURITY.md` for responsible disclosure.

---

## License & Attribution

By contributing:

* You agree your work is licensed under **Apache License 2.0**

* You confirm the code is **your own work** or properly attributed

* You agree to keep credit to:

* Vylt project

* @ankit-chaubey

* ciph engine (where applicable)

---

## Maintainer Authority

The maintainer reserves the right to:

* Request changes or clarification
* Reject contributions that conflict with project goals
* Prioritize security and correctness over features

This is not a rejection of contributors — it is protection of users.

---

## Final Note

Vylt is not just software — it is a **trust contract**.

If you contribute, you are helping people protect:

* Personal files
* Intellectual work
* Private memories
* Professional data

Take that responsibility seriously. 🔐

---

**Project:** Vylt – Vault Encryption Engine
**Maintainer:** @ankit-chaubey
**Version:** v0.1.0
