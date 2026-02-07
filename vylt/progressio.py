class ProgressIO:
    """
    File-like wrapper that updates a tqdm progress bar on read/write.
    Safe for use with libc FILE* via fdopen.
    """
    def __init__(self, f, bar):
        self.f = f
        self.bar = bar

    def read(self, size=-1):
        data = self.f.read(size)
        if data:
            self.bar.update(len(data))
        return data

    def write(self, data):
        n = self.f.write(data)
        if n:
            self.bar.update(n)
        return n

    def fileno(self):
        return self.f.fileno()

    def close(self):
        return self.f.close()
