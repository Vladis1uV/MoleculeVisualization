from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem.Descriptors import ExactMolWt
import base64
from io import BytesIO
import os
from utils.molecule_utils import get_molecule_data, generate_3d_coordinates

app = Flask(__name__)
CORS(app)

# PubChem API base URL
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_by_formula', methods=['POST'])
def search_by_formula():
    """Search molecules by chemical formula"""
    data = request.json
    formula = data.get('formula', '').strip()
    
    if not formula:
        return jsonify({'error': 'Formula is required'}), 400
    
    try:
        # Search PubChem by formula
        url = f"{PUBCHEM_BASE_URL}/compound/fastformula/{formula}/JSON"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            compounds = data.get('PC_Compounds', [])
            
            results = []
            for compound in compounds[:10]:  # Limit to first 10 results
                # Get CID
                cid = compound.get('id', {}).get('id', {}).get('cid', 'N/A')
                
                # Get properties
                props = {}
                if 'props' in compound:
                    for prop in compound['props']:
                        if 'urn' in prop and 'value' in prop:
                            label = prop['urn'].get('label', '')
                            if label:
                                props[label] = prop['value'].get('sval', prop['value'].get('fval', 'N/A'))
                
                # Try to get IUPAC name
                name_url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/property/IUPACName/JSON"
                name_response = requests.get(name_url)
                name = "Unknown"
                if name_response.status_code == 200:
                    name_data = name_response.json()
                    if 'PropertyTable' in name_data and 'Properties' in name_data['PropertyTable']:
                        name = name_data['PropertyTable']['Properties'][0].get('IUPACName', 'Unknown')
                
                results.append({
                    'cid': cid,
                    'name': name,
                    'formula': formula,
                    'properties': props
                })
            
            return jsonify({'results': results})
        else:
            return jsonify({'error': 'No compounds found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_molecule_3d', methods=['POST'])
def get_molecule_3d():
    """Get 3D structure data for a molecule by CID"""
    data = request.json
    cid = data.get('cid')
    
    if not cid:
        return jsonify({'error': 'CID is required'}), 400
    
    try:
        # First try to get 3D structure
        url_3d = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/SDF?record_type=3d"
        response_3d = requests.get(url_3d)
        
        if response_3d.status_code == 200:
            sdf_data = response_3d.text
            
            # Parse with RDKit
            mol = Chem.MolFromMolBlock(sdf_data)
            
            if mol:
                # Generate 3D coordinates if not present
                if mol.GetNumConformers() == 0:
                    mol = generate_3d_coordinates(mol)
                
                # Get atomic data
                atoms = []
                conformer = mol.GetConformer()
                
                for i, atom in enumerate(mol.GetAtoms()):
                    pos = conformer.GetAtomPosition(i)
                    atoms.append({
                        'element': atom.GetSymbol(),
                        'x': float(pos.x),
                        'y': float(pos.y),
                        'z': float(pos.z),
                        'atomic_number': atom.GetAtomicNum(),
                        'index': i
                    })
                
                # Get bond data
                bonds = []
                for bond in mol.GetBonds():
                    bonds.append({
                        'start': bond.GetBeginAtomIdx(),
                        'end': bond.GetEndAtomIdx(),
                        'type': str(bond.GetBondType()),
                        'order': bond.GetBondTypeAsDouble()
                    })
                
                # Get molecule properties
                formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
                molecular_weight = ExactMolWt(mol)
                
                # Generate 2D structure image
                img = Draw.MolToImage(mol, size=(300, 300))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Get SMILES
                smiles = Chem.MolToSmiles(mol)
                
                return jsonify({
                    'atoms': atoms,
                    'bonds': bonds,
                    'formula': formula,
                    'molecular_weight': molecular_weight,
                    'num_atoms': len(atoms),
                    'num_bonds': len(bonds),
                    'smiles': smiles,
                    '2d_structure': f"data:image/png;base64,{img_str}",
                    'sdf': sdf_data
                })
        
        # If 3D structure not available, try 2D structure
        url_2d = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/SDF"
        response_2d = requests.get(url_2d)
        
        if response_2d.status_code == 200:
            sdf_data = response_2d.text
            mol = Chem.MolFromMolBlock(sdf_data)
            
            if mol:
                # Generate 3D coordinates
                mol = generate_3d_coordinates(mol)
                
                # Get atomic data
                atoms = []
                conformer = mol.GetConformer()
                
                for i, atom in enumerate(mol.GetAtoms()):
                    pos = conformer.GetAtomPosition(i)
                    atoms.append({
                        'element': atom.GetSymbol(),
                        'x': float(pos.x),
                        'y': float(pos.y),
                        'z': float(pos.z),
                        'atomic_number': atom.GetAtomicNum(),
                        'index': i
                    })
                
                # Get bond data
                bonds = []
                for bond in mol.GetBonds():
                    bonds.append({
                        'start': bond.GetBeginAtomIdx(),
                        'end': bond.GetEndAtomIdx(),
                        'type': str(bond.GetBondType()),
                        'order': bond.GetBondTypeAsDouble()
                    })
                
                # Get molecule properties
                formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
                molecular_weight = ExactMolWt(mol)
                
                # Generate 2D structure image
                img = Draw.MolToImage(mol, size=(300, 300))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Get SMILES
                smiles = Chem.MolToSmiles(mol)
                
                return jsonify({
                    'atoms': atoms,
                    'bonds': bonds,
                    'formula': formula,
                    'molecular_weight': molecular_weight,
                    'num_atoms': len(atoms),
                    'num_bonds': len(bonds),
                    'smiles': smiles,
                    '2d_structure': f"data:image/png;base64,{img_str}",
                    'sdf': sdf_data
                })
        
        return jsonify({'error': 'Failed to fetch molecule data'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate_properties', methods=['POST'])
def calculate_properties():
    """Calculate additional molecular properties"""
    data = request.json
    smiles = data.get('smiles', '')
    
    if not smiles:
        return jsonify({'error': 'SMILES is required'}), 400
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            from rdkit.Chem import Descriptors, Lipinski, Crippen
            
            properties = {
                'molecular_weight': Descriptors.ExactMolWt(mol),
                'logp': Crippen.MolLogP(mol),
                'h_bond_donors': Lipinski.NumHDonors(mol),
                'h_bond_acceptors': Lipinski.NumHAcceptors(mol),
                'rotatable_bonds': Lipinski.NumRotatableBonds(mol),
                'tpsa': Descriptors.TPSA(mol),
                'num_atoms': mol.GetNumAtoms(),
                'num_bonds': mol.GetNumBonds(),
                'aromatic_rings': Descriptors.NumAromaticRings(mol),
                'heavy_atoms': Lipinski.HeavyAtomCount(mol)
            }
            
            return jsonify(properties)
        else:
            return jsonify({'error': 'Invalid SMILES'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert_smiles', methods=['POST'])
def convert_smiles():
    """Convert SMILES to 3D structure"""
    data = request.json
    smiles = data.get('smiles', '')
    
    if not smiles:
        return jsonify({'error': 'SMILES is required'}), 400
    
    try:
        # Convert SMILES to molecule
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return jsonify({'error': 'Invalid SMILES string'}), 400
        
        # Generate 3D coordinates
        mol = generate_3d_coordinates(mol)
        
        # Get atomic data
        atoms = []
        conformer = mol.GetConformer()
        
        for i, atom in enumerate(mol.GetAtoms()):
            pos = conformer.GetAtomPosition(i)
            atoms.append({
                'element': atom.GetSymbol(),
                'x': float(pos.x),
                'y': float(pos.y),
                'z': float(pos.z),
                'atomic_number': atom.GetAtomicNum(),
                'index': i
            })
        
        # Get bond data
        bonds = []
        for bond in mol.GetBonds():
            bonds.append({
                'start': bond.GetBeginAtomIdx(),
                'end': bond.GetEndAtomIdx(),
                'type': str(bond.GetBondType()),
                'order': bond.GetBondTypeAsDouble()
            })
        
        # Get molecule properties
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        molecular_weight = ExactMolWt(mol)
        
        # Generate 2D structure image
        img = Draw.MolToImage(mol, size=(300, 300))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'atoms': atoms,
            'bonds': bonds,
            'formula': formula,
            'molecular_weight': molecular_weight,
            'num_atoms': len(atoms),
            'num_bonds': len(bonds),
            'smiles': smiles,
            '2d_structure': f"data:image/png;base64,{img_str}"
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_molecule_info', methods=['POST'])
def get_molecule_info():
    """Get comprehensive molecule information by CID"""
    data = request.json
    cid = data.get('cid')
    
    if not cid:
        return jsonify({'error': 'CID is required'}), 400
    
    try:
        # Get compound record
        url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/JSON"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            compound_info = {
                'cid': cid,
                'properties': {},
                'synonyms': []
            }
            
            # Get properties
            if 'PC_Compound' in data:
                compound = data['PC_Compound']
                for prop in compound.get('props', []):
                    if 'urn' in prop and 'label' in prop['urn']:
                        label = prop['urn']['label']
                        if 'value' in prop:
                            if 'sval' in prop['value']:
                                compound_info['properties'][label] = prop['value']['sval']
                            elif 'fval' in prop['value']:
                                compound_info['properties'][label] = prop['value']['fval']
                            elif 'ival' in prop['value']:
                                compound_info['properties'][label] = prop['value']['ival']
            
            # Get synonyms
            synonyms_url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/synonyms/JSON"
            synonyms_response = requests.get(synonyms_url)
            if synonyms_response.status_code == 200:
                synonyms_data = synonyms_response.json()
                if 'InformationList' in synonyms_data and 'Information' in synonyms_data['InformationList']:
                    for info in synonyms_data['InformationList']['Information']:
                        if 'Synonym' in info:
                            compound_info['synonyms'] = info['Synonym'][:10]  # Limit to 10 synonyms
            
            return jsonify(compound_info)
        else:
            return jsonify({'error': 'Failed to fetch molecule information'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']

    app.run(host='0.0.0.0', port=port, debug=debug)