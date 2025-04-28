import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import { Quest } from '../../types/models';
import { API_BASE_URL } from '../../config';
import { logApiResponse } from '../../utils/debug';

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

interface UpdateQuestRequest {
    id: string;
    questData: Partial<Quest>;
}

interface EditingQuestState {
    id: string | null;
    field: 'title' | 'experienceReward' | null;
}

const initialState: QuestState = {
    quests: [],
    currentQuest: null,
    loading: false,
    error: null,
};

export const fetchQuests = createAsyncThunk(
    'quest/fetchAll',
    async (adventurerId: string, { rejectWithValue }) => {
        console.log(`Fetching quests for adventurer ID: ${adventurerId}`);
        console.log(`Using API base URL: ${API_BASE_URL}`);

        try {
            // Use the API_BASE_URL constant for consistent API paths
            const response = await apiClient.get(
                `${API_BASE_URL}/quests/${adventurerId}`
            );
            console.log('Raw quest API response:', response);

            // Log the response structure for debugging
            const dataType = typeof response.data;
            console.log(`Response data type: ${dataType}`);

            // The response contains raw data with no wrapping
            if (Array.isArray(response.data)) {
                console.log(`Response contains ${response.data.length} quests`);
                return response.data;
            }

            // If the data is an object but not an array (which usually means an error), check for error property
            if (
                response.data &&
                typeof response.data === 'object' &&
                'error' in response.data
            ) {
                console.error('API returned an error:', response.data.error);
                return rejectWithValue(response.data.error);
            }

            // If we got here but data is empty or not what we expect, log it and return empty array
            console.warn('Unexpected API response format:', response.data);
            return [];
        } catch (error: unknown) {
            console.error('Error in fetchQuests:', error);
            if (error instanceof Error) {
                console.error('Error details:', {
                    message: error.message,
                    stack: error.stack,
                    name: error.name,
                });
                return rejectWithValue(error.message);
            }
            return rejectWithValue('Failed to fetch quests');
        }
    }
);

export const createQuest = createAsyncThunk(
    'quest/create',
    async (questData: CreateQuestRequest, { rejectWithValue }) => {
        try {
            console.log('Sending quest creation request:', {
                title: questData.title,
                experience_reward: questData.experienceReward,
                adventurer_id: questData.adventurerId,
            });

            const response = await apiClient.post<Quest>(`${API_BASE_URL}/quest`, {
                title: questData.title,
                experience_reward: questData.experienceReward,
                adventurer_id: questData.adventurerId,
            });

            logApiResponse('Quest Creation', response);

            if (!response.data) {
                return rejectWithValue('No data received from server');
            }

            console.log('Successfully created quest:', response.data);
            return response.data;
        } catch (error: unknown) {
            console.error('API Error creating quest:', error);
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
            const response = await apiClient.get<Quest>(`${API_BASE_URL}/quest/${id}`);
            return response.data;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to fetch quest';
            return rejectWithValue(errorMessage);
        }
    }
);

export const markQuestAsCompleted = createAsyncThunk(
    'quest/complete',
    async (questData: UpdateQuestRequest, { rejectWithValue }) => {
        try {
            const response = await apiClient.put<Quest>(
                `${API_BASE_URL}/quest/${questData.id}`,
                {
                    completed:
                        questData.questData?.completed !== undefined
                            ? questData.questData.completed
                            : true,
                    adventurer_id: questData.questData?.adventurer_id,
                }
            );

            if (!response.data) {
                console.error('Invalid response format:', response);
                return rejectWithValue('Invalid response data structure');
            }

            console.log('Quest updated successfully:', response.data);
            return response.data;
        } catch (error: unknown) {
            console.error('Error in markQuestAsCompleted:', error);
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to complete quest';
            return rejectWithValue(errorMessage);
        }
    }
);

export const updateQuest = createAsyncThunk(
    'quest/update',
    async (questData: UpdateQuestRequest, { rejectWithValue }) => {
        try {
            const response = await apiClient.put<Quest>(
                `${API_BASE_URL}/quest/${questData.id}`,
                {
                    title: questData.questData.title,
                    experience_reward: questData.questData.experience_reward,
                    completed: questData.questData.completed,
                    adventurer_id: questData.questData.adventurer_id,
                }
            );

            if (!response.data) {
                console.error('Invalid response format:', response);
                return rejectWithValue('Invalid response data structure');
            }

            console.log('Quest details updated successfully:', response.data);
            return response.data;
        } catch (error: unknown) {
            console.error('Error in updateQuest:', error);
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to update quest';
            return rejectWithValue(errorMessage);
        }
    }
);

export const deleteQuest = createAsyncThunk(
    'quest/delete',
    async (id: string, { rejectWithValue }) => {
        try {
            await apiClient.delete(`${API_BASE_URL}/quest/${id}`);
            return id;
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error ? error.message : 'Failed to delete quest';
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
            state.quests.push(action.payload as Quest);
            state.currentQuest = action.payload as Quest;
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

        builder.addCase(updateQuest.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(updateQuest.fulfilled, (state, action) => {
            state.loading = false;
            state.currentQuest = action.payload;

            const index = state.quests.findIndex(
                quest => quest.id === action.payload.id
            );
            if (index !== -1) {
                state.quests[index] = action.payload;
            }
        });
        builder.addCase(updateQuest.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });

        builder.addCase(deleteQuest.pending, state => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(deleteQuest.fulfilled, (state, action) => {
            state.loading = false;
            if (state.currentQuest?.id === action.payload) {
                state.currentQuest = null;
            }
            state.quests = state.quests.filter(quest => quest.id !== action.payload);
        });
        builder.addCase(deleteQuest.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string;
        });
    },
});

export const { clearQuestError, setCurrentQuest } = questSlice.actions;
export default questSlice.reducer;
export type { EditingQuestState };
