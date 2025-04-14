import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../store/hooks/useAuth';
import { UserLoginRequest, UserRegistrationRequest } from '../types/api';
import { ROUTES, RouteNames } from '../types/routes';
import styles from '../styles/Login.module.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const { loginUser, registerUser, loading, error, clearAuthError } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        clearAuthError();

        const credentials: UserLoginRequest = {
            username,
            password,
        };

        const result = await loginUser(credentials);

        if (result.meta.requestStatus === 'fulfilled') {
            navigate(ROUTES[RouteNames.DASHBOARD].path);
        }
    };

    const handleRegisterToggle = () => {
        setIsRegistering(!isRegistering);
    };

    const handleRegister = async (e: FormEvent) => {
        e.preventDefault();
        console.log('User registration status:', isRegistering);

        const registrationData: UserRegistrationRequest = {
            username,
            password,
            email,
        };
        const result = await registerUser(registrationData);
        if (result.meta.requestStatus === 'fulfilled') {
            navigate(ROUTES[RouteNames.DASHBOARD].path);
        }
    };

    return (
        <div className={styles.loginContainer}>
            <h2>Login</h2>
            {error && <div className={styles.errorMessage}>{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className={styles.formGroup}>
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        required
                    />
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                    />
                </div>

                {isRegistering && (
                    <div className={styles.formGroup}>
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                        />
                        <button
                            type="submit"
                            className={styles.registerButton}
                            onClick={handleRegister}
                        >
                            Register
                        </button>
                    </div>
                )}

                <button type="submit" disabled={loading} className={styles.loginButton}>
                    {loading ? 'Logging in...' : 'Login'}
                </button>
                <button
                    type="button"
                    className={styles.registerButton}
                    onClick={handleRegisterToggle}
                >
                    Not a user? Register
                </button>
            </form>
        </div>
    );
};

export default Login;
