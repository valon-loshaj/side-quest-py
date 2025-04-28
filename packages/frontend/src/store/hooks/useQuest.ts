import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '..';
import {
    fetchQuests,
    createQuest,
    getQuest,
    markQuestAsCompleted,
    clearQuestError,
    setCurrentQuest,
    updateQuest,
    deleteQuest,
} from '../slices/questSlice';
import { Quest } from '../../types/models';

export const useQuest = () => {
    const dispatch = useAppDispatch();
    const { quests, currentQuest, loading, error } = useAppSelector(
        state => state.quest
    );

    const fetchAllQuests = useCallback(
        (adventurerId: string) => {
            return dispatch(fetchQuests(adventurerId));
        },
        [dispatch]
    );

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
        (id: string, adventurerId: string, completed: boolean = true) => {
            return dispatch(
                markQuestAsCompleted({
                    id,
                    questData: {
                        completed,
                        adventurer_id: adventurerId,
                    },
                })
            );
        },
        [dispatch]
    );

    const updateQuestDetails = useCallback(
        (id: string, questData: Partial<Quest>) => {
            return dispatch(updateQuest({ id, questData }));
        },
        [dispatch]
    );

    const removeQuest = useCallback(
        (id: string) => {
            return dispatch(deleteQuest(id));
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
        updateQuestDetails,
        removeQuest,
        clearQuestErrors,
        selectQuest,
    };
};
