"""
Nesting Engine — MaxRects bin-packing algorithm for sheet metal optimization.

Uses the rectpack library with MaxRectsBssf (Best Short Side Fit) strategy
to maximize material utilization. Kerf is handled by inflating each piece's
bounding box before packing, then mapping back to real coordinates.

Kerf Handling Strategy:
─────────────────────────────────────────────────────────────
   ┌───────────────────────────────────┐
   │  kerf/2  margin all around       │
   │  ┌───────────────────────────┐   │
   │  │   Actual piece            │   │
   │  │   (width × height)       │   │
   │  └───────────────────────────┘   │
   │                      kerf/2      │
   └───────────────────────────────────┘
     Zone allocated by rectpack:
     (width + kerf) × (height + kerf)
─────────────────────────────────────────────────────────────
This guarantees a minimum gap of `kerf` mm between any two
adjacent pieces, and between pieces and the sheet edge margin.
"""

import rectpack

from models import (
    NestingRequest,
    NestingResult,
    Piece,
    PlacedPiece,
    UnplacedPiece,
)


def solve_nesting(request: NestingRequest) -> NestingResult:
    """
    Run the nesting optimization algorithm.

    1. Shrink the usable sheet area by the sheet_margin on all sides.
    2. Inflate each piece by kerf (kerf/2 per side) for spacing.
    3. Pack using MaxRects Best Short Side Fit.
    4. Map packed coordinates back to real sheet coordinates.
    5. Return placed/unplaced pieces and utilization stats.
    """

    kerf = request.kerf
    margin = request.sheet_margin

    # ── Step 1: Compute usable sheet area (inside the margins) ──
    usable_width = request.sheet_width - (2 * margin)
    usable_height = request.sheet_height - (2 * margin)

    if usable_width <= 0 or usable_height <= 0:
        raise ValueError(
            f"Les marges de tôle ({margin}mm) sont trop grandes pour la tôle "
            f"({request.sheet_width}×{request.sheet_height}mm). "
            f"Aucune zone utilisable ne reste."
        )

    # ── Step 2: Build the packer ──
    # rectpack works with integers, so we use a scale factor (0.1mm precision)
    SCALE = 10

    packer = rectpack.newPacker(
        mode=rectpack.PackingMode.Offline,                    # Sort all rects before packing
        pack_algo=rectpack.MaxRectsBssf,                      # Best Short Side Fit
        rotation=True,                                        # Allow 90° rotation globally
    )

    # Add the usable bin (single sheet)
    bin_w = int(usable_width * SCALE)
    bin_h = int(usable_height * SCALE)
    packer.add_bin(bin_w, bin_h)

    # ── Step 3: Add all piece instances with inflated dimensions ──
    # Track each rect instance with a unique ID mapped to its source piece
    rect_registry: dict[int, dict] = {}
    rect_id = 0
    too_large_pieces: list[dict] = []

    for piece in request.pieces:
        # Inflate dimensions by kerf
        padded_w = piece.width + kerf
        padded_h = piece.height + kerf

        # Check if this piece can even fit in the usable area
        fits_normal = padded_w <= usable_width and padded_h <= usable_height
        fits_rotated = padded_h <= usable_width and padded_w <= usable_height

        if not fits_normal and not fits_rotated:
            # Piece is too large even alone — mark all copies as unplaceable
            for _ in range(piece.quantity):
                too_large_pieces.append({"piece": piece})
            continue

        # Add `quantity` copies of this piece
        for _ in range(piece.quantity):
            pw = int(padded_w * SCALE)
            ph = int(padded_h * SCALE)

            packer.add_rect(pw, ph, rid=rect_id)

            rect_registry[rect_id] = {
                "piece": piece,
                "padded_w": padded_w,
                "padded_h": padded_h,
            }
            rect_id += 1

    # ── Step 4: Run the packing algorithm ──
    packer.pack()

    # ── Step 5: Collect results ──
    placed_rids: set[int] = set()
    placed_pieces: list[PlacedPiece] = []

    # Iterate through packed rectangles
    # rect_list() returns tuples: (bin_index, x, y, width, height, rid)
    for rect_tuple in packer.rect_list():
        bin_idx, rx, ry, rw, rh, rid = rect_tuple

        if rid not in rect_registry:
            continue

        reg = rect_registry[rid]
        piece: Piece = reg["piece"]
        padded_w = reg["padded_w"]
        padded_h = reg["padded_h"]

        # Convert back from scaled integers to mm
        rx_mm = rx / SCALE
        ry_mm = ry / SCALE
        rw_mm = rw / SCALE
        rh_mm = rh / SCALE

        # Determine if the piece was rotated by rectpack
        # rectpack may swap width/height; compare with our padded dims
        expected_w = int(padded_w * SCALE)
        expected_h = int(padded_h * SCALE)
        rotated = not (rw == expected_w and rh == expected_h)

        # If piece doesn't allow rotation but was rotated, skip it
        if rotated and not piece.allow_rotation:
            continue

        # Actual piece dimensions (un-padded)
        if rotated:
            actual_w = piece.height
            actual_h = piece.width
        else:
            actual_w = piece.width
            actual_h = piece.height

        # Map to real sheet coordinates:
        # packed coords are within usable area, offset by margin + kerf/2
        real_x = rx_mm + margin + (kerf / 2)
        real_y = ry_mm + margin + (kerf / 2)

        placed_pieces.append(
            PlacedPiece(
                id=piece.id,
                label=piece.label,
                x=round(real_x, 2),
                y=round(real_y, 2),
                width=round(actual_w, 2),
                height=round(actual_h, 2),
                rotated=rotated,
            )
        )
        placed_rids.add(rid)

    # ── Step 6: Identify unplaced pieces ──
    unplaced_pieces: list[UnplacedPiece] = []

    # Pieces that were too large to even attempt
    for entry in too_large_pieces:
        piece = entry["piece"]
        unplaced_pieces.append(
            UnplacedPiece(
                id=piece.id,
                label=piece.label,
                width=piece.width,
                height=piece.height,
            )
        )

    # Pieces that were submitted but not placed by the algorithm
    for rid, reg in rect_registry.items():
        if rid not in placed_rids:
            piece = reg["piece"]
            unplaced_pieces.append(
                UnplacedPiece(
                    id=piece.id,
                    label=piece.label,
                    width=piece.width,
                    height=piece.height,
                )
            )

    # ── Step 7: Calculate utilization rate ──
    total_placed_area = sum(p.width * p.height for p in placed_pieces)
    sheet_area = request.sheet_width * request.sheet_height
    utilization_rate = round((total_placed_area / sheet_area) * 100, 2) if sheet_area > 0 else 0.0

    total_requested = sum(p.quantity for p in request.pieces)

    # Determine cut type based on thickness
    cut_type = "laser" if request.thickness < 15 else "plasma"

    return NestingResult(
        placed_pieces=placed_pieces,
        unplaced_pieces=unplaced_pieces,
        utilization_rate=utilization_rate,
        total_requested=total_requested,
        total_placed=len(placed_pieces),
        cut_type=cut_type,
        sheet_width=request.sheet_width,
        sheet_height=request.sheet_height,
        sheet_margin=request.sheet_margin,
        kerf=request.kerf,
    )
