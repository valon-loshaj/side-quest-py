import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from './store';
import Layout from './layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import ProtectedRoute from './components/ProtectedRoute';
import { ROUTES, RouteNames } from './types/routes';
import './App.css';

function App() {
    const { isAuthenticated } = useAppSelector(state => state.auth);

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
