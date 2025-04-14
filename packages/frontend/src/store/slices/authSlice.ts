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
import { store } from '..';

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
            const response = await apiClient.post<UserLoginResponse>(
                '/api/v1/auth/login',
                credentials
            );

            if (response.data.auth_token) {
                // Clear any existing token first
                tokenService.removeToken();
                // Then set the new token
                tokenService.setToken(response.data.auth_token);

                if (import.meta.env.MODE !== 'production') {
                    console.log('Login successful, token stored');
                    console.log(
                        'Token valid after login:',
                        tokenService.isTokenValid()
                    );
                }
            } else {
                console.error('No auth_token found in login response:', response.data);
            }

            return response.data;
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
            const response = await apiClient.get<{ user: User }>('/api/v1/auth/me');
            return response.data.user;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch user data';
            return rejectWithValue(errorMessage);
        }
    }
);

export const checkAuthStatus = createAsyncThunk(
    'auth/checkStatus',
    async (_, { rejectWithValue, dispatch }) => {
        try {
            const token = tokenService.getToken();

            // Add more detailed logging about token existence
            console.log('Checking auth status, token exists:', !!token);

            // Check if token exists and is valid
            if (!token) {
                console.log('No token found, clearing auth state');
                tokenService.removeToken();
                return null;
            }

            const isValid = tokenService.isTokenValid();
            console.log('Token validation result:', isValid);

            if (!isValid) {
                console.log('Token is invalid or expired, clearing auth state');
                tokenService.removeToken();
                return null;
            }

            console.log('Valid token found, fetching current user');

            // Directly make the API call instead of dispatching another action
            try {
                const response = await apiClient.get<{ user: User }>('/api/v1/auth/me');
                console.log('User data successfully fetched:', response.data.user?.id);
                return response.data.user;
            } catch (error) {
                console.error('Error fetching user with token:', error);

                // Only remove token on 401 Unauthorized (token rejection)
                if (
                    error &&
                    typeof error === 'object' &&
                    'code' in error &&
                    (error.code === 'HTTP_ERROR_401' || error.code === 'UNAUTHORIZED')
                ) {
                    console.log(
                        'Removing token from localStorage due to 401 unauthorized'
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
            console.error('Unexpected error in checkAuthStatus:', errorMessage);
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
    },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
