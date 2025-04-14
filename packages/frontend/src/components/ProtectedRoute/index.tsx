import React, { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store';
import { checkAuthStatus } from '../../store/slices/authSlice';
import { ROUTES, RouteNames } from '../../types/routes';
import * as tokenService from '../../services/token-service';

interface ProtectedRouteProps {
    children?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { isAuthenticated, loading } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();

    useEffect(() => {
        // Only check status if we have a token but aren't authenticated yet
        if (tokenService.hasToken() && !isAuthenticated) {
            dispatch(checkAuthStatus());
        }
    }, [dispatch, isAuthenticated]);

    // While checking, show nothing or a loading spinner
    if (loading) {
        return <div>Loading...</div>; // You can replace this with a proper loading component
    }

    if (!isAuthenticated) {
        return <Navigate to={ROUTES[RouteNames.LOGIN].path} replace />;
    }

    return <>{children || <Outlet />}</>;
};

export default ProtectedRoute;
