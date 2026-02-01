# Security Policy

## Overview

Vylt is a **local‑first, offline‑only encryption system**. It is designed to ensure that **only the user controls their data and keys**. There is no key recovery, no cloud dependency, and no backdoor.

If a password is lost, the data is **cryptographically unrecoverable by design**.

This document explains Vylt’s security guarantees, threat model, limitations, and responsible disclosure process.

---

## Core Security Principles

* 🔐 **Zero‑Knowledge**: Vylt never stores or transmits passwords, keys, or plaintext data.
* 📴 **Offline‑Only**: No network access is required or used at any stage.
* 🧠 **User‑Owned Keys**: Encryption keys exist only in memory during runtime.
* 🔒 **Fail‑Closed Design**: Any corruption, truncation, or wrong password causes hard failure.
* 🧩 **Deterministic Parsing**: Archive structure is strictly defined and verified.

---

## Encryption Architecture

Vylt uses **three independent encryption layers**, all executed locally:

### Layer 1 – Vylt Archive Layer

* Custom binary container format
* Strict header with:

  * Magic (`VYLT`)
  * Version
  * Archive ID
  * Metadata length
  * SHA‑256 hashes of encrypted metadata and payload
* Prevents file confusion, tampering, and misalignment

### Layer 2 & 3 – CIPH Crypto Engine

* Streaming ChaCha20‑based encryption
* Multiple internal cryptographic stages per stream
* Applied separately to:

  * Metadata (optional, via shield)
  * Payload (always)

All encryption happens **before disk write**.

---

## Metadata Shield (Sealed Metadata)

When `--seal-meta` is enabled:

* File paths and structure are encrypted
* Metadata size becomes variable
* Encrypted metadata length is stored in header
* Metadata is decrypted independently from payload

### Security Properties

* Prevents directory/file name leakage
* Allows listing only with correct metadata password
* Does **not** protect file contents (payload password does)

---

## Password Model

Vylt supports two passwords:

1. **Data Password** (mandatory)

   * Encrypts file contents
   * **If lost: data is permanently unrecoverable**

2. **Metadata Password** (optional)

   * Encrypts file names and structure
   * If lost, file paths cannot be recovered

Passwords are:

* Never stored
* Never logged
* Never cached
* Never transmitted

---

## Irreversibility Warning ⚠️

> **There is no recovery mechanism.**

* Lost data password → **files are gone forever**
* Lost metadata password → **structure is unreadable**
* Developers **cannot** help recover data

Users are strongly advised to:

* Store passwords securely
* Verify passwords before encryption
* Use configuration‑based automation for workflows

---

## Integrity & Tamper Detection

Vylt enforces integrity using:

* SHA‑256 hash of encrypted metadata
* SHA‑256 hash of encrypted payload
* Header verification before decryption

Any of the following will cause failure:

* Modified bytes
* Truncated files
* Wrong passwords
* Reordered archive parts

---

## Multi‑Part Archive Safety

When archives are split:

* Each part includes archive ID and index
* Renaming or modifying part names may prevent discovery
* Parts must remain unchanged and colocated

⚠️ **Do not rename or edit `.vylt` files manually**

---

## Performance & Thread Safety

* Encryption is CPU‑bound
* Recommended threads: **≤ number of CPU cores**
* Optimal default: **4 threads**

Using excessive threads:

* Does not increase security
* May reduce stability or performance

---

## Threat Model

Vylt protects against:

* Disk theft
* Cloud compromise
* Unauthorized access
* Metadata leakage (with shield)
* Accidental corruption

Vylt does **not** protect against:

* Malware running with user privileges
* Keyloggers
* Compromised operating systems
* User‑chosen weak passwords

---

## Responsible Disclosure

If you discover a security vulnerability:

* **Do not open a public issue**
* Contact the maintainer directly

GitHub: [https://github.com/ankit-chaubey](https://github.com/ankit-chaubey)
Email: m DOT ankitchaubey AT gmail DOT com
Please include:

* Vylt version
* Reproduction steps
* Impact analysis

---

## Dependencies

* ciph encryption engine

  * Repository: [https://github.com/ankit-chaubey/ciph](https://github.com/ankit-chaubey/ciph)
  * Written in C
  * Used via `ctypes`

Vylt does not implement custom cryptographic primitives.

---

## Final Note

Vylt is built for users who value **sovereignty over convenience**.

If privacy matters to you, Vylt gives you the power — and the responsibility — to protect your data.

🔏 **Your data. Your keys. Your control.**
