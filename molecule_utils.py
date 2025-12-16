import requests
import time
from rdkit import Chem
from rdkit.Chem import AllChem, rdmolfiles
import os
import uuid

BASE_FOLDER = "molecules/temp"
os.makedirs(BASE_FOLDER, exist_ok=True)

def fetch_molecule_smiles(name, max_wait=20):
    """Fetch SMILES from PubChem and handle waiting response"""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/CanonicalSMILES/JSON"
    response = requests.get(url)
    wait_time = 0

    while response.status_code == 202 or ("Waiting" in response.text):
        data = response.json()
        if "Waiting" in data:
            list_key = data["Waiting"]["ListKey"]
            time.sleep(1)
            wait_time += 1
            if wait_time > max_wait:
                return None
            response = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/listkey/{list_key}/property/CanonicalSMILES/JSON")
        else:
            break

    if response.status_code == 200:
        data = response.json()
        try:
            smiles = data['PropertyTable']['Properties'][0]['ConnectivitySMILES']
            return smiles
        except (KeyError, IndexError):
            return None
    return None

def generate_3d_molecule(smiles):
    """Generate 3D RDKit molecule from SMILES"""
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    return mol

def save_molecule(mol):
    """Save molecule as MOL file with unique filename"""
    filename = os.path.join(BASE_FOLDER, f"{uuid.uuid4().hex}.mol")
    rdmolfiles.MolToMolFile(mol, filename)
    return filename
