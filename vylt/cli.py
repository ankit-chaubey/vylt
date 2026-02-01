"""
ciph and vylt

Projects:
- ciph: https://github.com/ankit-chaubey/ciph
- vylt: https://github.com/ankit-chaubey/vylt

Author & Developer:
Ankit Chaubey (@ankit-chaubey)
https://github.com/ankit-chaubey

Copyright © 2026–present Ankit Chaubey

Licensed under the Apache License, Version 2.0
https://www.apache.org/licenses/LICENSE-2.0
"""

import argparse
import os
import glob
import getpass
import tempfile
import sys
import struct
import shutil
from tqdm import tqdm

from .config import VyltConfig
from .parallel import encrypt_parallel
from .selective import extract
from .wipe import wipe_tree
from .diagnostics import run_diagnostics
from .header import HEADER_SIZE, unpack_outer
from .ciphwrap import decrypt_file


class C:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    PINK = "\033[38;5;213m"

LOGO = f"""{C.MAGENTA}
╔══════════════════════════════════╗
║  V Y L T  –  Encryption Engine   ║
╚══════════════════════════════════╝
{C.RESET}"""

BANNER = f"""
{C.MAGENTA}
██╗   ██╗██╗   ██╗██╗     ████████╗
██║   ██║╚██╗ ██╔╝██║     ╚══██╔══╝
██║   ██║ ╚████╔╝ ██║        ██║   
╚██╗ ██╔╝  ╚██╔╝  ██║        ██║   
 ╚████╔╝    ██║   ███████╗   ██║   
  ╚═══╝     ╚═╝   ╚══════╝   ╚═╝   
{C.RESET}

{C.MAGENTA}
╔══════════════════════════════════╗
║  V Y L T  –  Encryption Engine   ║
╚══════════════════════════════════╝
{C.RESET}
{C.YELLOW}✓ Powered by CIPH © 2026-present{C.RESET}
{C.CYAN}Developed by Ankit Chaubey (@ankit-chaubey){C.RESET}

{C.GREEN}Commands:{C.RESET}
  {C.YELLOW}setup{C.RESET}     Run diagnostics and environment checks
  {C.YELLOW}info{C.RESET}      Show archive header information
  {C.YELLOW}list{C.RESET}      List files inside an archive
  {C.YELLOW}encrypt{C.RESET}   Encrypt a file or directory
  {C.YELLOW}decrypt{C.RESET}   Decrypt an archive

{C.BLUE}Quick examples:{C.RESET}
  • vylt encrypt myfolder
  • vylt info myfolder.*.vylt
  • vylt list myfolder.*.vylt
  • vylt enrypt doc/backup --seal-meta
  • vylt decrypt backup.*.vylt

{C.CYAN}> vylt --help for more details{C.RESET}
"""

def _cfg_password():
    cfg = VyltConfig.load()
    env = cfg.get("password_from_env") or "VYLT_PASSWORD"
    val = os.getenv(env)
    if val:
        return val.encode()
    return None

def ask_password(prompt, confirm=False):
    cfg_pwd = _cfg_password()
    if cfg_pwd:
        return cfg_pwd
    p = getpass.getpass(prompt)
    if confirm and p != getpass.getpass("Confirm: "):
        raise SystemExit(f"{C.RED}❌ Password mismatch{C.RESET}")
    return p.encode()


def retry_password(prompt):
    cfg_pwd = _cfg_password()
    if cfg_pwd:
        return cfg_pwd
    attempts = VyltConfig.load().get("max_password_attempts", 5)
    for _ in range(attempts):
        p = getpass.getpass(prompt)
        if p:
            return p.encode()
    raise SystemExit(f"{C.RED}❌ Too many attempts{C.RESET}")


def find_parts(path):
    base = os.path.basename(path)
    parts = base.rsplit(".", 3)
    if len(parts) < 3:
        return [path]
    root, aid = parts[0], parts[1]
    if not all(c in "0123456789abcdef" for c in aid):
        return [path]
    return sorted(glob.glob(f"{root}.{aid}.*.vylt")) or [path]


def info_cmd(path):
    with open(path, "rb") as f:
        hdr = f.read(HEADER_SIZE)

    magic, version, sealed, aid, part, total, meta_len, _, _ = unpack_outer(hdr)

    print(LOGO)

    print(f"{C.CYAN}📦 Vault Encryption Info{C.RESET}")
    print("────────────────────")
    print(f"Magic       : {magic.decode()}")
    print(f"Version     : v{version}")
    print(f"Archive ID  : {aid.hex()}")
    print(f"Part        : {part}")
    print(f"Sealed Meta : {'Yes' if sealed else 'No'}")
    print(f"Meta Length : {meta_len} bytes")
    print(f"Type        : {'Single' if total <= 1 else 'Sharded'}")


