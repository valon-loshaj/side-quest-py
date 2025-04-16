import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useAppSelector, useAppDispatch } from './store';
import { checkAuthStatus } from './store/slices/authSlice';
import Layout from './layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import AdventurerHub from './pages/AdventurerHub';
import ProtectedRoute from './components/ProtectedRoute';
import { ROUTES, RouteNames } from './types/routes';
import * as tokenService from './services/token-service';
import './App.css';

function App() {
    const { isAuthenticated, loading, user } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();
    const [initialAuthCheckDone, setInitialAuthCheckDone] = useState(false);
    const authCheckRef = useRef(false);

    // Debug logging for App component state
    useEffect(() => {
        console.log('App: Auth state updated', {
            isAuthenticated,
            loading,
            initialAuthCheckDone,
            hasUser: !!user,
            userId: user?.id,
            authCheckStarted: authCheckRef.current,
        });
    }, [isAuthenticated, loading, initialAuthCheckDone, user]);

    useEffect(() => {
        // Use a ref to ensure we only run this once regardless of rerenders
        if (authCheckRef.current) {
            return;
        }

        // Check if we have a token in storage
        const hasToken = tokenService.hasToken();
        console.log('App: Initial mount, token exists:', hasToken);

        // Mark that we've started an auth check
        authCheckRef.current = true;

        // Only run the auth check if we have a token to validate
        if (!hasToken) {
            console.log('App: No token exists, skipping auth check');
            setInitialAuthCheckDone(true);
            return;
        }

        // Check auth status on app mount
        const checkAuth = async () => {
            try {
                console.log('App: Starting auth check');
                await dispatch(checkAuthStatus()).unwrap();
                console.log('App: Auth check completed successfully');
            } catch (error) {
                console.error('App: Auth check failed:', error);
            } finally {
                console.log('App: Setting initialAuthCheckDone to true');
                setInitialAuthCheckDone(true);
            }
        };

        checkAuth();
    }, []); // Empty dependency array to run only once

    // Only show initial loading spinner while first auth check is happening
    // This prevents the initial flash of login screen
    if (loading && !initialAuthCheckDone) {
        console.log('App: Showing initial loading spinner');
        return <div className="app-loading">Loading...</div>;
    }

    // Continue with the regular rendering logic
    return (
        <BrowserRouter>
            <Routes>
                {/* Root route - redirects based on auth status */}
                <Route
                    path="/"
                    element={
                        <Navigate
                            to={
                                isAuthenticated
                                    ? ROUTES[RouteNames.DASHBOARD].path
                                    : ROUTES[RouteNames.LOGIN].path
                            }
                        />
                    }
                />

                {/* Login route - redirects to dashboard if already authenticated */}
                <Route
                    path={ROUTES[RouteNames.LOGIN].path}
                    element={
                        isAuthenticated ? (
                            <Navigate to={ROUTES[RouteNames.DASHBOARD].path} />
                        ) : (
                            <Layout>
                                <Login />
                            </Layout>
                        )
                    }
                />

                {/* Protected routes - wrapped with ProtectedRoute component */}
                <Route element={<ProtectedRoute />}>
                    <Route
                        path={ROUTES[RouteNames.DASHBOARD].path}
                        element={
                            <Layout>
                                <Dashboard />
                            </Layout>
                        }
                    />
                    <Route
                        path={ROUTES[RouteNames.USER_MANAGEMENT].path}
                        element={
                            <Layout>
                                <UserManagement />
                            </Layout>
                        }
                    />
                    <Route
                        path={ROUTES[RouteNames.ADVENTURER_HUB].path}
                        element={
                            <Layout>
                                <AdventurerHub />
                            </Layout>
                        }
                    />
                    {/* Add more protected routes here as needed */}
                </Route>

                {/* Catch-all route for unknown paths */}
                <Route
                    path="*"
                    element={
                        <Navigate
                            to={
                                isAuthenticated
                                    ? ROUTES[RouteNames.DASHBOARD].path
                                    : ROUTES[RouteNames.LOGIN].path
                            }
                        />
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
