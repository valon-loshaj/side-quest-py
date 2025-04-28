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
    userId: string;
    adventurer_type: string;
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
            console.log('[AdventurerSlice] Sending request to fetch adventurers');
            const response = await apiClient.get<Adventure[]>('/api/v1/adventurers');
            console.log('[AdventurerSlice] Adventurers fetched:', response.data);
            return response.data;
        } catch (error: unknown) {
            console.error('[AdventurerSlice] Error fetching adventurers:', error);
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
            console.log('Creating adventurer with data:', {
                name: adventurerData.name,
                user_id: adventurerData.userId,
                adventurer_type: adventurerData.adventurer_type,
            });

            // Correctly map userId from the request to user_id expected by the API
            const requestPayload = {
                name: adventurerData.name,
                user_id: adventurerData.userId,
                adventurer_type: adventurerData.adventurer_type,
            };

            console.log('Sending request payload:', requestPayload);

            const response = await apiClient.post<AdventurerResponse>(
                '/api/v1/adventurer',
                requestPayload
            );

            console.log('Adventurer created successfully:', response.data);
            return response.data.adventurer;
        } catch (error: unknown) {
            console.error('Error creating adventurer:', error);
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
            console.log('[AdventurerSlice] Getting adventurer with ID:', id);
            const endpoint = `/api/v1/adventurer/${id}`;
            console.log('[AdventurerSlice] API endpoint:', endpoint);

            const response = await apiClient.get<{ adventurer: Adventure }>(endpoint);

            console.log('[AdventurerSlice] Adventurer API response:', response);
            console.log('[AdventurerSlice] Adventurer data:', response.data);

            if (!response.data) {
                console.error('[AdventurerSlice] Empty response data');
                return rejectWithValue('Empty response data from API');
            }

            // Handle both response formats - some endpoints might return { adventurer: {...} }
            // while others might return the adventurer object directly
            const adventurerData = response.data.adventurer || response.data;

            if (!adventurerData) {
                console.error(
                    '[AdventurerSlice] Invalid response structure:',
                    response.data
                );
                return rejectWithValue('Invalid response structure from API');
            }

            return adventurerData;
        } catch (error: unknown) {
            console.error('[AdventurerSlice] Error fetching adventurer:', error);
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
                `/api/v1/adventurer/${data.adventurerId}/quest/${data.questId}`
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
            if (!state.adventurers) {
                state.adventurers = [];
            }
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
                adv => adv.name === action.payload.adventurer.name
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
