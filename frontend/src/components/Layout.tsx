import { Outlet, Link } from 'react-router-dom';
import MobileNav from './MobileNav';

const Layout = () => {
  return (
    <div className="app-container">
      {/* Mobile Navigation */}
      <MobileNav />
      
      {/* Desktop Navigation */}
      <nav className="main-nav">
        <div className="nav-logo">
          <img src="/logo.jpeg" alt="Orange Sunshine Aviation Logo" />
          <span>Orange Sunshine Aviation</span>
        </div>
        <ul>
          <li><Link to="/">Feed</Link></li>
          <li><Link to="/saved">Saved</Link></li>
          <li><Link to="/drafts">Drafts</Link></li>
          <li><Link to="/settings">Settings</Link></li>
        </ul>
      </nav>
      <main className="content-area">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
