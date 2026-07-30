import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/auth/LoginPage';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import './App.css';
import AuthLayout from './layouts/AuthLayout';
import UsersPage from './pages/admin/UsersPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Mặc định redirect đên trang đăng nhập */}
          <Route path='/' element={<Navigate to='/auth/login' replace />} />
          
          {/* Public routes */}
          <Route element={<AuthLayout />}>
            <Route path='/auth/login' element={<LoginPage />} />
          </Route>

          {/* Protected Admin routes */}
          <Route element={<ProtectedRoute requireAdmin={true} />}>
            <Route path='/admin/users' element={<UsersPage />} />
          </Route>
          
          <Route path="/403" element={<div>403 - Không có quyền truy cập</div>} />

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;