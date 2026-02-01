import os, secrets
def wipe_file(p):
    if not os.path.exists(p): return
    size = os.path.getsize(p)
    with open(p, "r+b") as f:
        f.write(secrets.token_bytes(size))
        f.flush()
        os.fsync(f.fileno())
    os.remove(p)

def wipe_tree(root):
    for base, _, files in os.walk(root, topdown=False):
        for f in files: wipe_file(os.path.join(base, f))
        try: os.rmdir(base)
        except: pass
