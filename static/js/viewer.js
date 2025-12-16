function displayMolecule(molFile, containerId) {
    fetch(molFile)
        .then(response => response.text())
        .then(molData => {
            let viewer = $3Dmol.createViewer(containerId, {backgroundColor: "white"});
            viewer.addModel(molData, "mol");
            viewer.setStyle({}, {stick:{}});
            viewer.zoomTo();
            viewer.render();
        })
        .catch(err => console.error("Error loading molecule:", err));
}
