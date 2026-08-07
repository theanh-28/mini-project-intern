import { Routes, Route, Navigate } from 'react-router-dom';

import ProtectedRoute from '@/routes/ProtectedRoute';

import AuthLayout from '@/layouts/auth_layout/AuthLayout';
import LoginPage from '@/pages/auth/LoginPage';

import IAMLayout from '@/layouts/iam_layout/IAMLayout';
import UsersPage from '@/pages/iam/users_page/UsersPage';
import UserDetailPage from '@/pages/iam/users_page/UserDetailPage';

import { PATHS } from '@/constants/routes';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Mặc định redirect đến trang đăng nhập */}
      <Route path={PATHS.HOME} element={<Navigate to={PATHS.LOGIN} replace />} />

      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route path={PATHS.LOGIN} element={<LoginPage />} />
      </Route>

      {/* Protected Admin routes */}
      <Route element={<ProtectedRoute requireAdmin={true} />}>
        <Route element={<IAMLayout />}>
          <Route path={PATHS.ADMIN_USERS} element={<UsersPage />} />
          <Route path={`${PATHS.ADMIN_USERS}/:userId`} element={<UserDetailPage />}/>
        </Route>
      </Route>

      {/* 403 Forbidden */}
      <Route path={PATHS.FORBIDDEN} element={<div>403 - Không có quyền truy cập</div>} />
    </Routes>
  );
}
