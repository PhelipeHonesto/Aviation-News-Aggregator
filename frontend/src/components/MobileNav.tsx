import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './MobileNav.css';

const MobileNav = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Feed', icon: '📰' },
    { path: '/saved', label: 'Saved', icon: '💾' },
    { path: '/drafts', label: 'Drafts', icon: '📝' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  return (
    <div className="mobile-nav">
      {/* Mobile Header */}
      <div className="mobile-header">
        <div className="mobile-logo">
          <img src="/logo.jpeg" alt="Orange Sunshine Aviation Logo" />
          <span>OSA Curator</span>
        </div>
        <button className="mobile-menu-toggle" onClick={toggleMenu}>
          <span className={`hamburger ${isOpen ? 'open' : ''}`}></span>
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      <div className={`mobile-menu-overlay ${isOpen ? 'open' : ''}`} onClick={closeMenu}>
        <div className="mobile-menu" onClick={(e) => e.stopPropagation()}>
          <div className="mobile-menu-header">
            <div className="mobile-menu-logo">
              <img src="/logo.jpeg" alt="Orange Sunshine Aviation Logo" />
              <span>Orange Sunshine Aviation</span>
            </div>
            <button className="mobile-menu-close" onClick={closeMenu}>
              ×
            </button>
          </div>
          
          <nav className="mobile-menu-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-item ${location.pathname === item.path ? 'active' : ''}`}
                onClick={closeMenu}
              >
                <span className="mobile-nav-icon">{item.icon}</span>
                <span className="mobile-nav-label">{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
};

export default MobileNav; 
