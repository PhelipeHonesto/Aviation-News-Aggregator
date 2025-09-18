import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Feed from './pages/Feed';
import Saved from './pages/Saved';
import Drafts from './pages/Drafts';
import Settings from './pages/Settings';
import ContentFactory from './pages/ContentFactory';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Feed />} />
        <Route path="saved" element={<Saved />} />
        <Route path="drafts" element={<Drafts />} />
        <Route path="settings" element={<Settings />} />
        <Route path="factory" element={<ContentFactory />} />
      </Route>
    </Routes>
  );
}

export default App;
