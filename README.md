# 🔬 Molecule 3D Visualization Web Application

A modern web application for searching, visualizing, and analyzing molecular structures in 3D using chemical formulas. Built with Flask, RDKit, PubChem API, and Three.js.

![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Flask](https://img.shields.io/badge/flask-2.3.2-red)
![RDKit](https://img.shields.io/badge/rdkit-2023.3.2-blue)
![Three.js](https://img.shields.io/badge/three.js-0.132.2-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🌟 Features

-  Formula-based Search: Search molecules by chemical formula (e.g., C6H6, H2O, C9H8O4)
-  Interactive 3D Visualization: Real-time 3D molecular viewer with CPK coloring
-  Molecular Properties: Display formula, molecular weight, atom/bond counts
-  Interactive Controls: Rotate, zoom, pan the 3D model
-  2D Structure Display: View 2D molecular structure alongside 3D
-  Export Functionality: Save visualizations as PNG images
-  Atom Labels: Clear identification of elements with labels
-  Fast Results: Fetches data from PubChem database

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Vladis1uV/MoleculeVisualization.git
cd MoleculeVisualization
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
### 5. Open in Browser

Navigate to http://localhost:5000

## 📁 Project Structure
```text
MoleculeVisualization/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore file
├── static/
│   ├── css/
│   │   └── style.css          # Stylesheets
│   └── js/
│       └── visualizer.js      # Three.js visualization logic
├── templates/
│   └── index.html             # Main HTML page
└── utils/
    └── molecule_utils.py      # Molecular processing utilities
```
### 🧪 Implementation Details
Backend Architecture
#### 1. Flask API Endpoints
 - /search_by_formula: Searches PubChem by chemical formula

 - /get_molecule_3d: Retrieves 3D molecular structure data

 - /calculate_properties: Computes molecular properties

 - /convert_smiles: Converts SMILES to 3D structure

#### 2. Molecular Processing Pipeline
```python
1. User inputs formula → 2. Query PubChem API → 3. Fetch SDF data
4. Parse with RDKit → 5. Generate 3D coordinates → 6. Calculate properties
7. Generate 2D image → 8. Return JSON response
```

#### 3. 3D Coordinate Generation
 - Uses RDKit's ETKDGv3 algorithm for conformer generation

 - Universal Force Field (UFF) optimization for geometry

 - Fallback to 2D structures when 3D unavailable


### 🧪 Dependencies

#### Python (requirements.txt)

```txt
Flask
rdkit
requests
numpy
flask-cors
```

#### JavaScript Libraries (CDN)

 - Three.js (v0.132.2)

 - OrbitControls.js

 - GLTFLoader.js

### 🚀 Deployment

#### Local Development
```bash
# Run with debug mode
python app.py

# Run on specific port
# Using environment variable
PORT=8080 python app.py

# Or on Windows CMD:
set PORT=8080 && python app.py

# Or on Windows PowerShell:
$env:PORT=8080; python app.py
```

### 📊 Results Achieved

#### Successful Implementation

The Molecule 3D Visualization Web Application has been successfully implemented with the following key achievements:

#### Functional Features
 - ✅ Formula-based Search: Users can successfully search for molecules using chemical formulas

 - ✅ Interactive 3D Visualization: Real-time rendering of molecular structures with smooth controls

 - ✅ CPK Coloring: Accurate representation of atoms using standard chemical coloring

 - ✅ Property Display: Molecular weight, atom count, bond count, and formula display

 - ✅ 2D Structure: Simultaneous display of 2D molecular structure

 - ✅ Export Functionality: Ability to save visualizations as PNG files