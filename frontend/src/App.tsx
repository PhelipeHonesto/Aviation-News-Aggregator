import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NewsTerminal from './pages/NewsTerminal';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<NewsTerminal />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;