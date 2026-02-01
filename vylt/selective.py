import fnmatch, tarfile
from pathlib import Path
from tqdm import tqdm
def extract(stream, patterns, out):
    out = Path(out)
    out.mkdir(exist_ok=True)
    with tarfile.open(fileobj=stream, mode="r|") as tar:
        for m in tqdm(tar, desc="📂 Restoring", unit="file"):
            if m.isfile() and any(fnmatch.fnmatch(m.name, p) for p in patterns):
                tar.extract(m, path=out)
