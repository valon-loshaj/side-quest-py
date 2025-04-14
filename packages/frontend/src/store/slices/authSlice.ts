import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import * as tokenService from '../../services/token-service';
import { User } from '../../types/models';
import {
    UserLoginRequest,
    UserLoginResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
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
                tokenService.setToken(response.data.auth_token);
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
    async (_, { rejectWithValue }) => {
        const token = tokenService.getToken();
        if (token && tokenService.isTokenValid()) {
            try {
                return await store.dispatch(getCurrentUser()).unwrap();
            } catch (error: unknown) {
                const errorMessage =
                    error instanceof Error
                        ? error.message
                        : 'Failed to check auth status';
                tokenService.removeToken();
                return rejectWithValue(errorMessage);
            }
        }
        return null;
    }
);

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
    },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
