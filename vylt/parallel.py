import os
import time
import tarfile
import tempfile
import shutil
import hashlib
import threading
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from .header import pack_outer, build_manifest
from .ciphwrap import encrypt_file
from .fileprogress import track_progress


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.digest()


def _collect_files(path):
    if os.path.isfile(path):
        return [path]
    files = []
    for r, _, fs in os.walk(path):
        for f in fs:
            files.append(os.path.join(r, f))
    return files


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


def worker(args):
    files, out, data_pwd, meta_pwd, aid, part, total, seal = args

    with tempfile.NamedTemporaryFile(delete=False) as t:
        tar_path = t.name

    with tarfile.open(tar_path, "w") as tar:
        for f in files:
            tar.add(f, arcname=os.path.relpath(f))

    manifest = build_manifest(files)

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

    ep = tempfile.NamedTemporaryFile(delete=False)
    ep.close()

    size = os.path.getsize(tar_path)
    stop = threading.Event()

    with tqdm(
        total=size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="🛡️ Encrypting",
        colour="magenta",
        dynamic_ncols=True,
    ) as bar:

        t = threading.Thread(
            target=track_progress,
            args=(ep.name, bar, stop),
            daemon=True,
        )
        t.start()

        t0 = time.perf_counter()
        encrypt_file(tar_path, ep.name, data_pwd)
        t1 = time.perf_counter()

        stop.set()
        t.join()

    data_hash = sha256_file(ep.name)

    mb = size / (1024 * 1024)
    dt = t1 - t0

    print(
        f"\n✔ Encryption complete\n"
        f"📦 Size   : {mb:.2f} MB\n"
        f"⏱ Time   : {dt:.2f} s\n"
        f"⚡ Speed  : {mb/dt:.2f} MB/s\n"
    )

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
