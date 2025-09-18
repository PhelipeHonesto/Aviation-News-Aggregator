import { Outlet, Link, useLocation } from 'react-router-dom';
import MobileNav from './MobileNav';
import LoudHawkLogo from './LoudHawkLogo';

const Layout = () => {
  const location = useLocation();

  return (
    <div className="osa-diamond-bg" style={{ minHeight: '100vh' }}>
      {/* Mobile Navigation */}
      <MobileNav />
      
      {/* OSA Desktop Navigation */}
      <nav className="osa-nav">
        <div className="osa-container osa-flex-between" style={{ padding: 'var(--space-lg) var(--space-lg)' }}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <LoudHawkLogo 
              size="medium" 
              variant="news" 
              color="orange"
              className="osa-nav-brand"
            />
          </Link>
          
          <ul className="osa-nav-links">
            <li>
              <Link 
                to="/" 
                className={`osa-nav-link ${location.pathname === '/' ? 'active' : ''}`}
              >
                📰 Feed
              </Link>
            </li>
            <li>
              <Link 
                to="/saved" 
                className={`osa-nav-link ${location.pathname === '/saved' ? 'active' : ''}`}
              >
                💾 Saved
              </Link>
            </li>
            <li>
              <Link 
                to="/drafts" 
                className={`osa-nav-link ${location.pathname === '/drafts' ? 'active' : ''}`}
              >
                📝 Drafts
              </Link>
            </li>
            <li>
              <Link 
                to="/factory" 
                className={`osa-nav-link ${location.pathname === '/factory' ? 'active' : ''}`}
              >
                🏭 Content Factory
              </Link>
            </li>
            <li>
              <Link 
                to="/settings" 
                className={`osa-nav-link ${location.pathname === '/settings' ? 'active' : ''}`}
              >
                ⚙️ Settings
              </Link>
            </li>
          </ul>
        </div>
      </nav>
      
      <main style={{ flex: 1, padding: 'var(--space-xl) 0' }}>
        <Outlet />
      </main>
      
      {/* OSA Footer */}
      <footer style={{ 
        background: 'var(--osa-gray)', 
        color: 'var(--osa-white)', 
        padding: 'var(--space-xl) 0',
        marginTop: 'auto'
      }}>
        <div className="osa-container osa-text-center">
          <p className="osa-body-small" style={{ color: 'var(--osa-beige)' }}>
            © 2025 Orange Sunshine Aviation - Democratizing Aviation Education
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
