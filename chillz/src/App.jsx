import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection'
import FlavorSelector from './components/FlavorSelector';
import flavors from './components/flavours.json';
import './App.css';

function App() {
    const [selectedFlavor, setSelectedFlavor] = useState('Strawberry');
    const currentFlavorData = flavors.find(flavor => flavor.name === selectedFlavor);

    console.log("maj app:", selectedFlavor)

  return (
    <div className="App" style={{ background: currentFlavorData.gradient }}>
      <Navbar />
      <HeroSection 
        flavor={currentFlavorData} 
        selectedFlavor={selectedFlavor} 
        setSelectedFlavor={setSelectedFlavor}/>
    </div>
  );
}

export default App;