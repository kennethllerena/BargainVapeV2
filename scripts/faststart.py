"""Move an MP4's `moov` atom to the front of the file ("faststart").

Encoders often leave `moov` after `mdat`, which forces a browser to download the
whole file before it can show a single frame. Relocating it lets playback begin
while the rest still streams. This is a lossless byte-shuffle — no re-encoding,
no quality change — but every chunk offset inside `moov` has to be rewritten,
because the media data ends up further down the file.

    python scripts/faststart.py input.mp4 output.mp4
"""

import os
import shutil
import struct
import sys


def read_boxes(data, start, end):
    """Yield (type, offset, header_len, total_size) for boxes in [start, end)."""
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8].decode("latin1")
        hdr = 8
        if size == 1:
            size = struct.unpack(">Q", data[pos + 8:pos + 16])[0]
            hdr = 16
        elif size == 0:
            size = end - pos
        if size < hdr:
            break
        yield typ, pos, hdr, size
        pos += size


CONTAINERS = {"moov", "trak", "mdia", "minf", "stbl", "edts", "udta", "mvex"}


def patch_offsets(buf, start, end, delta):
    """Add `delta` to every chunk offset in stco/co64 boxes within this range."""
    patched = 0
    for typ, pos, hdr, size in read_boxes(buf, start, end):
        body = pos + hdr
        if typ in CONTAINERS:
            patched += patch_offsets(buf, body, pos + size, delta)
        elif typ in ("stco", "co64"):
            count = struct.unpack(">I", buf[body + 4:body + 8])[0]
            entry = body + 8
            if typ == "stco":
                for i in range(count):
                    off = entry + i * 4
                    val = struct.unpack(">I", buf[off:off + 4])[0]
                    struct.pack_into(">I", buf, off, val + delta)
            else:
                for i in range(count):
                    off = entry + i * 8
                    val = struct.unpack(">Q", buf[off:off + 8])[0]
                    struct.pack_into(">Q", buf, off, val + delta)
            patched += count
    return patched


def faststart(src, dst):
    with open(src, "rb") as f:
        data = f.read()

    top = list(read_boxes(data, 0, len(data)))
    kinds = [t for t, _, _, _ in top]
    if "moov" not in kinds:
        raise SystemExit("no moov atom found")

    moov = next(b for b in top if b[0] == "moov")
    ftyp = next((b for b in top if b[0] == "ftyp"), None)
    mdat = next((b for b in top if b[0] == "mdat"), None)

    if mdat and moov[1] < mdat[1]:
        # Already streamable. Still copy it through so callers can treat this as
        # "produce the web-ready file at dst" regardless of the input.
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)
            print("moov already at front — copied unchanged to", dst)
        else:
            print("moov already at front — nothing to do")
        return False

    moov_buf = bytearray(data[moov[1]:moov[1] + moov[3]])

    # Everything except ftyp and moov, in original order.
    rest = [b for b in top if b[0] not in ("ftyp", "moov")]

    # In the new layout moov sits directly after ftyp, so all media data slides
    # down by exactly the size of moov.
    delta = moov[3]
    n = patch_offsets(moov_buf, 8, len(moov_buf), delta)

    with open(dst, "wb") as out:
        if ftyp:
            out.write(data[ftyp[1]:ftyp[1] + ftyp[3]])
        out.write(moov_buf)
        for _, pos, _, size in rest:
            out.write(data[pos:pos + size])

    print("moved moov to front, patched %d chunk offsets" % n)
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    faststart(sys.argv[1], sys.argv[2])
