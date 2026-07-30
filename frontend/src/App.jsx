import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/auth/LoginPage';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import AuthLayout from './layouts/AuthLayout';
import UsersPage from './pages/admin/UsersPage';
import { PATHS } from './constants/routes';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Mặc định redirect đên trang đăng nhập */}
          <Route path={PATHS.HOME} element={<Navigate to={PATHS.LOGIN} replace />} />

          {/* Public routes */}
          <Route element={<AuthLayout />}>
            <Route path={PATHS.LOGIN} element={<LoginPage />} />
          </Route>

          {/* Protected Admin routes */}
          <Route element={<ProtectedRoute requireAdmin={true} />}>
            <Route path={PATHS.ADMIN_USERS} element={<UsersPage />} />
          </Route>

          <Route path={PATHS.FORBIDDEN} element={<div>403 - Không có quyền truy cập</div>} />

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;