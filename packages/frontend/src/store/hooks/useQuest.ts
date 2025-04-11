import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '..';
import {
    fetchQuests,
    createQuest,
    getQuest,
    markQuestAsCompleted,
    clearQuestError,
    setCurrentQuest,
} from '../slices/questSlice';
import { Quest } from '../../types/models';

export const useQuest = () => {
    const dispatch = useAppDispatch();
    const { quests, currentQuest, loading, error } = useAppSelector(
        state => state.quest
    );

    const fetchAllQuests = useCallback(() => {
        return dispatch(fetchQuests());
    }, [dispatch]);

    const createNewQuest = useCallback(
        (title: string, adventurerId?: string, experienceReward?: number) => {
            return dispatch(
                createQuest({
                    title,
                    adventurerId,
                    experienceReward,
                })
            );
        },
        [dispatch]
    );

    const fetchQuestById = useCallback(
        (id: string) => {
            return dispatch(getQuest(id));
        },
        [dispatch]
    );

    const completeQuest = useCallback(
        (id: string) => {
            return dispatch(markQuestAsCompleted(id));
        },
        [dispatch]
    );

    const clearQuestErrors = useCallback(() => {
        dispatch(clearQuestError());
    }, [dispatch]);

    const selectQuest = useCallback(
        (quest: Quest) => {
            dispatch(setCurrentQuest(quest));
        },
        [dispatch]
    );

    return {
        quests,
        currentQuest,
        loading,
        error,
        fetchAllQuests,
        createNewQuest,
        fetchQuestById,
        completeQuest,
        clearQuestErrors,
        selectQuest,
    };
};
