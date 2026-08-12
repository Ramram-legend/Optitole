"""Full DXF generation audit test."""
import io
import ezdxf
import ezdxf.audit
from dxf_generator import generate_dxf
from models import NestingResult, PlacedPiece, UnplacedPiece

result = NestingResult(
    placed_pieces=[
        PlacedPiece(id="P1", label="Gousset G1", x=10,  y=10,  width=200, height=150, rotated=False),
        PlacedPiece(id="P2", label="Bride B2",   x=220, y=10,  width=100, height=300, rotated=True),
        PlacedPiece(id="P3", label="Platine Px", x=10,  y=170, width=180, height=200, rotated=False),
    ],
    unplaced_pieces=[],
    utilization_rate=72.5,
    total_requested=3,
    total_placed=3,
    cut_type="laser",
    sheet_width=500,
    sheet_height=600,
    sheet_margin=10,
    kerf=3,
)

dxf_bytes = generate_dxf(result)

# Audit
doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8")))
auditor = ezdxf.audit.Auditor(doc)
auditor.run()
print("Errors  :", auditor.errors)
print("Fixes   :", [(str(f.code), f.message) for f in auditor.fixes])
print("EXTMIN  :", doc.header.get("$EXTMIN"))
print("EXTMAX  :", doc.header.get("$EXTMAX"))

# Check labels
entities = list(doc.modelspace())
text_contents = [e.dxf.text for e in entities if e.dxftype() == "TEXT"]
print("Text entities:", text_contents)

# Save to disk for AutoCAD inspection
with open("test_autocad.dxf", "wb") as f:
    f.write(dxf_bytes)
print("Saved test_autocad.dxf — open this file in AutoCAD to verify")
