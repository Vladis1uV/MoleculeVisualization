from flask import Flask, render_template, request, send_file, jsonify
from molecule_fetcher import (
    fetch_molecule_info, 
    generate_3d_molecule, 
    save_molecule,
    save_molecule_from_smiles,
    cleanup_old_files
)
import os
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Clean up old files first
        cleanup_old_files()
        
        formula = request.form.get("formula", "").strip()
        smiles = request.form.get("smiles", "").strip()
        
        if not formula and not smiles:
            return render_template("index.html", error="Please enter a molecule name or SMILES string")
        
        search_query = formula if formula else smiles
        search_type = "name" if formula else "smiles"
        
        # Fetch molecule info
        mol_info = fetch_molecule_info(search_query)
        
        if "error" in mol_info:
            return render_template("index.html", error=mol_info["error"])
        
        # Handle multiple isomers
        if mol_info.get("type") == "multiple":
            return render_template("index.html", 
                                 isomers=mol_info["isomers"],
                                 search_query=search_query)
        
        # Handle single molecule
        if mol_info.get("type") == "single":
            # Generate 3D structure
            smiles = mol_info.get("smiles")
            if not smiles:
                return render_template("index.html", error="No SMILES string available")
            
            mol_file = save_molecule_from_smiles(smiles)
            
            if mol_file:
                return render_template("index.html",
                                     mol_file=mol_file,
                                     formula=mol_info.get("formula") or search_query,
                                     mol_info=mol_info,
                                     success=True)
            else:
                return render_template("index.html", 
                                     error="Failed to generate 3D structure")
    
    return render_template("index.html")

@app.route("/molecule/<filename>")
def serve_molecule(filename):
    """Serve molecule file."""
    path = os.path.join("molecules", "temp", filename)
    if os.path.exists(path):
        return send_file(path, mimetype='chemical/x-mdl-molfile')
    return "File not found", 404

@app.route("/api/search", methods=["POST"])
def api_search():
    """API endpoint for AJAX searches."""
    data = request.get_json()
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    mol_info = fetch_molecule_info(query)
    
    # If single molecule, generate 3D structure
    if mol_info.get("type") == "single":
        smiles = mol_info.get("smiles")
        if smiles:
            mol_file = save_molecule_from_smiles(smiles)
            if mol_file:
                filename = os.path.basename(mol_file)
                mol_info["mol_file"] = f"/molecule/{filename}"
    
    return jsonify(mol_info)

@app.route("/api/generate_3d", methods=["POST"])
def api_generate_3d():
    """Generate 3D structure from SMILES."""
    data = request.get_json()
    smiles = data.get("smiles", "").strip()
    cid = data.get("cid")
    
    if not smiles:
        return jsonify({"error": "No SMILES provided"}), 400
    
    mol_file = save_molecule_from_smiles(smiles)
    
    if mol_file:
        filename = os.path.basename(mol_file)
        return jsonify({
            "success": True,
            "mol_file": f"/molecule/{filename}",
            "cid": cid
        })
    
    return jsonify({"error": "Failed to generate 3D structure"}), 500

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("molecules/temp", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)