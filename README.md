# 🔐 Vylt — Vault/Media Encryption Engine

 - **Version:** [v0.1.0](https://pypi.org/project/vylt)
 - **Author:** [@ankit-chaubey]((https://github.com/ankit-chaubey)
 - **License:** [Apache-2.0](https://github.com/ankit-chaubey/vylt/blob/main/LICENSE)

---

[![PyPI](https://img.shields.io/pypi/v/vylt.svg)](https://pypi.org/project/vylt/)
[![Downloads](https://img.shields.io/pypi/dm/vylt.svg)](https://pypi.org/project/vylt/)
[![Python](https://img.shields.io/pypi/pyversions/vylt.svg)](https://pypi.org/project/vylt/)
[![CI](https://github.com/ankit-chaubey/vylt/actions/workflows/vylt-cli.yml/badge.svg)](https://github.com/ankit-chaubey/vylt/actions/workflows/vylt-cli.yml)
[![License](https://img.shields.io/github/license/ankit-chaubey/vylt)](https://github.com/ankit-chaubey/vylt/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/tag/ankit-chaubey/vylt?label=release)](https://github.com/ankit-chaubey/vylt/releases)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-blue)](#)
[![Crypto](https://img.shields.io/badge/crypto-AES--256--GCM%20%7C%20ChaCha20--Poly1305-blue)](#)
---

## 🧠 Why Vylt Exists

In a world where **data privacy is increasingly opaque**, Vylt was created from a simple belief:

> **Your data should never leave your control — not even for encryption.**

Vylt is a **local-first, offline-only vault encryption system** designed for people who:

* do not trust third‑party services with raw data
* want cryptographic guarantees, not marketing promises
* prefer tools that are honest about irreversible security
* complete gallery and folder support with multi-layer encryption.
* ​all encryption happens directly on your device—zero internet exposure.
* fully secured for protecting your private photos, videos, and personal data.

This project was built originally for personal use and later shared so others can **preserve privacy with confidence**.

---

## 🧱 Security Architecture (3‑Layer Protection)

Vylt uses **three distinct cryptographic layers**, all executed **entirely on your device**:

### 🔐 Layer 1 — Vylt Container Layer

* Custom archive format (`.vylt`)
* Secure header with:

  * archive ID
  * part number & total parts
  * metadata length
  * SHA‑256 integrity hashes
* Optional **metadata shielding**

### 🔒 Layer 2 & 3 — ciph secure encryption engine

Powered by [**ciph**](https://github.com/ankit-chaubey/ciph) (C-based SHA-256/ChaCha20-Poly1305 streaming engine):

* Two internal encryption stages
* Streaming, FD-safe, constant-memory
* No temp plaintext leaks

📌 **Important:** Each ciph layer itself contains multiple cryptographic rounds. All encryption happens **offline** — Vylt never connects to the internet.

**Projects:**

* Vylt: [https://github.com/ankit-chaubey/vylt](https://github.com/ankit-chaubey/vylt)
* ciph: [https://github.com/ankit-chaubey/ciph](https://github.com/ankit-chaubey/ciph)

---

## 🗄️ Metadata Shield (Optional)

When `--seal-meta` is enabled:

* File names & folder structure are encrypted separately
* Metadata size becomes **variable** (stored in header)
* Archive still lists correctly after decrypting metadata

Without shield:

* Metadata remains visible
* Faster listing
* Same data security level

---

## ⚠️ CRITICAL SECURITY WARNINGS

### 🚨 Password Loss = Permanent Data Loss

* **If you forget the *data password*** → your files are **gone forever**
* Metadata password cannot recover encrypted data
* No backdoors. No recovery. No master key.

➡️ **Write your password down. Store it safely. Verify twice.**

---

### ⚠️ Do NOT Rename or Modify `.vylt` Parts

* Archive ID & part numbering are required for recovery
* Renaming or altering filenames may break multi‑part discovery

---

### ⚠️ Threading Guidance

* Default: `1` thread (safe)
* Recommended maximum: **4 threads**
* Using more threads than your system supports may:

  * slow encryption
  * increase memory pressure
  * reduce stability

---

## 📦 Installation

```bash
pip install vylt
```

Or editable (development):

```bash
pip install -e .
```

PyPI: [https://pypi.org/project/vylt/](https://pypi.org/project/vylt/)

---

## 🚀 Usage

### Encrypt (no metadata shield)

```bash
vylt encrypt myfolder
```

### Encrypt with metadata shield

```bash
vylt encrypt myfolder --seal-meta
```

### List archive contents

```bash
vylt list myfolder.*.vylt
```

### Decrypt archive

```bash
vylt decrypt myfolder.*.vylt
```

---

## 🧪 Automated Testing & Integrity

Vylt includes full workflow tests:

* single file
* large files
* nested folders
* shielded & unshielded metadata
* SHA‑256 integrity verification

Tests run via GitHub Actions on every push.

---

## 🔧 Configuration

Vylt reads config from:

```
~/.vylt.json
```

Example:

```json
{
  "threads": 2,
  "reuse_data_password_for_meta": true,
  "max_password_attempts": 5,
  "password_from_env": "VYLT_PASSWORD"
}
```

This allows **CI / workflow automation without prompts**.

---

## 🧭 Roadmap

Planned future work:

* ☁️ remote cloud sync (encrypted blobs only)
* ⏱️ scheduled backups
* 📱 full‑device encryption mode
* 📚 formal archive specification docs

---

## 🧑‍💻 Author & Developer

* [**VYLT**](https://pypi.org/project/vylt) — design, format, CLI, orchestration
  Author: Ankit Chaubey [(@ankit-chaubey)](https://github.com/ankit-chaubey)

* Powered By [**CIPH**](https://pypi.org/project/ciph) — cryptographic encryption engine


---

## 🌟 Support & Community

If this project helped you:

* ⭐ Star the repo
* 🍴 Fork it
* 🔗 Share with privacy‑conscious friends

If you modify or redistribute:

* follow the Apache‑2.0 license
* **keep credit and repository links**

---

## 📜 License

Apache License 2.0

Copyright © 2026 Ankit Chaubey

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

---

## ⚠️ Disclaimer

This tool uses strong cryptography.

If you forget your password, **your data cannot be recovered**.

Use responsibly.

---

> This project exists because privacy matters.
> Your data. Your keys. Your control. 🔏
