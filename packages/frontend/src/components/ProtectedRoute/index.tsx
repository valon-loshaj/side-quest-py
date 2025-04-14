import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../../store';
import { ROUTES, RouteNames } from '../../types/routes';

interface ProtectedRouteProps {
    children?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { isAuthenticated } = useAppSelector(state => state.auth);

    if (!isAuthenticated) {
        return <Navigate to={ROUTES[RouteNames.LOGIN].path} replace />;
    }

    return <>{children || <Outlet />}</>;
};

export default ProtectedRoute;
