"""
ciph and vylt

Projects:
- ciph: https://github.com/ankit-chaubey/ciph
- vylt: https://github.com/ankit-chaubey/vylt

Author & Developer:
Ankit Chaubey (@ankit-chaubey)
https://github.com/ankit-chaubey

Copyright © 2026–present Ankit Chaubey

License:
Apache License, Version 2.0
https://www.apache.org/licenses/LICENSE-2.0
"""
import os
import tarfile
import tempfile
import shutil
import hashlib
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from .header import pack_outer, build_manifest
from .ciphwrap import encrypt_file


def check_disk_space(path):
    if os.path.isfile(path):
        total = os.path.getsize(path)
    else:
        total = sum(
            os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(path)
            for f in fs
        )

    _, _, free = shutil.disk_usage(os.getcwd())
    if free < total:
        raise SystemExit("❌ Not enough disk space")


def _collect_files(path):
    if os.path.isfile(path):
        return [path]

    files = []
    for r, _, fs in os.walk(path):
        for f in fs:
            files.append(os.path.join(r, f))
    return files


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.digest()


def worker(args):
    files, out, data_pwd, meta_pwd, aid, part, total, seal = args

    # ---------- PHASE 1: build TAR ----------
    with tempfile.NamedTemporaryFile(delete=False) as t:
        tar_path = t.name

    with tarfile.open(tar_path, "w") as tar:
        for f in files:
            tar.add(f, arcname=os.path.relpath(f))

    manifest = build_manifest(files)

    # ---------- PHASE 2: encrypt metadata ----------
    if seal:
        mp = tempfile.NamedTemporaryFile(delete=False)
        me = tempfile.NamedTemporaryFile(delete=False)
        mp.close()
        me.close()

        with open(mp.name, "wb") as m:
            m.write(manifest)

        encrypt_file(mp.name, me.name, meta_pwd)

        meta_len = os.path.getsize(me.name)
        meta_hash = sha256_file(me.name)

    else:
        meta_len = len(manifest)
        meta_hash = hashlib.sha256(manifest).digest()

    # ---------- PHASE 3: encrypt payload ----------
    ep = tempfile.NamedTemporaryFile(delete=False)
    ep.close()

    encrypt_file(tar_path, ep.name, data_pwd)
    data_hash = sha256_file(ep.name)

    # ---------- PHASE 4: write final archive ----------
    with open(out, "wb") as f:
        f.write(
            pack_outer(
                aid,
                part,
                total,
                1 if seal else 0,
                meta_len,
                meta_hash,
                data_hash,
            )
        )

        if seal:
            with open(me.name, "rb") as m:
                shutil.copyfileobj(m, f)
        else:
            f.write(manifest)

        with open(ep.name, "rb") as d:
            shutil.copyfileobj(d, f)

    # ---------- CLEANUP ----------
    os.unlink(tar_path)
    os.unlink(ep.name)
    if seal:
        os.unlink(mp.name)
        os.unlink(me.name)


def encrypt_parallel(path, data_pwd, meta_pwd, threads, aid, seal):
    check_disk_space(path)

    files = _collect_files(path)
    if not files:
        raise SystemExit("❌ Nothing to encrypt")

    n = threads if threads > 1 else 1
    buckets = [files[i::n] for i in range(n)]

    base = os.path.basename(path.rstrip("/"))
    tasks = []

    for i, b in enumerate(buckets, 1):
        if not b:
            continue

        out = (
            f"{base}.{aid.hex()}.vylt"
            if n == 1
            else f"{base}.{aid.hex()}.{i:03d}.vylt"
        )

        tasks.append((b, out, data_pwd, meta_pwd, aid, i, len(buckets), seal))

    if n == 1:
        list(
            tqdm(
                [tasks[0]],
                desc="🛡️ Encrypting",
                unit="shard",
                colour="magenta",
            )
        )
        worker(tasks[0])
    else:
        with ProcessPoolExecutor(n) as ex:
            list(
                tqdm(
                    ex.map(worker, tasks),
                    total=len(tasks),
                    desc="🛡️ Encrypting",
                    unit="shard",
                    colour="magenta",
                )
            )
