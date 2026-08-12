with open("test_autocad.dxf", "r", encoding="utf-8") as f:
    raw = f.read()
idx = raw.find("EXTMIN")
print(repr(raw[idx - 5:idx + 60]))
idx2 = raw.find("EXTMAX")
print(repr(raw[idx2 - 5:idx2 + 60]))

# Test simple replace
patched = raw.replace(
    "$EXTMIN\n 10\n1e+20\n 20\n1e+20\n 30\n1e+20",
    "$EXTMIN\n 10\n0.0\n 20\n-100.0\n 30\n0.0"
)
print("Changed (LF):", raw != patched)

patched2 = raw.replace(
    "$EXTMIN\r\n 10\r\n1e+20\r\n 20\r\n1e+20\r\n 30\r\n1e+20",
    "$EXTMIN\r\n 10\r\n0.0\r\n 20\r\n-100.0\r\n 30\r\n0.0"
)
print("Changed (CRLF):", raw != patched2)
