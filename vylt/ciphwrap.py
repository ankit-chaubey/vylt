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
__version__ = "1.0.0"

import ctypes
import os

try:
    LIB = ctypes.CDLL(os.path.join(os.getcwd(), "libciph.so"))
except OSError:
    LIB = ctypes.CDLL("libciph.so")

LIB.ciph_encrypt_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
]
LIB.ciph_encrypt_stream.restype = ctypes.c_int

LIB.ciph_decrypt_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
]
LIB.ciph_decrypt_stream.restype = ctypes.c_int

LIB.ciph_strerror.argtypes = [ctypes.c_int]
LIB.ciph_strerror.restype = ctypes.c_char_p

libc = ctypes.CDLL(None)

fdopen = libc.fdopen
fdopen.argtypes = [ctypes.c_int, ctypes.c_char_p]
fdopen.restype = ctypes.c_void_p

fclose = libc.fclose
fclose.argtypes = [ctypes.c_void_p]
fclose.restype = ctypes.c_int


def _die(rc: int):
    msg = LIB.ciph_strerror(rc)
    raise RuntimeError(msg.decode(errors="ignore"))


def encrypt_file(src: str, dst: str, password: bytes):
    name = os.path.basename(src).encode()

    def _run(cipher: int):
        infd = os.open(src, os.O_RDONLY)
        outfd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

        fin = fdopen(infd, b"rb")
        fout = fdopen(outfd, b"wb")

        rc = LIB.ciph_encrypt_stream(
            fin,
            fout,
            password,
            cipher,
            name,
        )

        fclose(fin)
        fclose(fout)
        return rc

    rc = _run(1)  # AES first

    if rc == 0:
        return

    if rc != 0:
        try:
            os.unlink(dst)
        except FileNotFoundError:
            pass

    rc = _run(2)  # ChaCha fallback

    if rc != 0:
        _die(rc)


def decrypt_file(src: str, dst: str, password: bytes):
    infd = os.open(src, os.O_RDONLY)
    outfd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

    fin = fdopen(infd, b"rb")
    fout = fdopen(outfd, b"wb")

    name_buf = ctypes.create_string_buffer(256)

    rc = LIB.ciph_decrypt_stream(
        fin,
        fout,
        password,
        name_buf,
        ctypes.sizeof(name_buf),
    )

    fclose(fin)
    fclose(fout)

    if rc != 0:
        _die(rc)

    return name_buf.value.decode(errors="ignore")
