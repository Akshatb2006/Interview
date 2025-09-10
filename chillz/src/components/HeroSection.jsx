import React, { useEffect, useRef, useState } from 'react';
import './HeroSection.css';
import FlavorSelector from './FlavorSelector';
import flavors from './flavours.json';

function HeroSection({ flavor, selectedFlavor, setSelectedFlavor }) {

  const prevFlavorRef = useRef();
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    if (prevFlavorRef.current && prevFlavorRef.current !== flavor) {
      setAnimate(true);

      const timer = setTimeout(() => {
        setAnimate(false);
      }, 1200); 

      return () => clearTimeout(timer);
    }

    prevFlavorRef.current = flavor; 
  }, [flavor]);

  return (
    <div className="hero-wrapper">
      <section className="hero-section">
        <div className="hero-content">
          <p className="hero-title">icecream</p>
          <p className="hero-subtitle">{flavor.name} cone</p>
          <p className="hero-description">
            Embark on a culinary journey of delight as you immerse yourself in our
            artisan-crafted ice cream collection—each flavor a story, each scoop
            an unforgettable chapter in your sweet odyssey!
          </p>
          <p className="hero-description">
            Indulge in a world of imagination, where every scoop unveils
            a new taste adventure! choose your favorite
          </p>
        </div>

        <FlavorSelector
          flavors={flavors}
          selectedFlavor={selectedFlavor}
          setSelectedFlavor={setSelectedFlavor}
        />
      </section>

      <div key={flavor.name} className={animate ? "slide-down-back-full" : "slide-down-back-full"}>
        <img
          src={flavor.image}
          alt={`${flavor.name} ice cream cone`}
          className="hero-icecream-image"
        />
      </div>
    </div>
  );
}

export default HeroSection;