import fnmatch
import tarfile
from pathlib import Path
from tqdm import tqdm

def extract(stream, patterns, out):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    with tarfile.open(fileobj=stream, mode="r|") as tar:
        for m in tqdm(tar, desc="📂 Restoring", unit="file"):
            if not m.isfile():
                continue

            name = m.name

            if not any(fnmatch.fnmatch(name, p) for p in patterns):
                continue

            target = (out / name).resolve()
            if not str(target).startswith(str(out)):
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            tar.extract(m, path=out)
