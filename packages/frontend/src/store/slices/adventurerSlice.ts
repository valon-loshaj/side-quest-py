import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import { Adventure } from '../../types/models';

interface AdventurerState {
    adventurers: Adventure[];
    currentAdventurer: Adventure | null;
    loading: boolean;
    error: string | null;
}

interface CreateAdventurerRequest {
    name: string;
    userId?: string;
    [key: string]: unknown;
}

interface CompleteQuestRequest {
    adventurerId: string;
    questId: string;
    [key: string]: unknown;
}

interface AdventurerResponse {
    message: string;
    adventurer: Adventure;
}

interface QuestCompletionResponse {
    message: string;
    adventurer: Adventure;
    was_new_completion: boolean;
    leveled_up: boolean;
}

const initialState: AdventurerState = {
    adventurers: [],
    currentAdventurer: null,
    loading: false,
    error: null,
};

export const fetchAdventurers = createAsyncThunk(
    'adventurer/fetchAll',
    async (_, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<{
                adventurers: Adventure[];
                count: number;
            }>('/adventurers');
            return response.data.adventurers;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch adventurers';
            return rejectWithValue(errorMessage);
        }
    }
);

export const createAdventurer = createAsyncThunk(
    'adventurer/create',
    async (adventurerData: CreateAdventurerRequest, { rejectWithValue }) => {
        try {
            const response = await apiClient.post<AdventurerResponse>('/adventurer', {
                name: adventurerData.name,
                user_id: adventurerData.userId,
            });
            return response.data.adventurer;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to create adventurer';
            return rejectWithValue(errorMessage);
        }
    }
);

export const getAdventurer = createAsyncThunk(
    'adventurer/getOne',
    async (id: string, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<{ adventurer: Adventure }>(
                `/adventurer/${id}`
            );
            return response.data.adventurer;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch adventurer';
            return rejectWithValue(errorMessage);
        }
    }
);

export const completeQuest = createAsyncThunk(
    'adventurer/completeQuest',
    async (data: CompleteQuestRequest, { rejectWithValue }) => {
        try {
            const response = await apiClient.post<QuestCompletionResponse>(
                `/adventurer/${data.adventurerId}/quest/${data.questId}`
            );

            return {
                adventurer: response.data.adventurer,
                wasNewCompletion: response.data.was_new_completion,
                leveledUp: response.data.leveled_up,
            };
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to complete quest';
            return rejectWithValue(errorMessage);
        }
    }
);

const adventurerSlice = createSlice({
    name: 'adventurer',
    initialState,
    reducers: {
        clearAdventurerError: state => {
            state.error = null;
        },
        setCurrentAdventurer: (state, action) => {
            state.currentAdventurer = action.payload;
        },
    },
    extraReducers: builder => {
        builder.addCase(fetchAdventurers.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(fetchAdventurers.fulfilled, (state, action) => {
            state.loading = false;
            state.adventurers = action.payload;
        });
        builder.addCase(fetchAdventurers.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(createAdventurer.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(createAdventurer.fulfilled, (state, action) => {
            state.loading = false;
            state.adventurers.push(action.payload);
            state.currentAdventurer = action.payload;
        });
        builder.addCase(createAdventurer.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(getAdventurer.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(getAdventurer.fulfilled, (state, action) => {
            state.loading = false;
            state.currentAdventurer = action.payload;
        });
        builder.addCase(getAdventurer.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(completeQuest.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(completeQuest.fulfilled, (state, action) => {
            state.loading = false;
            state.currentAdventurer = action.payload.adventurer;

            const index = state.adventurers.findIndex(
                adv => adv.id === action.payload.adventurer.id
            );

            if (index !== -1) {
                state.adventurers[index] = action.payload.adventurer;
            }
        });
        builder.addCase(completeQuest.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });
    },
});

export const { clearAdventurerError, setCurrentAdventurer } = adventurerSlice.actions;
export default adventurerSlice.reducer;
