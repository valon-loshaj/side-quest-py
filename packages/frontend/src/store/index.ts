import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

import authReducer from '../store/slices/authSlice';
import adventurerReducer from '../store/slices/adventurerSlice';
import questReducer from '../store/slices/questSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        adventurer: adventurerReducer,
        quest: questReducer,
    },
    devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
