"""
Unit tests for the OptiTôle nesting engine and DXF generator.
Run with: pytest tests/test_nesting.py -v
"""

import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ezdxf

from models import NestingRequest, Piece
from nesting_engine import solve_nesting
from dxf_generator import generate_dxf


# ─────────────────────────────────────────────────
# Helper: create a standard request
# ─────────────────────────────────────────────────
def make_request(
    pieces: list[Piece],
    sheet_w: float = 2500.0,
    sheet_h: float = 1250.0,
    thickness: float = 10.0,
    kerf: float = 5.0,
    margin: float = 10.0,
) -> NestingRequest:
    return NestingRequest(
        sheet_width=sheet_w,
        sheet_height=sheet_h,
        thickness=thickness,
        kerf=kerf,
        sheet_margin=margin,
        pieces=pieces,
    )


# ─────────────────────────────────────────────────
# Test: Single piece placement
# ─────────────────────────────────────────────────
class TestSinglePiece:
    def test_single_piece_fits(self):
        """A single small piece should always be placed."""
        pieces = [Piece(id="P1", label="Test", width=200, height=100)]
        result = solve_nesting(make_request(pieces))

        assert result.total_placed == 1
        assert len(result.placed_pieces) == 1
        assert result.placed_pieces[0].id == "P1"
        assert len(result.unplaced_pieces) == 0

    def test_piece_too_large(self):
        """A piece larger than the sheet should be unplaced."""
        pieces = [Piece(id="P1", label="Huge", width=3000, height=2000)]
        result = solve_nesting(make_request(pieces))

        assert result.total_placed == 0
        assert len(result.unplaced_pieces) == 1


# ─────────────────────────────────────────────────
# Test: Multiple pieces
# ─────────────────────────────────────────────────
class TestMultiplePieces:
    def test_multiple_pieces_placed(self):
        """Multiple small pieces should all be placed."""
        pieces = [
            Piece(id="A", label="Piece A", width=200, height=150, quantity=3),
            Piece(id="B", label="Piece B", width=300, height=100, quantity=2),
        ]
        result = solve_nesting(make_request(pieces))

        assert result.total_requested == 5  # 3 + 2
        assert result.total_placed == 5
        assert len(result.unplaced_pieces) == 0

    def test_overflow_pieces(self):
        """When pieces exceed sheet capacity, some should be unplaced."""
        pieces = [
            Piece(id="X", label="Big", width=800, height=600, quantity=10),
        ]
        result = solve_nesting(make_request(pieces))

        assert result.total_requested == 10
        assert result.total_placed < 10
        assert len(result.unplaced_pieces) > 0
        assert result.total_placed + len(result.unplaced_pieces) == 10


# ─────────────────────────────────────────────────
# Test: Kerf / spacing validation
# ─────────────────────────────────────────────────
class TestKerfSpacing:
    def test_kerf_respected(self):
        """No two placed pieces should overlap or be closer than kerf."""
        pieces = [
            Piece(id="K1", label="K1", width=300, height=200, quantity=4),
        ]
        kerf = 8.0
        result = solve_nesting(make_request(pieces, kerf=kerf))

        placed = result.placed_pieces
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                p1 = placed[i]
                p2 = placed[j]

                # Check horizontal separation
                h_gap = max(
                    p2.x - (p1.x + p1.width),
                    p1.x - (p2.x + p2.width),
                )
                # Check vertical separation
                v_gap = max(
                    p2.y - (p1.y + p1.height),
                    p1.y - (p2.y + p2.height),
                )

                # At least one gap direction must be >= kerf - small epsilon
                # (pieces don't overlap if at least one gap is >= 0)
                assert h_gap >= kerf - 0.2 or v_gap >= kerf - 0.2, (
                    f"Pieces {p1.id}@({p1.x},{p1.y}) and {p2.id}@({p2.x},{p2.y}) "
                    f"are too close: h_gap={h_gap:.2f}, v_gap={v_gap:.2f}, kerf={kerf}"
                )

    def test_pieces_within_margins(self):
        """All placed pieces must be inside the sheet margin."""
        pieces = [
            Piece(id="M1", label="Margin Test", width=150, height=100, quantity=6),
        ]
        margin = 15.0
        result = solve_nesting(make_request(pieces, margin=margin))

        for p in result.placed_pieces:
            assert p.x >= margin - 0.1, f"Piece {p.id} x={p.x} is inside left margin"
            assert p.y >= margin - 0.1, f"Piece {p.id} y={p.y} is inside bottom margin"
            assert p.x + p.width <= 2500 - margin + 0.1, f"Piece {p.id} exceeds right margin"
            assert p.y + p.height <= 1250 - margin + 0.1, f"Piece {p.id} exceeds top margin"


# ─────────────────────────────────────────────────
# Test: Utilization rate
# ─────────────────────────────────────────────────
class TestUtilization:
    def test_utilization_calculation(self):
        """Utilization rate should be correctly calculated."""
        pieces = [
            Piece(id="U1", label="U1", width=500, height=500, quantity=1),
        ]
        result = solve_nesting(make_request(pieces))

        # Expected: (500*500) / (2500*1250) * 100 = 8.0%
        expected = (500 * 500) / (2500 * 1250) * 100
        assert abs(result.utilization_rate - expected) < 0.1

    def test_utilization_rate_between_0_and_100(self):
        pieces = [
            Piece(id="U2", label="U2", width=200, height=100, quantity=20),
        ]
        result = solve_nesting(make_request(pieces))

        assert 0 <= result.utilization_rate <= 100


# ─────────────────────────────────────────────────
# Test: Cut type determination
# ─────────────────────────────────────────────────
class TestCutType:
    def test_laser_for_thin_sheet(self):
        pieces = [Piece(id="L1", label="L1", width=100, height=100)]
        result = solve_nesting(make_request(pieces, thickness=8.0))
        assert result.cut_type == "laser"

    def test_plasma_for_thick_sheet(self):
        pieces = [Piece(id="L2", label="L2", width=100, height=100)]
        result = solve_nesting(make_request(pieces, thickness=20.0))
        assert result.cut_type == "plasma"

    def test_plasma_at_boundary(self):
        pieces = [Piece(id="L3", label="L3", width=100, height=100)]
        result = solve_nesting(make_request(pieces, thickness=15.0))
        assert result.cut_type == "plasma"  # >= 15 → plasma


# ─────────────────────────────────────────────────
# Test: DXF generation
# ─────────────────────────────────────────────────
class TestDXFGeneration:
    def test_dxf_is_valid(self):
        """Generated DXF should be parseable by ezdxf."""
        pieces = [
            Piece(id="D1", label="DXF Test", width=300, height=200, quantity=2),
        ]
        result = solve_nesting(make_request(pieces))
        dxf_bytes = generate_dxf(result)

        assert len(dxf_bytes) > 0

        # Parse the generated DXF to validate structure
        import io
        doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8")))
        msp = doc.modelspace()

        # Should have entities: sheet outline + margin + cuts + labels + info
        entities = list(msp)
        assert len(entities) > 0

    def test_dxf_has_correct_layers(self):
        """DXF should contain all expected layers."""
        pieces = [
            Piece(id="D2", label="Layer Test", width=200, height=150),
        ]
        result = solve_nesting(make_request(pieces))
        dxf_bytes = generate_dxf(result)

        import io
        doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8")))

        layer_names = [layer.dxf.name for layer in doc.layers]
        assert "SHEET_OUTLINE" in layer_names
        assert "CUT_LINES" in layer_names
        assert "LABELS" in layer_names
        assert "INFO" in layer_names
