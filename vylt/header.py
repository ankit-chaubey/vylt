"""
ciph and vylt

Projects:
- ciph: https://github.com/ankit-chaubey/ciph
- vylt: https://github.com/ankit-chaubey/vylt

Author & Developer:
Ankit Chaubey (@ankit-chaubey)
https://github.com/ankit-chaubey

Copyright © 2026 Ankit Chaubey

License:
Apache License, Version 2.0
https://www.apache.org/licenses/LICENSE-2.0
"""

import struct

# -------------------------
# Constants
# -------------------------

MAGIC = b"VYLT"
VERSION = 1

# Header layout (big-endian):
#
#  0–3   : MAGIC        (4s)   b"VYLT"
#  4     : VERSION      (B)
#  5     : SEALED       (B)    0 / 1
#  6–13  : ARCHIVE ID   (8s)
# 14–15  : PART NO      (H)
# 16–17  : TOTAL PARTS  (H)
# 18–21  : META LENGTH  (I)    encrypted meta size (VARIABLE!)
# 22–53  : META HASH    (32s)  sha256(encrypted meta)
# 54–85  : DATA HASH    (32s)  sha256(encrypted payload)
#
# Total = 86 bytes

HEADER_FMT = ">4sBB8sHHI32s32s"
HEADER_SIZE = struct.calcsize(HEADER_FMT)


# -------------------------
# Builders
# -------------------------

def pack_outer(
    aid: bytes,
    part: int,
    total: int,
    sealed: int,
    meta_len: int,
    meta_hash: bytes,
    data_hash: bytes,
):
    """
    Build Vylt outer header.
    """
    if len(aid) != 8:
        raise ValueError("Archive ID must be 8 bytes")

    if len(meta_hash) != 32 or len(data_hash) != 32:
        raise ValueError("Hashes must be SHA-256 (32 bytes)")

    return struct.pack(
        HEADER_FMT,
        MAGIC,
        VERSION,
        sealed,
        aid,
        part,
        total,
        meta_len,
        meta_hash,
        data_hash,
    )


# -------------------------
# Parsers
# -------------------------

def unpack_outer(buf: bytes):
    """
    Parse Vylt outer header.
    Returns:
      magic, version, sealed, aid, part, total, meta_len, meta_hash, data_hash
    """
    if len(buf) < HEADER_SIZE:
        raise ValueError("Buffer too small for Vylt header")

    return struct.unpack(HEADER_FMT, buf)


# -------------------------
# Metadata builder
# -------------------------

def build_manifest(files):
    """
    Build Vylt metadata manifest (PLAIN).
    Format:
      VMNF | count | NUL-separated paths
    """
    head = struct.pack(">4sI", b"VMNF", len(files))
    body = b"\0".join(f.encode() for f in files)
    return head + body
