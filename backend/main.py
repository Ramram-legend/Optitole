"""
OptiTôle Nesting API — FastAPI server for sheet metal nesting optimization.

Endpoints:
  POST /api/preview  — Returns JSON with placement coordinates (for canvas preview)
  POST /api/nest     — Returns a downloadable DXF file with the nesting layout
  GET  /api/health   — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from models import NestingRequest, NestingResult
from nesting_engine import solve_nesting
from dxf_generator import generate_dxf

app = FastAPI(
    title="OptiTôle Nesting API",
    description="API d'optimisation de découpe laser/plasma pour l'imbrication de pièces sur tôle",
    version="1.0.0",
)

# ──────────────────────────────────────
# CORS — Allow Next.js frontend
# ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Utilization-Rate", "X-Pieces-Placed", "X-Pieces-Total"],
)


# ──────────────────────────────────────
# Health check
# ──────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "OptiTôle Nesting API"}


# ──────────────────────────────────────
# Preview — Returns JSON coordinates
# ──────────────────────────────────────
@app.post("/api/preview", response_model=NestingResult)
async def preview_nesting(request: NestingRequest):
    """
    Calculate the optimal nesting layout and return the result as JSON.
    Used by the frontend to render the SVG/Canvas preview.
    """
    try:
        result = solve_nesting(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nesting calculation failed: {str(e)}")


# ──────────────────────────────────────
# Export DXF — Returns binary file
# ──────────────────────────────────────
@app.post("/api/nest")
async def export_dxf(request: NestingRequest):
    """
    Calculate the optimal nesting layout and generate a DXF file.
    Returns the DXF as a downloadable binary response.
    """
    try:
        result = solve_nesting(request)

        if result.total_placed == 0:
            raise HTTPException(
                status_code=422,
                detail="Aucune pièce n'a pu être placée sur la tôle. "
                       "Vérifiez que les dimensions des pièces sont compatibles "
                       "avec la tôle et les marges.",
            )

        dxf_bytes = generate_dxf(result)

        # Build a descriptive filename
        filename = (
            f"nesting_{result.sheet_width:.0f}x{result.sheet_height:.0f}"
            f"_{result.cut_type}"
            f"_{result.total_placed}pieces.dxf"
        )

        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Utilization-Rate": f"{result.utilization_rate:.1f}",
                "X-Pieces-Placed": str(result.total_placed),
                "X-Pieces-Total": str(result.total_requested),
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DXF generation failed: {str(e)}")


# ──────────────────────────────────────
# Run with: uvicorn main:app --reload --port 8000
# ──────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import sys
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
