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
    return !!localStorage.getItem(TOKEN_KEY);
};

/**
 * Gets the token from localStorage
 * @returns token string or null if not found
 */
export const getToken = (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
};

/**
 * Sets the token in localStorage
 * @param token - The JWT token to store
 */
export const setToken = (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Removes the token from localStorage
 */
export const removeToken = (): void => {
    localStorage.removeItem(TOKEN_KEY);
};

/**
 * Checks if the current token is valid
 * @returns boolean indicating if token is valid
 */
export const isTokenValid = (): boolean => {
    const token = getToken();
    if (!token) return false;

    try {
        const decoded = jwtDecode<JwtPayload>(token);
        const currentTime = Math.floor(Date.now() / 1000);

        // Check if token is expired (expiration time is in seconds)
        return decoded.exp > currentTime;
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
