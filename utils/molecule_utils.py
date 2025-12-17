from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem import rdMolDescriptors
import requests
import json

def get_molecule_data(cid):
    """Fetch molecule data from PubChem"""
    try:
        # Get compound record
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching molecule data: {e}")
        return None

def generate_3d_coordinates(mol):
    """Generate 3D coordinates for a molecule"""
    try:
        # Add hydrogens
        mol = Chem.AddHs(mol)
        
        # Generate 3D coordinates
        params = AllChem.ETKDGv3()
        params.randomSeed = 0xf00d
        params.useRandomCoords = True
        
        success = AllChem.EmbedMolecule(mol, params)
        
        if success == -1:
            # Fallback to basic embedding if ETKDG fails
            AllChem.EmbedMolecule(mol, randomSeed=0xf00d)
        
        # Optimize geometry using UFF (Universal Force Field)
        try:
            AllChem.UFFOptimizeMolecule(mol)
        except:
            # If UFF fails, try MMFF
            try:
                AllChem.MMFFOptimizeMolecule(mol)
            except:
                # If both fail, just use the embedded coordinates
                pass
        
        return mol
    except Exception as e:
        print(f"Error generating 3D coordinates: {e}")
        # Return the original molecule if 3D generation fails
        return mol

def formula_to_smiles(formula):
    """Try to convert formula to SMILES (simplified - in reality this is complex)"""
    try:
        # Search PubChem for formula and get first result's SMILES
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/{formula}/property/CanonicalSMILES/JSON"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:
                return data['PropertyTable']['Properties'][0].get('CanonicalSMILES', None)
    except Exception as e:
        print(f"Error converting formula to SMILES: {e}")
    return None

def get_molecule_properties(mol):
    """Calculate various molecular properties using RDKit"""
    if not mol:
        return {}
    
    try:
        properties = {}
        
        # Basic properties
        properties['molecular_formula'] = rdMolDescriptors.CalcMolFormula(mol)
        properties['molecular_weight'] = rdMolDescriptors.CalcExactMolWt(mol)
        properties['num_atoms'] = mol.GetNumAtoms()
        properties['num_bonds'] = mol.GetNumBonds()
        properties['num_heavy_atoms'] = rdMolDescriptors.CalcNumHeavyAtoms(mol)
        
        # Ring information
        properties['num_rings'] = rdMolDescriptors.CalcNumRings(mol)
        properties['num_aromatic_rings'] = rdMolDescriptors.CalcNumAromaticRings(mol)
        properties['num_aliphatic_rings'] = rdMolDescriptors.CalcNumAliphaticRings(mol)
        
        # Hydrogen bond information
        properties['num_h_donors'] = rdMolDescriptors.CalcNumHBD(mol)
        properties['num_h_acceptors'] = rdMolDescriptors.CalcNumHBA(mol)
        
        # Rotatable bonds
        properties['num_rotatable_bonds'] = rdMolDescriptors.CalcNumRotatableBonds(mol)
        
        # Topological polar surface area
        properties['tpsa'] = rdMolDescriptors.CalcTPSA(mol)
        
        # LogP
        from rdkit.Chem import Crippen
        properties['logp'] = Crippen.MolLogP(mol)
        
        # Atom counts
        atom_counts = {}
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1
        
        properties['atom_counts'] = atom_counts
        
        return properties
        
    except Exception as e:
        print(f"Error calculating properties: {e}")
        return {}

def create_molecule_from_formula(formula):
    """Attempt to create a molecule from formula (very simplified)"""
    # Note: This is a very simplified approach and won't work for complex formulas
    # In production, you'd need a proper structure elucidation algorithm
    
    try:
        # This is a placeholder - actual implementation would be complex
        # For now, we'll search PubChem and return the first result
        smiles = formula_to_smiles(formula)
        if smiles:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                return mol
        
        return None
    except Exception as e:
        print(f"Error creating molecule from formula: {e}")
        return None

def optimize_molecule_geometry(mol, force_field='UFF'):
    """Optimize molecule geometry using force field"""
    try:
        if force_field.upper() == 'UFF':
            # Universal Force Field
            success = AllChem.UFFOptimizeMolecule(mol)
        elif force_field.upper() == 'MMFF':
            # Merck Molecular Force Field
            success = AllChem.MMFFOptimizeMolecule(mol)
        else:
            # Default to UFF
            success = AllChem.UFFOptimizeMolecule(mol)
        
        return mol, success == 0  # Return True if optimization converged
        
    except Exception as e:
        print(f"Error optimizing geometry: {e}")
        return mol, False

def get_bond_lengths(mol):
    """Calculate all bond lengths in a molecule"""
    if not mol or mol.GetNumConformers() == 0:
        return {}
    
    try:
        bond_lengths = {}
        conformer = mol.GetConformer()
        
        for bond in mol.GetBonds():
            start_idx = bond.GetBeginAtomIdx()
            end_idx = bond.GetEndAtomIdx()
            
            start_pos = conformer.GetAtomPosition(start_idx)
            end_pos = conformer.GetAtomPosition(end_idx)
            
            # Calculate distance
            dx = start_pos.x - end_pos.x
            dy = start_pos.y - end_pos.y
            dz = start_pos.z - end_pos.z
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            bond_key = f"{bond.GetBeginAtom().GetSymbol()}{start_idx}-{bond.GetEndAtom().GetSymbol()}{end_idx}"
            bond_lengths[bond_key] = distance
        
        return bond_lengths
        
    except Exception as e:
        print(f"Error calculating bond lengths: {e}")
        return {}

def get_bond_angles(mol):
    """Calculate all bond angles in a molecule"""
    if not mol or mol.GetNumConformers() == 0:
        return {}
    
    try:
        from rdkit import Geometry
        import math
        
        bond_angles = {}
        conformer = mol.GetConformer()
        
        # Get all angles for each atom with at least 2 bonds
        for atom in mol.GetAtoms():
            if atom.GetDegree() >= 2:
                neighbors = atom.GetNeighbors()
                neighbor_indices = [n.GetIdx() for n in neighbors]
                
                # Calculate angle for each pair of neighbors
                for i in range(len(neighbor_indices)):
                    for j in range(i+1, len(neighbor_indices)):
                        idx1 = neighbor_indices[i]
                        idx2 = neighbor_indices[j]
                        center_idx = atom.GetIdx()
                        
                        v1 = conformer.GetAtomPosition(idx1) - conformer.GetAtomPosition(center_idx)
                        v2 = conformer.GetAtomPosition(idx2) - conformer.GetAtomPosition(center_idx)
                        
                        # Calculate angle
                        dot_product = v1.DotProduct(v2)
                        norm1 = v1.Length()
                        norm2 = v2.Length()
                        
                        if norm1 > 0 and norm2 > 0:
                            cos_angle = dot_product / (norm1 * norm2)
                            # Clamp to avoid numerical errors
                            cos_angle = max(-1.0, min(1.0, cos_angle))
                            angle = math.degrees(math.acos(cos_angle))
                            
                            angle_key = f"{mol.GetAtomWithIdx(idx1).GetSymbol()}{idx1}-{atom.GetSymbol()}{center_idx}-{mol.GetAtomWithIdx(idx2).GetSymbol()}{idx2}"
                            bond_angles[angle_key] = angle
        
        return bond_angles
        
    except Exception as e:
        print(f"Error calculating bond angles: {e}")
        return {}