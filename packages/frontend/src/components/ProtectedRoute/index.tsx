import React, { useEffect, useState, useRef } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store';
import { checkAuthStatus } from '../../store/slices/authSlice';
import { ROUTES, RouteNames } from '../../types/routes';
import * as tokenService from '../../services/token-service';

interface ProtectedRouteProps {
    children?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { isAuthenticated, user } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();
    const [authCheckAttempted, setAuthCheckAttempted] = useState(false);
    const authCheckRef = useRef(false);

    // If we already have a user or are authenticated, mark auth as attempted
    useEffect(() => {
        if (isAuthenticated || user) {
            console.log(
                'ProtectedRoute: User already authenticated, skipping auth check'
            );
            setAuthCheckAttempted(true);
        }
    }, [isAuthenticated, user]);

    useEffect(() => {
        // Skip auth check if already attempted or if already checked in App component
        if (authCheckAttempted || authCheckRef.current || isAuthenticated || user) {
            return;
        }

        authCheckRef.current = true;
        const checkAuth = async () => {
            // Only attempt auth check if token exists and we haven't checked yet
            if (tokenService.hasToken()) {
                console.log('ProtectedRoute: Checking authentication status');
                try {
                    await dispatch(checkAuthStatus()).unwrap();
                    console.log('ProtectedRoute: Auth check completed successfully');
                } catch (error) {
                    console.error('ProtectedRoute: Auth check failed', error);
                } finally {
                    setAuthCheckAttempted(true);
                }
            } else {
                console.log('ProtectedRoute: No token exists');
                setAuthCheckAttempted(true);
            }
        };

        checkAuth();
    }, [dispatch, authCheckAttempted, isAuthenticated, user]);

    // This avoids the "Verifying your session..." getting stuck
    const authCheckComplete = authCheckAttempted || isAuthenticated || user != null;

    if (!authCheckComplete && tokenService.hasToken()) {
        console.log('ProtectedRoute: Still verifying session...');
        return <div className="auth-loading">Verifying your session...</div>;
    }

    if (!isAuthenticated) {
        console.log('ProtectedRoute: Not authenticated, redirecting to login');
        return <Navigate to={ROUTES[RouteNames.LOGIN].path} replace />;
    }

    console.log('ProtectedRoute: Authentication verified, rendering protected content');
    return <>{children || <Outlet />}</>;
};

export default ProtectedRoute;
