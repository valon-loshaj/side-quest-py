import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '..';
import {
    login,
    logout,
    register,
    getCurrentUser,
    updateUser,
    clearError,
} from '../slices/authSlice';
import {
    UserLoginRequest,
    UserRegistrationRequest,
    UserUpdateRequest,
} from '../../types/api';

export const useAuth = () => {
    const dispatch = useAppDispatch();
    const { user, isAuthenticated, loading, error } = useAppSelector(
        state => state.auth
    );

    const loginUser = useCallback(
        (credentials: UserLoginRequest) => {
            return dispatch(login(credentials));
        },
        [dispatch]
    );

    const registerUser = useCallback(
        (userData: UserRegistrationRequest) => {
            return dispatch(register(userData));
        },
        [dispatch]
    );

    const logoutUser = useCallback(() => {
        return dispatch(logout());
    }, [dispatch]);

    const fetchCurrentUser = useCallback(() => {
        return dispatch(getCurrentUser());
    }, [dispatch]);

    const updateUserProfile = useCallback(
        (userId: string, userData: UserUpdateRequest) => {
            return dispatch(updateUser({ userId, userData }));
        },
        [dispatch]
    );

    const clearAuthError = useCallback(() => {
        dispatch(clearError());
    }, [dispatch]);

    return {
        user,
        isAuthenticated,
        loading,
        error,
        loginUser,
        registerUser,
        logoutUser,
        fetchCurrentUser,
        updateUserProfile,
        clearAuthError,
    };
};
