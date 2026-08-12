"""
DXF Generator — Creates professional multi-layered DXF files for CNC machines.

Layers:
  SHEET_OUTLINE  (color 7  / White)  — Raw sheet metal boundary
  MARGIN_BORDER  (color 4  / Cyan)   — Safety margin / clamp zone (dashed)
  CUT_LINES      (color 1  / Red)    — Actual cut contours for the CNC
  LABELS         (color 3  / Green)  — Piece identification text (label + dimensions)
  INFO           (color 2  / Yellow) — Title block with metadata

Output format: AutoCAD R2010 DXF (compatible with AutoCAD, LibreCAD, and CNC controllers).

Design rules for AutoCAD compatibility:
  - All linetypes must be explicitly defined in the LTYPE table (no implicit DASHED).
  - Text uses only ASCII characters (no accented letters, no × symbol).
  - TEXT entities are positioned with an insertion point + halign/valign code via
    dxfattribs; set_placement() is used only where the alignment parameter is a
    valid TextEntityAlignment member.
  - Header variables $EXTMIN/$EXTMAX/$LIMMIN/$LIMMAX are set explicitly so that
    AutoCAD opens the file with a correct "Zoom Extents" view.
"""

import io
import re
from datetime import datetime

import ezdxf
import ezdxf.zoom
from ezdxf.enums import TextEntityAlignment

from models import NestingResult


# ──────────────────────────────────────
# Helper: strip non-ASCII characters
# ──────────────────────────────────────
def _ascii(text: str) -> str:
    """Replace common accented / special characters with ASCII equivalents."""
    replacements = {
        "à": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
        "×": "x",
        "—": "-",
        "\u2019": "'",  # right single quotation mark
    }
    for char, sub in replacements.items():
        text = text.replace(char, sub)
    # Strip any remaining non-ASCII characters
    return text.encode("ascii", errors="replace").decode("ascii").replace("?", "_")


