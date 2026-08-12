"""
Pydantic models for the OptiTôle Nesting API.
Defines request/response schemas for sheet metal nesting operations.
"""

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

class Piece(BaseModel):
    """A single rectangular piece to be nested on the sheet."""

    id: str = Field(..., description="Unique identifier (e.g. 'PL-001')")
    label: str = Field(..., description="Display name (e.g. 'Gousset G1')")
    width: float = Field(..., gt=0, description="Width in mm")
    height: float = Field(..., gt=0, description="Height in mm")
    quantity: int = Field(default=1, ge=1, description="Number of copies needed")
    allow_rotation: bool = Field(
        default=True,
        description="Whether the piece can be rotated 90° for better fit",
    )


class NestingRequest(BaseModel):
    """Full nesting request: sheet dimensions + pieces + cutting parameters."""

    # Sheet dimensions
    sheet_width: float = Field(
        default=2500.0, gt=0, description="Sheet width in mm"
    )
    sheet_height: float = Field(
        default=1250.0, gt=0, description="Sheet height in mm"
    )
    thickness: float = Field(
        default=10.0, gt=0, description="Sheet thickness in mm (determines laser vs plasma)"
    )

    # Cutting parameters
    kerf: float = Field(
        default=5.0,
        ge=0,
        description="Minimum spacing between pieces in mm (inter-piece clearance)",
    )
    sheet_margin: float = Field(
        default=10.0,
        ge=0,
        description="Border margin from sheet edges in mm (for clamps/edge defects)",
    )

    # Pieces to nest
    pieces: list[Piece] = Field(
        ..., min_length=1, description="List of pieces to nest"
    )


# ──────────────────────────────────────────────
# Response Models
# ──────────────────────────────────────────────

class PlacedPiece(BaseModel):
    """A piece that was successfully placed on the sheet."""

    id: str
    label: str
    x: float = Field(..., description="X coordinate of bottom-left corner (mm)")
    y: float = Field(..., description="Y coordinate of bottom-left corner (mm)")
    width: float = Field(..., description="Effective width after potential rotation (mm)")
    height: float = Field(..., description="Effective height after potential rotation (mm)")
    rotated: bool = Field(
        default=False, description="Whether the piece was rotated 90°"
    )


class UnplacedPiece(BaseModel):
    """A piece that could not fit on the sheet."""

    id: str
    label: str
    width: float
    height: float


class NestingResult(BaseModel):
    """Result of the nesting optimization."""

    # Placed pieces with coordinates
    placed_pieces: list[PlacedPiece]

    # Pieces that didn't fit
    unplaced_pieces: list[UnplacedPiece]

    # Statistics
    utilization_rate: float = Field(
        ..., description="Material utilization percentage (0-100)"
    )
    total_requested: int = Field(
        ..., description="Total number of piece instances requested"
    )
    total_placed: int = Field(
        ..., description="Total number of piece instances placed"
    )

    # Cut type determination
    cut_type: str = Field(
        ..., description="'laser' if thickness < 15mm, 'plasma' otherwise"
    )

    # Sheet info (echoed back for frontend convenience)
    sheet_width: float
    sheet_height: float
    sheet_margin: float
    kerf: float
