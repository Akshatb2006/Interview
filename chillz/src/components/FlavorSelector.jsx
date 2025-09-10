import React from 'react';
import './FlavorSelector.css';

function FlavorSelector({ flavors, selectedFlavor, setSelectedFlavor }) {
    console.log("flavors in selector", flavors, selectedFlavor);


  return (
      <div className="flavor-selector">
          {flavors?.map((flavor) => {
            return (
                <>
                    <div
                        key={flavor.name}
                        className={`flavor-item ${selectedFlavor === flavor.name ? 'selected' : ''}`}
                        onClick={() => setSelectedFlavor(flavor.name)}
                    >
                        <img src={flavor.image} alt={flavor.name} className="flavor-thumbnail" />
                    </div>
                </>
            )
          })}
    </div>
  );
}

export default FlavorSelector;