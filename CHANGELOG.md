# CHANGELOG

All notable changes to this project will be documented in this file.

This project follows **Semantic Versioning** and prioritizes
**deterministic security, correctness, and zero-leak behavior**.

---

## [1.0.0] — 2026-02-26

### 🎉 First Stable Release

This release marks **Vylt v1.0.0**, the first **stable, production-ready**
version of the secure archive engine powered by **CIPH**.

After extensive real-world testing (large files, selective extraction,
sealed metadata, and integrity verification), Vylt is now considered
**stable and reliable**.

---

### 🔐 Security & Cryptography

* Integrated **CIPH streaming encryption engine**
* Deterministic encryption & decryption (no chunk-size dependency)
* Correct handling of:

  * wrong password
  * wrong cipher
  * corrupted archives
* Zero plaintext leakage during all operations
* Encrypted metadata support (`--seal-meta`)
* Safe password handling with optional environment variable support

---

### 📦 Archive Features

* Encrypt files **or full directory trees**
* Automatic archive ID generation
* Multi-part archive support (parallel mode)
* Original directory structure preserved on restore
* Archive filename can be renamed safely without data loss
* Embedded original filenames restored on decrypt

---

### 🎯 Selective Extraction

* Extract only selected paths using glob patterns:

  * `--only "dir/*"`
  * `--only "*.jpg"`
* Selective extraction does **not** decrypt or extract unrelated files
* Fully tested for nested directories

---

### ⚙️ CLI Improvements

* Clean, colorful, readable CLI output
* Progress bars for encryption & decryption
* Clear success / failure indicators
* Deterministic exit behavior (script-safe)
* Sci-art ASCII banner on startup
* Stable command structure:

  * `encrypt`
  * `decrypt`
  * `list`
  * `info`
  * `setup`

---

### 🧪 Testing & Reliability

* Full end-to-end integration test suite:

  * encryption → rename → decrypt → integrity check
  * selective extraction
  * sealed metadata behavior
  * diagnostics & benchmark
* Tested with:

  * small files
  * large files (GB-scale)
  * mismatched chunk sizes
* Memory usage verified to stay low and bounded

---

### 📊 Diagnostics & Benchmarking

* `vylt setup` runs:

  * system diagnostics
  * filesystem checks
  * libciph linkage verification
  * streaming encryption benchmark
* Reports real encryption/decryption throughput

---

### 🧹 Safety & Cleanup

* Secure temp file handling
* Automatic cleanup on SIGINT / SIGTERM
* Optional secure wipe of source data (`--wipe`)

---

### 🔄 Internal Refactors

* Stable header format
* Clean separation of:

  * crypto
  * archive logic
  * CLI
  * diagnostics
* Robust error propagation from C → Python → CLI

---

### 🛑 Breaking Changes

* **None**
  This is the first stable release.

---

### 📌 Notes

* Vylt is designed for **Linux / Unix-like systems**
* Requires `libciph.so` available at runtime
* Optimized for large media archives and backups

---

**Status:** ✅ Stable
**Recommended for production use**