def generate_dxf(result: NestingResult) -> bytes:
    """
    Generate a complete DXF file from a NestingResult.

    Returns the DXF file content as raw bytes, ready to be
    streamed as an HTTP response or written to disk.
    """

    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM

    # ──────────────────────────────────────
    # Linetype definitions (must exist before any entity references them)
    # ──────────────────────────────────────
    if "DASHED" not in doc.linetypes:
        doc.linetypes.add(
            "DASHED",
            pattern="A, 12.0, -6.0",
            description="Dashed _ _ _ _",
        )
    if "CONTINUOUS" not in doc.linetypes:
        # Always present in a new document, but guard just in case
        doc.linetypes.add("CONTINUOUS", description="Solid line")

    # ──────────────────────────────────────
    # Layer setup
    # ──────────────────────────────────────
    doc.layers.add("SHEET_OUTLINE", color=7)                       # White
    doc.layers.add("MARGIN_BORDER", color=4, linetype="DASHED")    # Cyan / dashed
    doc.layers.add("CUT_LINES",     color=1)                       # Red
    doc.layers.add("LABELS",        color=3)                       # Green
    doc.layers.add("INFO",          color=2)                       # Yellow

    msp = doc.modelspace()

    sw     = result.sheet_width
    sh     = result.sheet_height
    margin = result.sheet_margin

    # ──────────────────────────────────────
    # 1. Sheet outline (raw sheet boundary)
    # ──────────────────────────────────────
    msp.add_lwpolyline(
        [(0, 0), (sw, 0), (sw, sh), (0, sh)],
        close=True,
        dxfattribs={"layer": "SHEET_OUTLINE", "lineweight": 50},
    )

    # ──────────────────────────────────────
    # 2. Margin border (usable area inside the sheet)
    # ──────────────────────────────────────
    if margin > 0:
        msp.add_lwpolyline(
            [
                (margin,      margin),
                (sw - margin, margin),
                (sw - margin, sh - margin),
                (margin,      sh - margin),
            ],
            close=True,
            dxfattribs={"layer": "MARGIN_BORDER", "linetype": "DASHED"},
        )

    # ──────────────────────────────────────
    # 3. Cut lines + labels for each placed piece
    # ──────────────────────────────────────
    for piece in result.placed_pieces:
        x, y = piece.x, piece.y
        w, h = piece.width, piece.height

        # 3a. Cut contour
        msp.add_lwpolyline(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
            close=True,
            dxfattribs={"layer": "CUT_LINES"},
        )

        # 3b. Text height: 10 % of the smallest side, clamped [3 mm – 20 mm]
        text_h = min(max(min(w, h) * 0.10, 3.0), 20.0)
        cx     = x + w / 2
        cy     = y + h / 2

        # ── Line 1: piece label (human-readable name) ──────────────────────
        label = _ascii(piece.label if piece.label.strip() else piece.id)
        t1 = msp.add_text(
            label,
            dxfattribs={
                "layer":  "LABELS",
                "height": text_h,
            },
        )
        t1.set_placement(
            (cx, cy + text_h * 0.6),
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

        # ── Line 2: dimensions [+ "(R)" if rotated] ────────────────────────
        # Use only ASCII — "x" instead of "×"
        dim_str = f"{piece.width:.0f}x{piece.height:.0f} mm"
        if piece.rotated:
            dim_str += " (R)"
        dim_h = text_h * 0.65
        t2 = msp.add_text(
            _ascii(dim_str),
            dxfattribs={
                "layer":  "LABELS",
                "height": dim_h,
            },
        )
        t2.set_placement(
            (cx, cy - text_h * 0.6),
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

    # ──────────────────────────────────────
    # 4. Title block / cartouche (below the sheet)
    # ──────────────────────────────────────
    tb_x      = 0.0
    tb_y      = -10.0          # just below the sheet bottom edge
    tb_height = max(5.0, sh * 0.015)  # scale with sheet size
    tb_spacing = tb_height * 1.8

    info_lines = [
        "OptiTole - Nesting Module",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Sheet: {sw:.0f} x {sh:.0f} mm",
        f"Cut type: {result.cut_type.upper()}",
        f"Kerf: {result.kerf:.1f} mm",
        f"Pieces: {result.total_placed} / {result.total_requested} placed",
        f"Utilization: {result.utilization_rate:.1f}%",
    ]

    for i, line in enumerate(info_lines):
        t = msp.add_text(
            _ascii(line),
            dxfattribs={
                "layer":  "INFO",
                "height": tb_height,
            },
        )
        t.set_placement(
            (tb_x, tb_y - i * tb_spacing),
            align=TextEntityAlignment.LEFT,
        )

    # ──────────────────────────────────────
    # 5. Drawing extents (critical for AutoCAD auto-zoom)
    # ──────────────────────────────────────
    # Compute actual bounding box
    info_bottom = tb_y - len(info_lines) * tb_spacing

    ext_min_x, ext_min_y = 0.0, info_bottom
    ext_max_x, ext_max_y = float(sw), float(sh)

    try:
        from ezdxf import bbox as ezdxf_bbox
        extents = ezdxf_bbox.extents(msp, fast=True)
        if extents.has_data:
            ext_min_x = min(0.0, extents.extmin.x)
            ext_min_y = min(info_bottom, extents.extmin.y)
            ext_max_x = max(float(sw), extents.extmax.x)
            ext_max_y = max(float(sh), extents.extmax.y)
    except Exception:
        pass

    # Zoom the Model Space viewport to fit all entities
    try:
        ezdxf.zoom.extents(msp)
    except Exception:
        pass

    # ──────────────────────────────────────
    # 6. Export to bytes (then patch raw DXF header)
    # ──────────────────────────────────────
    stream = io.StringIO()
    doc.write(stream)
    raw = stream.getvalue()

    # ezdxf writes $EXTMIN/$EXTMAX as 1e+20/-1e+20 (sentinel values).
    # We patch them directly in the raw text — the only reliable method.
    def _patch_var3(text: str, varname: str, x: float, y: float, z: float = 0.0) -> str:
        """Replace a 3-point header variable (groups 9, 10, 20, 30) in raw DXF."""
        import re as _re
        pattern = (
            r"(  9\r?\n\\" + varname.lstrip("$") + r"\r?\n"
            r"\s*10\r?\n)[^\r\n]+"
            r"(\r?\n\s*20\r?\n)[^\r\n]+"
            r"(\r?\n\s*30\r?\n)[^\r\n]+"
        )
        replacement = (
            r"\g<1>" + repr(x) +
            r"\g<2>" + repr(y) +
            r"\g<3>" + repr(z)
        )
        return _re.sub(pattern, replacement, text, count=1)

    def _patch_var2(text: str, varname: str, x: float, y: float) -> str:
        """Replace a 2-point header variable (groups 9, 10, 20) in raw DXF."""
        import re as _re
        pattern = (
            r"(  9\r?\n\\" + varname.lstrip("$") + r"\r?\n"
            r"\s*10\r?\n)[^\r\n]+"
            r"(\r?\n\s*20\r?\n)[^\r\n]+"
        )
        replacement = r"\g<1>" + repr(x) + r"\g<2>" + repr(y)
        return _re.sub(pattern, replacement, text, count=1)

    # Patch using simple string.replace — ezdxf writes LF-separated values.
    # $EXTMIN sentinel: "1e+20"  $EXTMAX sentinel: "-1e+20"
    raw = raw.replace(
        "$EXTMIN\n 10\n1e+20\n 20\n1e+20\n 30\n1e+20",
        f"$EXTMIN\n 10\n{ext_min_x:.6f}\n 20\n{ext_min_y:.6f}\n 30\n0.0",
        1,
    )
    raw = raw.replace(
        "$EXTMAX\n 10\n-1e+20\n 20\n-1e+20\n 30\n-1e+20",
        f"$EXTMAX\n 10\n{ext_max_x:.6f}\n 20\n{ext_max_y:.6f}\n 30\n0.0",
        1,
    )
    raw = raw.replace(
        "$LIMMIN\n 10\n0.0\n 20\n0.0",
        f"$LIMMIN\n 10\n{ext_min_x:.6f}\n 20\n{ext_min_y:.6f}",
        1,
    )
    raw = raw.replace(
        "$LIMMAX\n 10\n420.0\n 20\n297.0",
        f"$LIMMAX\n 10\n{ext_max_x:.6f}\n 20\n{ext_max_y:.6f}",
        1,
    )

    return raw.encode("utf-8")

