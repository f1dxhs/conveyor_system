import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
// 导入其他页面...

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>带式输送机托辊监测系统</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            {/* 其他路由... */}
          </Routes>
        </main>
        <footer>
          <p>&copy; 2023 带式输送机托辊监测系统</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;