# OptiTole - Cutting Optimization Software (Nesting)

OptiTole is a 2D nesting software designed to optimize the cutting of parts on sheet metal (laser, plasma, waterjet). The application intelligently places variously shaped parts on a rectangular surface to minimize scrap and increase material utilization.

## Key Features

- **Part Import**: Import DXF files containing the geometries of the parts to be cut.
- **Configuration**: Define the dimensions of the raw sheet metal (length and width).
- **Nesting Engine**: Algorithm based on the No-Fit-Polygon method for highly optimized layout, with free rotation of parts.
- **DXF Export**: Generation of a DXF file ready to be sent to the cutting machine, containing the optimally nested parts.
- **Standalone Desktop Software**: The application is a native executable requiring no installation of Node.js or Python on the end user's machine.

## Architecture

The project is divided into two main parts packaged within an Electron shell:

1. **Frontend (Next.js / React)**: Modern, ergonomic, and responsive user interface, allowing live visualization (canvas) of imported parts and the nesting result.
2. **Backend (FastAPI / Python)**: Robust calculation engine integrating `ezdxf` for manipulating geometric files and polygon processing libraries (Shapely) for collision and placement calculations.

## Development Instructions

### Prerequisites
- [Node.js](https://nodejs.org/)
- [Python 3.12](https://www.python.org/)

### Launching in Development Mode

1. **Start the backend (FastAPI)**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Start the frontend (Next.js)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Compiling the Windows Application (.exe)

The application can be compiled into a standalone executable using Electron and PyInstaller:

```bash
# At the root of the project
npm install
npm run build:app
```
> The final software (.exe) will be generated in the `dist/` folder.

## Technologies

- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: Python, FastAPI, ezdxf, Shapely
- **Desktop Wrapper**: Electron, @electron/packager, PyInstaller

---

*Developed as part of an industrial tool development internship.*