def list_cmd(path):
    with open(path, "rb") as f:
        hdr = f.read(HEADER_SIZE)
        magic, version, sealed, aid, part, total, meta_len, _, _ = unpack_outer(hdr)
        meta_blob = f.read(meta_len)

    if magic != b"VYLT":
        raise SystemExit(f"{C.RED}❌ Not a Vylt archive{C.RESET}")

    if sealed:
        pwd = retry_password(f"{C.PINK}Metadata password: {C.RESET}")
        encf = tempfile.NamedTemporaryFile(delete=False)
        decf = tempfile.NamedTemporaryFile(delete=False)
        encf.write(meta_blob)
        encf.close()
        decf.close()
        try:
            decrypt_file(encf.name, decf.name, pwd)
            with open(decf.name, "rb") as f:
                meta = f.read()
        finally:
            os.unlink(encf.name)
            os.unlink(decf.name)
    else:
        meta = meta_blob

    sig, count = struct.unpack(">4sI", meta[:8])
    if sig != b"VMNF":
        raise SystemExit(f"{C.RED}❌ Bad metadata or wrong password{C.RESET}")

    names = [n.decode() for n in meta[8:].split(b"\0") if n][:count]

    print(LOGO)
    print(f"{C.GREEN}📂 Archive contents{C.RESET}")
    print("──────────────────")
    for i, n in enumerate(names, 1):
        print(f"{C.BLUE}{i:3d}.{C.RESET} {n}")


def main():
    if len(sys.argv) == 1:
        print(BANNER)
        return

    p = argparse.ArgumentParser(
        prog="vylt",
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"""
   {C.MAGENTA}
     __     __     _ _
     \\ \\   / /   _| | |_
      \\ \\ / / | | | | __|
       \\ V /| |_| | | |_
        \\_/  \\__,_|_|\\__|
   {C.RESET}

    A secure, disk-first encryption tool for files and directories.

    {C.CYAN}Core features:{C.RESET}
      • Streaming ChaCha20 encryption
      • Sharded archives for large data
      • Optional sealed metadata
      • FD-safe, Linux-safe design
      • Works on Termux and servers
    """,
        epilog=rf"""
    {C.GREEN}COMMAND GUIDE{C.RESET}

    {C.YELLOW}setup{C.RESET}
      Run system diagnostics and verify cryptographic backend.

    {C.YELLOW}info <archive.vylt>{C.RESET}
      Show low-level archive header details:
        - format version
        - archive ID
        - shard information
        - metadata size

    {C.YELLOW}list <archive.vylt>{C.RESET}
      List files stored in the archive.
      If metadata is sealed, a password is required.

    {C.YELLOW}encrypt <path> [options]{C.RESET}
      Encrypt a file or directory.

      Options:
        --seal-meta     Encrypt file list (hide metadata)
        --threads N     Number of encryption workers
        --wipe          Securely delete original files


    {C.YELLOW}decrypt <archive.vylt> [options]{C.RESET}
      Decrypt and extract files.

      Options:
        --only files    Comma-separated file paths to extract
        --out DIR       Output directory (default: current)

    {C.BLUE}EXAMPLES{C.RESET}
      vylt setup
      vylt encrypt folder/secrets --seal-meta
      vylt list backup.vylt
      vylt decrypt backup.vylt --out restore/

    {C.RED}SECURITY NOTE{C.RESET}
      Lost passwords cannot be recovered.
      There is no backdoor by design.

    {C.MAGENTA}
    ╔══════════════════════════════════╗
    ║  V Y L T  –  Encryption Engine   ║
    ╚══════════════════════════════════╝
    {C.RESET}
"""
    )
    s = p.add_subparsers(dest="cmd", required=True)

    s.add_parser("setup")

    i = s.add_parser("info")
    i.add_argument("file")

    l = s.add_parser("list")
    l.add_argument("file")

    e = s.add_parser("encrypt")
    e.add_argument("path")
    e.add_argument("--threads", type=int)
    e.add_argument("--seal-meta", action="store_true")
    e.add_argument("--wipe", action="store_true")

    d = s.add_parser("decrypt")
    d.add_argument("file")
    d.add_argument("--only")
    d.add_argument("--out", default=".")

    a = p.parse_args()
    cfg = VyltConfig.load()

    if a.cmd == "setup":
        run_diagnostics()
        return

    if a.cmd == "info":
        info_cmd(a.file)
        return

    if a.cmd == "list":
        list_cmd(a.file)
        return

    if a.cmd == "encrypt":
        data_pwd = ask_password(f"{C.PINK}Data password: {C.RESET}", confirm=True)
        meta_pwd = data_pwd
        if a.seal_meta and not cfg.get("reuse_data_password_for_meta", True):
            meta_pwd = ask_password(f"{C.PINK}Metadata password: {C.RESET}", confirm=True)

        encrypt_parallel(
            a.path,
            data_pwd,
            meta_pwd,
            a.threads or cfg["threads"],
            os.urandom(8),
            1 if a.seal_meta else 0
        )

        if a.wipe:
            wipe_tree(a.path)

    elif a.cmd == "decrypt":
        pwd = retry_password(f"{C.PINK}Data password: {C.RESET}")
        for part in tqdm(
            find_parts(a.file),
            desc=f"{C.MAGENTA}🔓 Decrypting{C.RESET}",
            unit="shard",
            colour="cyan"
        ):
            payload = tempfile.NamedTemporaryFile(delete=False)
            dec_tar = tempfile.NamedTemporaryFile(delete=False)
            payload.close()
            dec_tar.close()
            try:
                with open(part, "rb") as f:
                    hdr = f.read(HEADER_SIZE)
                    _, _, _, _, _, _, meta_len, _, _ = unpack_outer(hdr)
                    f.seek(HEADER_SIZE + meta_len)
                    with open(payload.name, "wb") as pld:
                        shutil.copyfileobj(f, pld)

                decrypt_file(payload.name, dec_tar.name, pwd)

                with open(dec_tar.name, "rb") as tarf:
                    extract(
                        tarf,
                        a.only.split(",") if a.only else ["*"],
                        a.out
                    )
            finally:
                os.unlink(payload.name)
                os.unlink(dec_tar.name)
