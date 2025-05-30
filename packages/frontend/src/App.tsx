import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useAppSelector, useAppDispatch } from './store';
import { checkAuthStatus } from './store/slices/authSlice';
import Layout from './layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import AdventurerHub from './pages/AdventurerHub';
import LandingPage from './pages/LandingPage';
import TestScrollPage from './pages/TestScrollPage';
import ProtectedRoute from './components/ProtectedRoute';
import { ROUTES, RouteNames } from './types/routes';
import * as tokenService from './services/token-service';
import './App.css';
function App() {
    const { isAuthenticated, loading } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();
    const [initialAuthCheckDone, setInitialAuthCheckDone] = useState(false);
    const authCheckRef = useRef(false);

    useEffect(() => {
        if (authCheckRef.current) {
            return;
        }

        const hasToken = tokenService.hasToken();
        authCheckRef.current = true;

        if (!hasToken) {
            setInitialAuthCheckDone(true);
            return;
        }

        const checkAuth = async () => {
            try {
                await dispatch(checkAuthStatus()).unwrap();
            } catch (error) {
                console.error('App: Auth check failed:', error);
            } finally {
                setInitialAuthCheckDone(true);
            }
        };

        checkAuth();
    }, []);

    if (loading && !initialAuthCheckDone) {
        return <div className="app-loading">Loading...</div>;
    }

    return (
        <BrowserRouter>
            <Routes>
                {/* Root route - redirects based on auth status */}
                <Route path="/" element={<LandingPage />} />

                {/* Test scroll page for debugging */}
                <Route path="/test-scroll" element={<TestScrollPage />} />

                {/* Login route - redirects to dashboard if already authenticated */}
                <Route
                    path={ROUTES[RouteNames.LOGIN].path}
                    element={
                        isAuthenticated ? (
                            <Navigate to={ROUTES[RouteNames.DASHBOARD].path} />
                        ) : (
                            <Login />
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
                    {/* More protected routes can be added here as needed */}
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
