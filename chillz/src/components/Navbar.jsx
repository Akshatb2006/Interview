import React from 'react';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <img src="/images/logo.png" alt="Chillz company logo" className="navbar-logo" />
      
      <ul className="navbar-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#shop">Shop</a></li>
        <li><a href="#delivery">Delivery</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
      <button className="navbar-order-btn">Order Your Ice-cream</button>
    </nav>
  );
}

export default Navbar;