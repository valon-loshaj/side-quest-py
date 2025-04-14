import { jwtDecode } from 'jwt-decode';

// Token key for localStorage
const TOKEN_KEY = 'auth_token';

interface JwtPayload {
    exp: number;
    [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}

/**
 * Checks if a token exists in localStorage
 * @returns boolean indicating if token exists
 */
export const hasToken = (): boolean => {
    const hasToken = !!localStorage.getItem(TOKEN_KEY);
    if (import.meta.env.MODE !== 'production') {
        console.log('Token exists check:', hasToken);
    }
    return hasToken;
};

/**
 * Gets the token from localStorage
 * @returns token string or null if not found
 */
export const getToken = (): string | null => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (import.meta.env.MODE !== 'production') {
        console.log('Retrieved token from storage:', token ? 'exists' : 'not found');
    }
    return token;
};

/**
 * Sets the token in localStorage
 * @param token - The JWT token to store
 */
export const setToken = (token: string): void => {
    if (import.meta.env.MODE !== 'production') {
        console.log('Setting token in localStorage');
    }
    localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Removes the token from localStorage
 */
export const removeToken = (): void => {
    if (import.meta.env.MODE !== 'production') {
        console.log('Removing token from localStorage');
    }
    localStorage.removeItem(TOKEN_KEY);
};

/**
 * Checks if the current token is valid
 * @returns boolean indicating if token is valid
 */
export const isTokenValid = (): boolean => {
    const token = getToken();
    if (!token) {
        if (import.meta.env.MODE !== 'production') {
            console.log('Token validation failed: No token found');
        }
        return false;
    }

    try {
        // Log complete token in dev for debugging
        if (import.meta.env.MODE !== 'production') {
            // Only log token length and a small prefix for security
            const tokenLength = token.length;
            const tokenPrefix = token.substring(0, 10);
            console.log(`Token to validate: ${tokenPrefix}... (${tokenLength} chars)`);

            // Check token format - should have 3 parts separated by periods
            const parts = token.split('.');
            console.log('Token parts count:', parts.length);

            if (parts.length !== 3) {
                console.error(
                    'Error: Invalid token format - not a valid JWT. JWT should have 3 parts separated by dots.'
                );
                return false;
            }
        }

        // Actually decode and verify the token
        const decoded = jwtDecode<JwtPayload>(token);

        // Check if expiration exists
        if (!decoded.exp) {
            console.error('Token is missing expiration claim');
            return false;
        }

        const currentTime = Math.floor(Date.now() / 1000);
        const isValid = decoded.exp > currentTime;

        if (import.meta.env.MODE !== 'production') {
            const expiryDate = new Date(decoded.exp * 1000);
            const timeRemaining = Math.floor((decoded.exp - currentTime) / 60); // minutes

            console.log('Token validation result:', isValid ? 'valid' : 'expired', {
                expires: expiryDate.toISOString(),
                now: new Date().toISOString(),
                timeRemaining: timeRemaining,
                minutesUntilExpiry: timeRemaining,
            });

            // Warn if token is about to expire
            if (isValid && timeRemaining < 10) {
                console.warn(`Token will expire soon (in ${timeRemaining} minutes)`);
            }
        }

        return isValid;
    } catch (error) {
        console.error('Error decoding token:', error);
        return false;
    }
};

/**
 * Gets the token expiration time
 * @returns Date object representing expiration or null if token is invalid
 */
export const getTokenExpiration = (): Date | null => {
    const token = getToken();
    if (!token) return null;

    try {
        const decoded = jwtDecode<JwtPayload>(token);
        return new Date(decoded.exp * 1000); // Convert seconds to milliseconds
    } catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
};
