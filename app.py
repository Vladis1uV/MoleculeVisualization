from flask import Flask, render_template, request, send_file
from molecule_utils import fetch_molecule_smiles, generate_3d_molecule, save_molecule, cleanup_old_files
import os


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    mol_file = None
    formula = None
    error = None

    if request.method == "POST":
        formula = request.form.get("formula")
        if formula:
            # Clean up old files first
            cleanup_old_files()

            smiles = fetch_molecule_smiles(formula)
            if smiles:
                mol = generate_3d_molecule(smiles)
                mol_file = save_molecule(mol)
            else:
                error = "Molecule not found or request timed out."
        else:
            error = "Please enter a molecule formula."

    return render_template("index.html", mol_file=mol_file, formula=formula, error=error)

@app.route("/molecule/<filename>")
def serve_molecule(filename):
    path = os.path.join("molecules", "temp", filename)
    if os.path.exists(path):
        return send_file(path)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
