import sys
import ezdxf
from ezdxf.audit import Auditor
from models import NestingResult, PlacedPiece, UnplacedPiece

result = NestingResult(
    placed_pieces=[
        PlacedPiece(id='P1', label='P1', x=10, y=10, width=100, height=100, rotated=False)
    ],
    unplaced_pieces=[],
    utilization_rate=50.0,
    total_requested=1,
    total_placed=1,
    cut_type='laser',
    sheet_width=1000,
    sheet_height=1000,
    sheet_margin=10,
    kerf=3
)

from dxf_generator import generate_dxf
dxf_bytes = generate_dxf(result)
with open('test_autocad.dxf', 'wb') as f:
    f.write(dxf_bytes)

doc = ezdxf.readfile('test_autocad.dxf')
auditor = Auditor(doc)
auditor.run()

if len(auditor.errors) > 0:
    print('Errors found:')
    for e in auditor.errors:
        print(e)
else:
    print('No errors found in DXF.')
