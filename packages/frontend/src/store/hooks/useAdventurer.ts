import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '..';
import {
    fetchAdventurers,
    createAdventurer,
    getAdventurer,
    completeQuest,
    clearAdventurerError,
    setCurrentAdventurer,
} from '../slices/adventurerSlice';
import { Adventure } from '../../types/models';

export const useAdventurer = () => {
    const dispatch = useAppDispatch();
    const { adventurers, currentAdventurer, loading, error } = useAppSelector(
        state => state.adventurer
    );

    const fetchAllAdventurers = useCallback(() => {
        return dispatch(fetchAdventurers());
    }, [dispatch]);

    const createNewAdventurer = useCallback(
        (name: string, userId: string, adventurer_type: string = 'Amazon') => {
            console.log(
                'Creating new adventurer with name, type and userId:',
                name,
                adventurer_type,
                userId
            );
            return dispatch(createAdventurer({ name, userId, adventurer_type }));
        },
        [dispatch]
    );

    const fetchAdventurerById = useCallback(
        (id: string) => {
            return dispatch(getAdventurer(id));
        },
        [dispatch]
    );

    const completeQuestForAdventurer = useCallback(
        (adventurerId: string, questId: string) => {
            return dispatch(completeQuest({ adventurerId, questId }));
        },
        [dispatch]
    );

    const clearAdventurerErrors = useCallback(() => {
        dispatch(clearAdventurerError());
    }, [dispatch]);

    const selectAdventurer = useCallback(
        (adventurer: Adventure) => {
            dispatch(setCurrentAdventurer(adventurer));
        },
        [dispatch]
    );

    return {
        adventurers,
        currentAdventurer,
        loading,
        error,
        fetchAllAdventurers,
        createNewAdventurer,
        fetchAdventurerById,
        completeQuestForAdventurer,
        clearAdventurerErrors,
        selectAdventurer,
    };
};
