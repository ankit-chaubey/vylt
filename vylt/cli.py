import argparse
import os
import glob
import getpass
import tempfile
import struct
import shutil
import time
import threading
import signal
import sys
from contextlib import contextmanager
from tqdm import tqdm

from .config import VyltConfig
from .parallel import encrypt_parallel
from .selective import extract
from .wipe import wipe_tree
from .diagnostics import run_diagnostics
from .header import HEADER_SIZE, unpack_outer
from .ciphwrap import decrypt_file
from .fileprogress import track_progress


# =========================
# 🎨 COLOR + SCI ART SYSTEM
# =========================
class C:
    R = "\033[0m"
    G = "\033[92m"
    Y = "\033[93m"
    C = "\033[96m"
    M = "\033[95m"
    E = "\033[91m"
    B = "\033[94m"
    D = "\033[90m"


BANNER = f"""
{C.M}╔══════════════════════════════════════════╗
║   V Y L T  —  Secure Archive Engine      ║
║   Powered by CIPH (Streaming Crypto)     ║
║   Zero-leak • Fast • Deterministic       ║
╚══════════════════════════════════════════╝{C.R}
"""


# =========================
# 🧹 TEMP CLEANUP HANDLING
# =========================
_PENDING = []


def _cleanup(sig=None, frame=None):
    for p in list(_PENDING):
        try:
            if os.path.exists(p):
                os.unlink(p)
        except Exception:
            pass
    sys.exit(130 if sig else 1)


signal.signal(signal.SIGINT, _cleanup)
signal.signal(signal.SIGTERM, _cleanup)


@contextmanager
def safe_temp(suffix=""):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    _PENDING.append(path)
    try:
        yield path
    finally:
        try:
            if os.path.exists(path):
                os.unlink(path)
        finally:
            if path in _PENDING:
                _PENDING.remove(path)


# =========================
# 🔐 PASSWORD HANDLING
# =========================
def _env_password():
    cfg = VyltConfig.load()
    env = cfg.get("password_from_env") or "VYLT_PASSWORD"
    v = os.getenv(env)
    return v.encode() if v else None


def ask_password(prompt, confirm=False):
    env_pwd = _env_password()
    if env_pwd:
        print(f"{C.D}• Using password from environment{C.R}")
        return env_pwd

    p = getpass.getpass(prompt).encode()
    if confirm:
        if p != getpass.getpass("Confirm: ").encode():
            raise SystemExit(f"{C.E}Password mismatch{C.R}")
    return p


def retry_password(prompt):
    env_pwd = _env_password()
    if env_pwd:
        print(f"{C.D}• Using password from environment{C.R}")
        return env_pwd

    for _ in range(5):
        p = getpass.getpass(prompt)
        if p:
            return p.encode()
    raise SystemExit(f"{C.E}Too many attempts{C.R}")


# =========================
# 📦 ARCHIVE HELPERS
# =========================
def find_parts(path):
    base = os.path.basename(path)
    parts = base.rsplit(".", 3)
    if len(parts) < 3:
        return [path]
    root, aid = parts[0], parts[1]
    if not all(c in "0123456789abcdef" for c in aid):
        return [path]
    return sorted(glob.glob(f"{root}.{aid}.*.vylt")) or [path]


def decrypt_part(part, password, outdir, only):
    with safe_temp() as payload, safe_temp() as tarout:
        with open(part, "rb") as f:
            hdr = f.read(HEADER_SIZE)
            _, _, _, _, _, _, meta_len, _, _ = unpack_outer(hdr)
            f.seek(HEADER_SIZE + meta_len)
            with open(payload, "wb") as o:
                shutil.copyfileobj(f, o)

        total = os.path.getsize(payload)
        stop = threading.Event()

        with tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=f"{C.C}🔓 Decrypting{C.R}",
            dynamic_ncols=True,
        ) as bar:
            t = threading.Thread(
                target=track_progress,
                args=(tarout, bar, stop),
                daemon=True,
            )
            t.start()

            t0 = time.perf_counter()
            decrypt_file(payload, tarout, password)
            t1 = time.perf_counter()

            stop.set()
            bar.update(bar.total - bar.n)

        mb = total / (1024 * 1024)
        dt = t1 - t0

        print(f"{C.G}✔ Decrypted{C.R} {mb:.2f} MB in {dt:.2f}s ({mb/dt:.2f} MB/s)")
        print(f"{C.B}→ Extracting{C.R}")

        with open(tarout, "rb") as tarf:
            extract(tarf, only, outdir)

        print(f"{C.G}✔ Restored to{C.R} {outdir}\n")


# =========================
# 🚀 CLI ENTRYPOINT
# =========================
def main():
    print(BANNER)

    p = argparse.ArgumentParser(
        prog="vylt",
        description=f"{C.C}Vylt — Secure archival encryption with CIPH{C.R}",
        epilog=f"""
{C.M}Examples:{C.R}

  vylt encrypt photos/
  vylt encrypt secrets/ --seal-meta
  vylt decrypt backup.abc123.vylt
  vylt decrypt archive.vylt --only "docs/*" --out restored/
  vylt setup

{C.D}Tip:{C.R} Use VYLT_PASSWORD env var for non-interactive use.
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    s = p.add_subparsers(dest="cmd", required=True)

    s.add_parser("setup", help="🔧 Run system diagnostics & benchmark")
    s.add_parser("info", help="📦 Show archive metadata").add_argument("file")
    s.add_parser("list", help="📄 List files inside archive").add_argument("file")

    e = s.add_parser("encrypt", help="🔐 Encrypt file or directory")
    e.add_argument("path", help="Path to file or directory")
    e.add_argument("--threads", help="Parallel shards")
    e.add_argument("--seal-meta", action="store_true", help="Hide filenames")
    e.add_argument("--wipe", action="store_true", help="Securely wipe source")

    d = s.add_parser("decrypt", help="🔓 Decrypt archive")
    d.add_argument("files", nargs="+", help="Archive(s) to decrypt")
    d.add_argument("--only", help="Selective patterns (comma-separated)")
    d.add_argument("--out", default=".", help="Output directory")

    a = p.parse_args()
    cfg = VyltConfig.load()

    # ---------------------
    if a.cmd == "setup":
        run_diagnostics()
        return

    if a.cmd == "encrypt":
        pwd = ask_password("Data password: ", confirm=True)
        encrypt_parallel(
            a.path,
            pwd,
            pwd,
            int(a.threads) if a.threads else cfg["threads"],
            os.urandom(8),
            1 if a.seal_meta else 0,
        )
        if a.wipe:
            wipe_tree(a.path)
        return

    if a.cmd == "decrypt":
        pwd = retry_password("Data password: ")
        outdir = os.path.abspath(a.out)
        os.makedirs(outdir, exist_ok=True)
        only = a.only.split(",") if a.only else ["*"]
        for f in a.files:
            for part in find_parts(f):
                decrypt_part(part, pwd, outdir, only)
