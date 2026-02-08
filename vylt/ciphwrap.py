"""
ciph and vylt

Projects:
- ciph: https://github.com/ankit-chaubey/ciph
- vylt: https://github.com/ankit-chaubey/vylt

Author & Developer:
Ankit Chaubey (@ankit-chaubey)

License:
Apache License, Version 2.0
"""

__version__ = "1.1.2"

import ctypes
import os


# -------------------------
# Load libciph
# -------------------------

try:
    LIB = ctypes.CDLL(os.path.join(os.getcwd(), "libciph.so"), mode=ctypes.RTLD_GLOBAL)
except OSError:
    LIB = ctypes.CDLL("libciph.so", mode=ctypes.RTLD_GLOBAL)


# -------------------------
# Correct ABI types
# -------------------------

u8_p = ctypes.POINTER(ctypes.c_uint8)

LIB.ciph_encrypt_stream.argtypes = [
    ctypes.c_void_p,   # FILE *in
    ctypes.c_void_p,   # FILE *out
    u8_p,              # password (RAW)
    ctypes.c_size_t,   # password_len
    ctypes.c_int,      # cipher
    u8_p,              # original_name (RAW)
]
LIB.ciph_encrypt_stream.restype = ctypes.c_int


LIB.ciph_decrypt_stream.argtypes = [
    ctypes.c_void_p,   # FILE *in
    ctypes.c_void_p,   # FILE *out
    u8_p,              # password (RAW)
    ctypes.c_size_t,   # password_len
    ctypes.c_char_p,   # out_name
    ctypes.c_size_t,   # out_name_len
]
LIB.ciph_decrypt_stream.restype = ctypes.c_int


LIB.ciph_strerror.argtypes = [ctypes.c_int]
LIB.ciph_strerror.restype = ctypes.c_char_p


# -------------------------
# libc helpers
# -------------------------

libc = ctypes.CDLL(None)

fdopen = libc.fdopen
fdopen.argtypes = [ctypes.c_int, ctypes.c_char_p]
fdopen.restype = ctypes.c_void_p

fclose = libc.fclose
fclose.argtypes = [ctypes.c_void_p]
fclose.restype = ctypes.c_int


# -------------------------
# Error helper
# -------------------------

def _die(rc: int):
    msg = LIB.ciph_strerror(rc)
    raise RuntimeError(msg.decode(errors="ignore"))


# -------------------------
# Public API
# -------------------------

def _as_u8(buf: bytes):
    return (ctypes.c_uint8 * len(buf)).from_buffer_copy(buf)


def encrypt_file(src: str, dst: str, password: bytes):
    name = os.path.basename(src).encode()

    pwd_buf = _as_u8(password)
    name_buf = _as_u8(name)

    def _run(cipher: int):
        infd = os.open(src, os.O_RDONLY)
        outfd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

        fin = fdopen(infd, b"rb")
        fout = fdopen(outfd, b"wb")

        rc = LIB.ciph_encrypt_stream(
            fin,
            fout,
            pwd_buf,
            len(password),
            cipher,
            name_buf,
        )

        fclose(fin)
        fclose(fout)
        return rc

    rc = _run(1)  # AES
    if rc == 0:
        return

    try:
        os.unlink(dst)
    except FileNotFoundError:
        pass

    rc = _run(2)  # ChaCha
    if rc != 0:
        _die(rc)


def decrypt_file(src: str, dst: str, password: bytes):
    pwd_buf = _as_u8(password)

    infd = os.open(src, os.O_RDONLY)
    outfd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

    fin = fdopen(infd, b"rb")
    fout = fdopen(outfd, b"wb")

    name_buf = ctypes.create_string_buffer(256)

    rc = LIB.ciph_decrypt_stream(
        fin,
        fout,
        pwd_buf,
        len(password),
        name_buf,
        ctypes.sizeof(name_buf),
    )

    fclose(fin)
    fclose(fout)

    if rc != 0:
        _die(rc)

    return name_buf.value.decode(errors="ignore")
