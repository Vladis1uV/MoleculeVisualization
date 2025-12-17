let scene, camera, renderer, controls;
let moleculeGroup = new THREE.Group();
let atoms = [];
let bonds = [];
let showBonds = true;

// Atomic colors (CPK coloring)
const atomColors = {
    'H': 0xFFFFFF, 'C': 0x808080, 'N': 0x0000FF, 'O': 0xFF0000,
    'F': 0x00FF00, 'Cl': 0x00FF00, 'Br': 0x802A2A, 'I': 0x660099,
    'P': 0xFFA500, 'S': 0xFFFF00, 'B': 0xFFB5C5, 'Li': 0xCC80FF,
    'Na': 0xAB5CF2, 'K': 0x8F40D4, 'Mg': 0x8AFF00, 'Ca': 0x3DFF00,
    'Fe': 0xE06633, 'Cu': 0xC88033, 'Zn': 0x7D80B0
};

// Atomic radii (van der Waals radii scaled down for visualization)
const atomRadii = {
    'H': 0.3, 'C': 0.7, 'N': 0.65, 'O': 0.6, 'F': 0.5,
    'Cl': 1.0, 'Br': 1.15, 'I': 1.4, 'P': 1.0, 'S': 1.0
};

function init3DViewer() {
    const container = document.getElementById('moleculeViewer');
    
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a202c);
    
    // Camera
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(15, 10, 15);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 15);
    scene.add(directionalLight);
    
    // Add axes helper
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
    
    // Add molecule group
    scene.add(moleculeGroup);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation
    animate();
}

function onWindowResize() {
    const container = document.getElementById('moleculeViewer');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function searchMolecules() {
    const formula = document.getElementById('formulaInput').value.trim();
    if (!formula) {
        alert('Please enter a chemical formula');
        return;
    }
    
    fetch('/search_by_formula', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ formula: formula })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        displayResults(data.results);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error searching for molecules');
    });
}

function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsSection = document.getElementById('resultsSection');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No molecules found for this formula.</p>';
        resultsSection.style.display = 'block';
        return;
    }
    
    let html = '';
    results.forEach((mol, index) => {
        html += `
            <div class="molecule-card" onclick="loadMolecule3D(${mol.cid}, this)">
                <h4>${mol.name}</h4>
                <p><strong>CID:</strong> ${mol.cid}</p>
                <p><strong>Formula:</strong> ${mol.formula}</p>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    resultsSection.style.display = 'block';
}

function setExample(formula) {
    document.getElementById('formulaInput').value = formula;
    searchMolecules();
}

function loadMolecule3D(cid, element) {
    // Remove previous selection
    document.querySelectorAll('.molecule-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Highlight selected card
    if (element) element.classList.add('selected');
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    
    fetch('/get_molecule_3d', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cid: cid })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        renderMolecule3D(data);
        displayProperties(data);
        document.getElementById('loading').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error loading molecule');
        document.getElementById('loading').style.display = 'none';
    });
}

function renderMolecule3D(data) {
    // Clear previous molecule
    while (moleculeGroup.children.length > 0) {
        moleculeGroup.remove(moleculeGroup.children[0]);
    }
    
    atoms = [];
    bonds = [];
    
    // Center coordinates
    let center = new THREE.Vector3(0, 0, 0);
    data.atoms.forEach(atom => {
        center.x += atom.x;
        center.y += atom.y;
        center.z += atom.z;
    });
    center.divideScalar(data.atoms.length);
    
    // Create atoms
    data.atoms.forEach(atom => {
        const element = atom.element;
        const radius = atomRadii[element] || 0.7;
        const color = atomColors[element] || 0x888888;
        
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshPhongMaterial({ 
            color: color,
            shininess: 30,
            transparent: true,
            opacity: 0.9
        });
        
        const sphere = new THREE.Mesh(geometry, material);
        
        // Center the coordinates
        sphere.position.set(
            atom.x - center.x,
            atom.y - center.y,
            atom.z - center.z
        );
        
        moleculeGroup.add(sphere);
        atoms.push({ mesh: sphere, element: element, position: sphere.position });
        
        // Add atom label (always visible in this version)
        addAtomLabel(atom.element, sphere.position, atom.index);
    });
    
    // Create bonds
    if (showBonds) {
        data.bonds.forEach(bond => {
            const startPos = atoms[bond.start].position;
            const endPos = atoms[bond.end].position;
            
            const distance = startPos.distanceTo(endPos);
            const direction = new THREE.Vector3().subVectors(endPos, startPos).normalize();
            const centerPos = new THREE.Vector3().addVectors(startPos, endPos).multiplyScalar(0.5);
            
            const bondGeometry = new THREE.CylinderGeometry(0.1, 0.1, distance, 8);
            bondGeometry.rotateX(Math.PI / 2);
            
            const bondMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xCCCCCC,
                shininess: 90
            });
            
            const bondMesh = new THREE.Mesh(bondGeometry, bondMaterial);
            bondMesh.position.copy(centerPos);
            bondMesh.lookAt(endPos);
            
            moleculeGroup.add(bondMesh);
            bonds.push(bondMesh);
        });
    }
    
    // Display 2D structure
    if (data['2d_structure']) {
        const img = document.getElementById('structureImage');
        img.src = data['2d_structure'];
        img.style.display = 'block';
    }
}

function addAtomLabel(element, position, index) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 64;
    canvas.height = 32;
    
    // Draw background
    context.fillStyle = 'rgba(255, 255, 255, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw text
    context.fillStyle = '#000000';
    context.font = 'bold 24px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(element, canvas.width/2, canvas.height/2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true
    });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.copy(position);
    sprite.position.y += 1.2;
    sprite.scale.set(2, 1, 1);
    
    moleculeGroup.add(sprite);
}

function displayProperties(data) {
    const propertiesSection = document.getElementById('propertiesSection');
    const propertiesContainer = document.getElementById('propertiesContainer');
    const infoContainer = document.getElementById('infoContainer');
    
    // Display basic properties
    let html = `
        <div class="property-grid">
            <div class="property">
                <div class="property-label">Molecular Formula</div>
                <div class="property-value">${data.formula}</div>
            </div>
            <div class="property">
                <div class="property-label">Molecular Weight</div>
                <div class="property-value">${data.molecular_weight.toFixed(2)} g/mol</div>
            </div>
            <div class="property">
                <div class="property-label">Number of Atoms</div>
                <div class="property-value">${data.num_atoms}</div>
            </div>
            <div class="property">
                <div class="property-label">Number of Bonds</div>
                <div class="property-value">${data.num_bonds}</div>
            </div>
        </div>
    `;
    
    propertiesContainer.innerHTML = html;
    propertiesSection.style.display = 'block';
    
    // Display additional info
    infoContainer.innerHTML = `
        <p>Use mouse/touch to rotate, zoom, and pan the 3D model.</p>
        <p>Atom colors follow CPK coloring convention.</p>
    `;
}

function resetView() {
    controls.reset();
    camera.position.set(15, 10, 15);
    controls.update();
}

function toggleBonds() {
    showBonds = !showBonds;
    const btn = document.getElementById('toggleBondsBtn');
    btn.textContent = showBonds ? 'Hide Bonds' : 'Show Bonds';
    
    bonds.forEach(bond => {
        bond.visible = showBonds;
    });
}

function exportPNG() {
    renderer.render(scene, camera);
    const link = document.createElement('a');
    link.download = 'molecule.png';
    link.href = renderer.domElement.toDataURL('image/png');
    link.click();
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', () => {
    init3DViewer();
});