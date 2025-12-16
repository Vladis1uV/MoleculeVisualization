import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem, rdmolfiles
import os
import uuid
import time
import glob

BASE_FOLDER = "molecules/temp"
os.makedirs(BASE_FOLDER, exist_ok=True)

def cleanup_old_files(folder="molecules/temp", max_age_sec=300):
    """Delete .mol files older than max_age_sec seconds."""
    now = time.time()
    for f in glob.glob(os.path.join(folder, "*.mol")):
        if now - os.path.getmtime(f) > max_age_sec:
            os.remove(f)

def fetch_molecule_info(name):
    """
    Fetch molecule information using pubchempy.
    Returns: {
        'smiles': str,
        'iupac_name': str,
        'molecular_formula': str,
        'molecular_weight': float,
        'cid': int,
        'isomers': list (if multiple found)
    }
    """
    try:
        # Search for compounds by name
        compounds = pcp.get_compounds(name, 'name')
        
        if not compounds:
            return {'error': 'No compounds found'}
        
        if len(compounds) > 1:
            # Multiple compounds found - return isomers list
            isomers = []
            for compound in compounds[:5]:  # Limit to 5 for performance
                try:
                    # Use connectivity_smiles instead of canonical_smiles
                    smiles = compound.connectivity_smiles
                    if smiles:
                        isomers.append({
                            'cid': compound.cid,
                            'name': compound.iupac_name or compound.synonyms[0] if compound.synonyms else f"CID_{compound.cid}",
                            'formula': compound.molecular_formula,
                            'weight': compound.molecular_weight,
                            'smiles': smiles
                        })
                except:
                    continue
            
            return {
                'type': 'multiple',
                'isomers': isomers,
                'count': len(compounds)
            }
        
        # Single compound found
        compound = compounds[0]
        
        # Try to get 3D conformer if available
        try:
            # Get compound with 3D conformer
            compound_3d = pcp.Compound.from_cid(compound.cid, record_type='3d')
            if compound_3d and hasattr(compound_3d, 'to_dict'):
                # Use PubChem's 3D structure if available
                return {
                    'type': 'single',
                    'cid': compound.cid,
                    'smiles': compound.connectivity_smiles,  # Fixed here
                    'iupac_name': compound.iupac_name,
                    'formula': compound.molecular_formula,
                    'weight': compound.molecular_weight,
                    'synonyms': compound.synonyms[:5] if compound.synonyms else [],
                    'has_3d': True,
                    'pubchem_3d': compound_3d.to_dict() if hasattr(compound_3d, 'to_dict') else None
                }
        except:
            pass  # Fall back to RDKit generation
        
        return {
            'type': 'single',
            'cid': compound.cid,
            'smiles': compound.connectivity_smiles,  # Fixed here
            'iupac_name': compound.iupac_name,
            'formula': compound.molecular_formula,
            'weight': compound.molecular_weight,
            'synonyms': compound.synonyms[:5] if compound.synonyms else [],
            'has_3d': False
        }
        
    except pcp.BadRequestError:
        return {'error': 'Invalid request'}
    except pcp.NotFoundError:
        return {'error': 'Compound not found'}
    except Exception as e:
        return {'error': f'Error fetching data: {str(e)}'}

def generate_3d_molecule(smiles, optimize=True):
    """
    Generate 3D molecule from SMILES using RDKit.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        # Add hydrogens
        mol = Chem.AddHs(mol)
        
        # Generate 3D coordinates
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        
        # Optimize geometry (optional but recommended)
        if optimize:
            AllChem.UFFOptimizeMolecule(mol)
        
        return mol
    except Exception as e:
        print(f"Error generating 3D molecule: {e}")
        return None

def save_molecule(mol, filename=None):
    """
    Save molecule as MOL file.
    """
    if mol is None:
        return None
    
    if filename is None:
        filename = f"{uuid.uuid4().hex}.mol"
    
    filepath = os.path.join(BASE_FOLDER, filename)
    
    try:
        rdmolfiles.MolToMolFile(mol, filepath)
        return filepath
    except Exception as e:
        print(f"Error saving molecule: {e}")
        return None

def save_molecule_from_smiles(smiles, filename=None):
    """
    Generate and save 3D molecule from SMILES.
    """
    mol = generate_3d_molecule(smiles)
    if mol:
        return save_molecule(mol, filename)
    return None