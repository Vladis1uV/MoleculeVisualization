from flask import Flask, render_template, request, send_file
import io
import requests
from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image
import base64

app = Flask(__name__)

class MoleculeVisualizer:
    def __init__(self):
        self.pubchem_base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def formula_to_smiles(self, formula):
        """Convert molecular formula to SMILES using PubChem"""
        try:
            url = f"{self.pubchem_base_url}/compound/fastformula/{formula}/property/CanonicalSMILES/JSON"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                compounds = data.get('PropertyTable', {}).get('Properties', [])
                if compounds:
                    # Return the first compound's SMILES
                    return compounds[0].get('ConnectivitySMILES')
            return None
        except Exception as e:
            print(f"Error fetching from PubChem: {e}")
            return None
    
    def smiles_to_image(self, smiles):
        """Convert SMILES to molecular structure image"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                img = Draw.MolToImage(mol, size=(400, 400))
                return img
            return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def image_to_base64(self, img):
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

visualizer = MoleculeVisualizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_molecule():
    formula = request.form.get('formula', '').strip()
    
    if not formula:
        return render_template('index.html', error="Please enter a molecular formula")
    
    # Get SMILES from PubChem
    smiles = visualizer.formula_to_smiles(formula)
    
    if not smiles:
        return render_template('index.html', error=f"No molecule found for formula: {formula}")
    
    # Generate molecular image
    img = visualizer.smiles_to_image(smiles)
    
    if img:
        img_data = visualizer.image_to_base64(img)
        return render_template('result.html', 
                             formula=formula, 
                             smiles=smiles, 
                             image_data=img_data)
    else:
        return render_template('index.html', error="Could not generate molecular structure")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)