import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import * as tokenService from '../../services/token-service';
import { User } from '../../types/models';
import {
    UserLoginRequest,
    UserLoginResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserUpdateRequest,
} from '../../types/api';

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    user: null,
    isAuthenticated: tokenService.isTokenValid(),
    loading: false,
    error: null,
};

export const login = createAsyncThunk<UserLoginResponse, UserLoginRequest>(
    'auth/login',
    async (credentials, { rejectWithValue }) => {
        try {
            // Create form data payload as OAuth2 expects
            const formData = new URLSearchParams();
            formData.append('username', credentials.username);
            formData.append('password', credentials.password);

            const headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            };

            // Make a direct fetch call for OAuth2 format
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: headers,
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                return rejectWithValue(errorData.detail || 'Login failed');
            }

            const data = await response.json();

            if (data.access_token) {
                tokenService.removeToken();
                tokenService.setToken(data.access_token);

                if (import.meta.env.MODE !== 'production') {
                    console.log('Login successful, token stored');
                    console.log(
                        'Token valid after login:',
                        tokenService.isTokenValid()
                    );
                }
            } else {
                console.error('No access_token found in login response:', data);
            }

            return data;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Login failed';
            return rejectWithValue(errorMessage);
        }
    }
);

export const register = createAsyncThunk<
    UserRegistrationResponse,
    UserRegistrationRequest
>('auth/register', async (userData, { rejectWithValue }) => {
    try {
        const response = await apiClient.post<UserRegistrationResponse>(
            '/api/v1/auth/register',
            userData
        );

        if (response.data.auth_token) {
            tokenService.setToken(response.data.auth_token);
        } else {
            console.error(
                'No auth_token found in registration response:',
                response.data
            );
        }

        return response.data;
    } catch (error: unknown) {
        const errorMessage =
            error instanceof Error ? error.message : 'Registration failed';
        return rejectWithValue(errorMessage);
    }
});

export const logout = createAsyncThunk(
    'auth/logout',
    async (_, { rejectWithValue }) => {
        try {
            const token = tokenService.getToken();

            await apiClient.post('/api/v1/auth/logout', undefined, {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });

            tokenService.removeToken();
            return null;
        } catch (error: unknown) {
            tokenService.removeToken();
            const errorMessage =
                error instanceof Error ? error.message : 'Logout failed';
            return rejectWithValue(errorMessage);
        }
    }
);

export const getCurrentUser = createAsyncThunk(
    'auth/getCurrentUser',
    async (_, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<User>('/api/v1/auth/me');
            console.log(
                '[AuthSlice] User data successfully fetched:',
                response.data?.id
            );
            return response.data;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch user data';
            return rejectWithValue(errorMessage);
        }
    }
);

export const checkAuthStatus = createAsyncThunk(
    'auth/checkStatus',
    async (_, { rejectWithValue }) => {
        try {
            const token = tokenService.getToken();

            // Add more detailed logging about token existence
            console.log('AuthSlice: Checking auth status, token exists:', !!token);

            // Check if token exists and is valid
            if (!token) {
                console.log('AuthSlice: No token found, clearing auth state');
                tokenService.removeToken();
                return null;
            }

            const isValid = tokenService.isTokenValid();
            console.log('AuthSlice: Token validation result:', isValid);

            if (!isValid) {
                console.log(
                    'AuthSlice: Token is invalid or expired, clearing auth state'
                );
                tokenService.removeToken();
                return null;
            }

            console.log('AuthSlice: Valid token found, fetching current user');

            // Directly make the API call instead of dispatching another action
            try {
                const response = await apiClient.get<User>('/api/v1/auth/me');
                console.log(
                    'AuthSlice: User data successfully fetched:',
                    response.data?.id
                );
                return response.data;
            } catch (error) {
                console.error('AuthSlice: Error fetching user with token:', error);

                // Only remove token on 401 Unauthorized (token rejection)
                if (
                    error &&
                    typeof error === 'object' &&
                    'code' in error &&
                    (error.code === 'HTTP_ERROR_401' || error.code === 'UNAUTHORIZED')
                ) {
                    console.log(
                        'AuthSlice: Removing token from localStorage due to 401 unauthorized'
                    );
                    tokenService.removeToken();
                    return rejectWithValue('Session expired. Please login again.');
                }

                // For other errors, keep the token but report the error
                return rejectWithValue(
                    'Error connecting to server. Please try again later.'
                );
            }
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to check auth status';
            console.error(
                'AuthSlice: Unexpected error in checkAuthStatus:',
                errorMessage
            );
            return rejectWithValue(errorMessage);
        }
    }
);

export const updateUser = createAsyncThunk<
    User,
    { userId: string; userData: UserUpdateRequest }
>('auth/updateUser', async ({ userId, userData }, { rejectWithValue }) => {
    try {
        const response = await apiClient.put<{ user: User }>(
            `/api/v1/user/${userId}`,
            userData
        );

        return response.data.user;
    } catch (error: unknown) {
        const errorMessage =
            error instanceof Error ? error.message : 'Failed to update user data';
        return rejectWithValue(errorMessage);
    }
});

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        clearError: state => {
            state.error = null;
        },
    },
    extraReducers: builder => {
        builder.addCase(login.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(login.fulfilled, (state, action) => {
            state.loading = false;
            state.isAuthenticated = true;
            state.user = action.payload.user;
        });
        builder.addCase(login.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(register.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(register.fulfilled, (state, action) => {
            state.loading = false;
            state.isAuthenticated = true;
            state.user = action.payload.user;
        });
        builder.addCase(register.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(logout.fulfilled, state => {
            state.user = null;
            state.isAuthenticated = false;
        });

        builder.addCase(getCurrentUser.pending, state => {
            state.loading = true;
        });
        builder.addCase(getCurrentUser.fulfilled, (state, action) => {
            state.loading = false;
            state.user = action.payload;
            state.isAuthenticated = true;
        });
        builder.addCase(getCurrentUser.rejected, state => {
            state.loading = false;
            state.user = null;
            state.isAuthenticated = false;
            tokenService.removeToken();
        });

        builder.addCase(updateUser.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(updateUser.fulfilled, (state, action) => {
            state.loading = false;
            state.user = action.payload;
        });
        builder.addCase(updateUser.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(checkAuthStatus.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(checkAuthStatus.fulfilled, (state, action) => {
            state.loading = false;
            if (action.payload) {
                state.user = action.payload;
                state.isAuthenticated = true;
                console.log('AuthSlice reducer: User authenticated successfully');
            } else {
                state.user = null;
                state.isAuthenticated = false;
                console.log(
                    'AuthSlice reducer: No user data returned, setting as not authenticated'
                );
            }
        });
        builder.addCase(checkAuthStatus.rejected, (state, action) => {
            state.loading = false;
            state.user = null;
            state.isAuthenticated = false;
            state.error = (action.payload as string) || 'Authentication failed';
            console.log('AuthSlice reducer: Auth check rejected, clearing user state');
        });
    },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
