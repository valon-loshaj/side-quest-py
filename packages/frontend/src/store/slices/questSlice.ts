import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import { Quest } from '../../types/models';

interface QuestState {
    quests: Quest[];
    currentQuest: Quest | null;
    loading: boolean;
    error: string | null;
}

interface CreateQuestRequest {
    title: string;
    experienceReward?: number;
    adventurerId?: string;
    [key: string]: unknown;
}

interface QuestResponse {
    message: string;
    quest: Quest;
}

const initialState: QuestState = {
    quests: [],
    currentQuest: null,
    loading: false,
    error: null,
};

export const fetchQuests = createAsyncThunk(
    'quest/fetchAll',
    async (_, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<Quest[]>('/quests');
            return response.data;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch quests';
            return rejectWithValue(errorMessage);
        }
    }
);

export const createQuest = createAsyncThunk(
    'quest/create',
    async (questData: CreateQuestRequest, { rejectWithValue }) => {
        try {
            const response = await apiClient.post<QuestResponse>('/quest', {
                title: questData.title,
                experience_reward: questData.experienceReward,
                adventurer_id: questData.adventurerId,
            });
            return response.data.quest;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to create quest';
            return rejectWithValue(errorMessage);
        }
    }
);

export const getQuest = createAsyncThunk(
    'quest/getOne',
    async (id: string, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<{ quest: Quest }>(`/quest/${id}`);
            return response.data.quest;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch quest';
            return rejectWithValue(errorMessage);
        }
    }
);

export const markQuestAsCompleted = createAsyncThunk(
    'quest/complete',
    async (id: string, { rejectWithValue }) => {
        try {
            const response = await apiClient.patch<QuestResponse>(`/quest/${id}`);
            return response.data.quest;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to complete quest';
            return rejectWithValue(errorMessage);
        }
    }
);

const questSlice = createSlice({
    name: 'quest',
    initialState,
    reducers: {
        clearQuestError: state => {
            state.error = null;
        },
        setCurrentQuest: (state, action) => {
            state.currentQuest = action.payload;
        },
    },
    extraReducers: builder => {
        builder.addCase(fetchQuests.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(fetchQuests.fulfilled, (state, action) => {
            state.loading = false;
            state.quests = action.payload;
        });
        builder.addCase(fetchQuests.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(createQuest.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(createQuest.fulfilled, (state, action) => {
            state.loading = false;
            state.quests.push(action.payload);
            state.currentQuest = action.payload;
        });
        builder.addCase(createQuest.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(getQuest.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(getQuest.fulfilled, (state, action) => {
            state.loading = false;
            state.currentQuest = action.payload;
        });
        builder.addCase(getQuest.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(markQuestAsCompleted.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(markQuestAsCompleted.fulfilled, (state, action) => {
            state.loading = false;
            state.currentQuest = action.payload;

            const index = state.quests.findIndex(
                quest => quest.id === action.payload.id
            );
            if (index !== -1) {
                state.quests[index] = action.payload;
            }
        });
        builder.addCase(markQuestAsCompleted.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });
    },
});

export const { clearQuestError, setCurrentQuest } = questSlice.actions;
export default questSlice.reducer;
