# OptiTôle - Logiciel d'Optimisation de Découpe (Nesting)

OptiTôle est un logiciel de placement 2D (nesting) conçu pour optimiser la découpe de pièces sur des plaques de tôle (laser, plasma, jet d'eau). L'application place intelligemment des pièces de formes variées sur une surface rectangulaire afin de minimiser les chutes et d'augmenter le taux d'utilisation de la matière.

## Fonctionnalités Principales

- **Import de Pièces** : Import de fichiers DXF contenant les géométries des pièces à découper.
- **Paramétrage** : Définition des dimensions de la tôle brute (longueur et largeur).
- **Moteur de Placement (Nesting)** : Algorithme basé sur la méthode No-Fit-Polygon pour un agencement ultra-optimisé, avec rotation libre des pièces.
- **Export DXF** : Génération d'un fichier DXF prêt à être envoyé à la machine de découpe, contenant les pièces imbriquées de manière optimale.
- **Logiciel de Bureau Indépendant** : L'application est un exécutable natif ne nécessitant aucune installation de Node.js ou Python chez l'utilisateur final.

## Architecture

Le projet est divisé en deux parties principales empaquetées dans une coquille Electron :

1. **Frontend (Next.js / React)** : Interface utilisateur moderne, ergonomique et réactive, permettant la visualisation en direct (canvas) des pièces importées et du résultat de l'imbrication.
2. **Backend (FastAPI / Python)** : Moteur de calcul robuste intégrant `ezdxf` pour la manipulation des fichiers géométriques et des librairies de traitement polygonale (Shapely) pour les calculs de collision et de placement.

## Instructions de Développement

### Prérequis
- [Node.js](https://nodejs.org/)
- [Python 3.12](https://www.python.org/)

### Lancement en mode développement

1. **Démarrer le backend (FastAPI)**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Démarrer le frontend (Next.js)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Compilation de l'application Windows (.exe)

L'application peut être compilée en un exécutable autonome (standalone) grâce à Electron et PyInstaller :

```bash
# À la racine du projet
npm install
npm run build:app
```
> Le logiciel final (.exe) sera généré dans le dossier `dist/`.

## Technologies

- **Frontend** : Next.js, React, Tailwind CSS
- **Backend** : Python, FastAPI, ezdxf, Shapely
- **Desktop Wrapper** : Electron, @electron/packager, PyInstaller

---

*Développé dans le cadre d'un stage de développement d'outils industriels.*
