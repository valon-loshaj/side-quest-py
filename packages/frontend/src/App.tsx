import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
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
    const { isAuthenticated, loading } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();
    const [initialAuthCheckDone, setInitialAuthCheckDone] = useState(false);

    useEffect(() => {
        // Check if we have a token in storage
        const hasToken = tokenService.hasToken();
        console.log('App mounted, token exists:', hasToken);

        // Check auth status on app mount
        const checkAuth = async () => {
            try {
                await dispatch(checkAuthStatus()).unwrap();
                console.log('Auth check completed successfully');
            } catch (error) {
                console.error('Auth check failed:', error);
            } finally {
                setInitialAuthCheckDone(true);
            }
        };

        checkAuth();
    }, [dispatch]);

    // Only show initial loading spinner while first auth check is happening
    // This prevents the initial flash of login screen
    if (loading && !initialAuthCheckDone) {
        return <div className="app-loading">Loading...</div>;
    }

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
