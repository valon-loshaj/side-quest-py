import React, { useEffect, useState, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { useAdventurer } from '../store/hooks/useAdventurer';
import { useQuest } from '../store/hooks/useQuest';
import styles from '../styles/Dashboard.module.css';
import { logout, getCurrentUser } from '../store/slices/authSlice';
import { Link } from 'react-router-dom';
import { Quest } from '../types/models';
import { EditingQuestState } from '../store/slices/questSlice';
import QuestCard from '../components/QuestCard';
import QuestCreateModal from '../components/QuestCreateModal';

const Dashboard: React.FC = () => {
    const { user, loading: authLoading } = useAppSelector(state => state.auth);
    const { currentAdventurer, adventurers, fetchAllAdventurers, selectAdventurer } =
        useAdventurer();
    const {
        quests,
        loading,
        error,
        fetchAllQuests,
        createNewQuest,
        updateQuestDetails,
        removeQuest,
        selectQuest,
        completeQuest,
    } = useQuest();
    const dispatch = useAppDispatch();
    const [currentQuestId, setCurrentQuestId] = useState<string | null>(null);
    const [editingQuest, setEditingQuest] = useState<EditingQuestState>({
        id: null,
        field: null,
    });
    const [editValue, setEditValue] = useState<string>('');
    const [adventurersLoading, setAdventurersLoading] = useState(false);
    const [questsLoading, setQuestsLoading] = useState(false);
    const adventurersFetchedRef = useRef(false);
    const userFetchedRef = useRef(false);
    const [isQuestCreateModalOpen, setIsQuestCreateModalOpen] = useState(false);
    const [updatingQuestIds, setUpdatingQuestIds] = useState<string[]>([]);

    // Fetch user data if not already loaded
    useEffect(() => {
        if (!user && !userFetchedRef.current && !authLoading) {
            userFetchedRef.current = true;
            dispatch(getCurrentUser());
        }
    }, [user, dispatch, authLoading]);

    // First useEffect - fetch adventurers once user data is available
    useEffect(() => {
        // Only fetch if we have a user but no adventurers
        console.log('[Dashboard] Checking if should fetch adventurers:', {
            user: !!user,
            adventurersExist: !!adventurers && !!adventurers.length,
            alreadyFetched: adventurersFetchedRef.current,
        });

        if (
            user &&
            (!adventurers || !adventurers.length) &&
            !adventurersFetchedRef.current
        ) {
            console.log('[Dashboard] Fetching adventurers for user:', user.id);
            adventurersFetchedRef.current = true;
            setAdventurersLoading(true);
            fetchAllAdventurers().finally(() => {
                console.log('[Dashboard] Finished fetching adventurers');
                setAdventurersLoading(false);
            });
        }
    }, [user, adventurers, fetchAllAdventurers]);

    // Second useEffect - select the first adventurer if none is selected but adventurers are available
    useEffect(() => {
        if (!currentAdventurer && adventurers && adventurers.length > 0) {
            selectAdventurer(adventurers[0]);
        }
    }, [adventurers, currentAdventurer, selectAdventurer]);

    // Third useEffect - fetch quests for the current adventurer
    useEffect(() => {
        // Fetch quests if we have an adventurer
        if (currentAdventurer?.id) {
            setQuestsLoading(true);
            fetchAllQuests(currentAdventurer.id).finally(() => {
                setQuestsLoading(false);
            });
        }
    }, [currentAdventurer, fetchAllQuests]);

    useEffect(() => {
        // Set a default current quest if none exists
        if (!currentQuestId && quests.length > 0) {
            const activeQuests = quests.filter(q => !q.completed);
            if (activeQuests.length > 0) {
                setCurrentQuestId(activeQuests[0].id);
            }
        }
    }, [quests, currentQuestId]);

    const handleLogout = () => {
        dispatch(logout());
    };

    // Don't return null during initial load, show a loading state instead
    if (authLoading) {
        return <div className={styles.loadingContainer}>Authenticating...</div>;
    }

    if (!user) {
        return <div className={styles.loadingContainer}>Loading user data...</div>;
    }

    // Show a loading state for adventurers
    if (adventurersLoading) {
        return <div className={styles.loadingContainer}>Loading adventurers...</div>;
    }

    // Show a more detailed loading state
    if (loading || questsLoading) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.loadingMessage}>
                    {questsLoading ? 'Loading quests...' : 'Loading...'}
                    {currentAdventurer && <> for {currentAdventurer.name}</>}
                </div>
            </div>
        );
    }

    // Validate currentAdventurer before displaying
    const isValidAdventurer =
        currentAdventurer &&
        currentAdventurer.id &&
        currentAdventurer.name &&
        typeof currentAdventurer.name === 'string';

    // Get the current quest object
    const currentQuest = quests.find(q => q.id === currentQuestId) || null;

    // Handle completing a quest
    const toggleQuestCompletion = (questId: string) => {
        const quest = quests.find(q => q.id === questId);
        if (quest && currentAdventurer?.id) {
            // Mark this quest as updating
            setUpdatingQuestIds(prev => [...prev, questId]);

            // Perform the update
            completeQuest(questId, currentAdventurer.id, !quest.completed)
                .then(result => {
                    console.log('Quest update result:', result);
                    if (result.meta.requestStatus === 'fulfilled') {
                        // Update is successful, no need to do anything else as Redux has updated
                        console.log('Quest completion status updated successfully');
                    } else {
                        // If it fails, show an error
                        console.error('Failed to update quest status:', result.payload);
                    }
                })
                .catch(err => {
                    console.error('Error updating quest:', err);
                })
                .finally(() => {
                    // Always remove the updating indicator when done
                    setUpdatingQuestIds(prev => prev.filter(id => id !== questId));
                });
        }
    };

    const setAsCurrent = (questId: string) => {
        setCurrentQuestId(questId);
        const quest = quests.find(q => q.id === questId);
        if (quest) {
            selectQuest(quest);
        }
    };

    const moveQuestUp = (index: number) => {
        if (index <= 0) return; // Can't move up if already at the top

        const questToMove = quests[index];
        const questToSwap = quests[index - 1];

        const newQuests = [...quests];
        newQuests[index] = questToSwap;
        newQuests[index - 1] = questToMove;
    };

    const moveQuestDown = (index: number) => {
        if (index >= quests.length - 1) return; // Can't move down if already at the bottom
        const questToMove = quests[index];
        const questToSwap = quests[index + 1];
        const newQuests = [...quests];
        newQuests[index] = questToSwap;
        newQuests[index + 1] = questToMove;
    };

    const deleteQuest = (questId: string) => {
        if (questId === currentQuestId) {
            setCurrentQuestId(null);
        }

        removeQuest(questId);
    };

    const startEditing = (questId: string, field: 'title' | 'experienceReward') => {
        const quest = quests.find(q => q.id === questId);
        if (!quest) return;

        setEditingQuest({ id: questId, field });

        const fieldMapping: Record<string, string> = {
            title: 'title',
            experienceReward: 'experience_reward',
        };

        setEditValue(String(quest[fieldMapping[field] as keyof Quest]));
    };

    const saveEditedValue = () => {
        if (!editingQuest.id || !editingQuest.field || !currentAdventurer?.id) return;

        const quest = quests.find(q => q.id === editingQuest.id);
        if (!quest) return;

        // Mark this quest as updating
        setUpdatingQuestIds(prev => [...prev, editingQuest.id!]);

        let updatePromise;
        if (editingQuest.field === 'title') {
            updatePromise = updateQuestDetails(editingQuest.id, {
                title: editValue,
                adventurer_id: currentAdventurer.id,
            });
        } else if (editingQuest.field === 'experienceReward') {
            const xpValue = parseInt(editValue, 10);
            if (!isNaN(xpValue)) {
                updatePromise = updateQuestDetails(editingQuest.id, {
                    experience_reward: xpValue,
                    adventurer_id: currentAdventurer.id,
                });
            }
        }

        if (updatePromise) {
            updatePromise
                .then(result => {
                    console.log('Quest update result:', result);
                    if (result.meta.requestStatus === 'fulfilled') {
                        console.log('Quest details updated successfully');
                    } else {
                        console.error(
                            'Failed to update quest details:',
                            result.payload
                        );
                    }
                })
                .catch(err => {
                    console.error('Error updating quest details:', err);
                })
                .finally(() => {
                    // Always remove the updating indicator when done
                    setUpdatingQuestIds(prev =>
                        prev.filter(id => id !== editingQuest.id!)
                    );
                });
        } else {
            // If no promise was created, remove from updating
            setUpdatingQuestIds(prev => prev.filter(id => id !== editingQuest.id!));
        }

        setEditingQuest({ id: null, field: null });
        setEditValue('');
    };

    const handleInputBlur = () => {
        saveEditedValue();
    };

    const handleInputKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            saveEditedValue();
        } else if (e.key === 'Escape') {
            setEditingQuest({ id: null, field: null });
            setEditValue('');
        }
    };

    const createNewQuestHandler = (questData: Partial<Quest>) => {
        if (!currentAdventurer?.id) {
            alert('Please select an adventurer first');
            return;
        }

        // Ensure we have an adventurer ID before creating quest
        const adventurerId = currentAdventurer.id;

        console.log('Creating quest with data:', {
            title: questData.title || 'New Quest',
            adventurerId: adventurerId,
            experienceReward: questData.experience_reward || 100,
        });

        createNewQuest(
            questData.title || 'New Quest',
            adventurerId,
            questData.experience_reward || 100
        )
            .then(result => {
                console.log('Quest creation result:', result);

                if (result.meta.requestStatus === 'fulfilled' && result.payload) {
                    // Make sure payload exists and has an id property
                    const newQuest = result.payload as Quest;
                    console.log('New quest created:', newQuest);

                    if (newQuest && newQuest.id) {
                        setCurrentQuestId(newQuest.id);
                    } else {
                        console.error('Created quest has no ID:', newQuest);
                    }
                    setIsQuestCreateModalOpen(false);
                } else {
                    // When there's an error, the payload contains the error message
                    const errorMessage = result.payload || 'Unknown error';
                    console.error('Error creating quest:', result);
                    alert(`Error creating quest: ${errorMessage}`);
                }
            })
            .catch(err => {
                console.error('Failed to create quest:', err);
                alert('Failed to create quest. See console for details.');
            });
    };

    const sortedQuests = [...quests].sort((a, b) => {
        if (a.completed === b.completed) return 0;
        return a.completed ? 1 : -1;
    });

    if (loading && quests.length === 0) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.loadingMessage}>Loading quests...</div>
            </div>
        );
    }

    if (error && quests.length === 0) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.errorMessage}>Error loading quests: {error}</div>

                <button className={styles.logoutButton} onClick={handleLogout}>
                    Logout
                </button>
            </div>
        );
    }

    if (!isValidAdventurer) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.welcomeMessage}>Welcome, {user.username}!</div>
                <div className={styles.noAdventurerMessage}>
                    Please select or create an adventurer to manage quests.
                </div>
                <button
                    type="button"
                    className={styles.logoutButton}
                    onClick={handleLogout}
                >
                    Logout
                </button>
            </div>
        );
    }

    return (
        <div className={styles.dashboard}>
            <h1>Dashboard</h1>
            <div className={styles.welcomeMessage}>Welcome, {user.username}!</div>

            <div className={styles.dashboardLayout}>
                <div className={styles.mainColumn}>
                    {isValidAdventurer && (
                        <div className={styles.currentAdventurer}>
                            <h2>Current Adventurer</h2>
                            <div className={styles.avatarContainer}>
                                <div className={styles.avatarCircle}>
                                    <img
                                        src={`/images/${(currentAdventurer.adventurer_type || 'Amazon').toLowerCase()}.png`}
                                        alt={`${currentAdventurer.adventurer_type || 'Amazon'} avatar`}
                                        className={styles.avatarImage}
                                    />
                                </div>
                            </div>
                            <p className={styles.adventurerName}>
                                {currentAdventurer.name}
                            </p>
                            <p className={styles.adventurerLevel}>
                                Level {currentAdventurer.level || 1}
                            </p>
                            <p className={styles.adventurerId}>
                                ID: {currentAdventurer.id}
                            </p>
                            <Link
                                to={`/adventurer/${currentAdventurer.id}`}
                                className={styles.manageAdventurerLink}
                            >
                                Manage Adventurer
                            </Link>
                        </div>
                    )}

                    <div className={styles.currentQuestSection}>
                        <h2>Current Quest</h2>
                        {currentQuest ? (
                            <QuestCard
                                quest={currentQuest}
                                isCurrent={true}
                                isUpdating={updatingQuestIds.includes(currentQuest.id)}
                                onToggleCompletion={toggleQuestCompletion}
                                onEdit={startEditing}
                                onSaveEdit={saveEditedValue}
                                onInputChange={setEditValue}
                                onInputBlur={handleInputBlur}
                                onInputKeyDown={handleInputKeyDown}
                                onDelete={deleteQuest}
                                editingQuest={editingQuest}
                                editValue={editValue}
                            />
                        ) : (
                            <p className={styles.noQuestMessage}>
                                {quests.length > 0
                                    ? 'Select a quest from the list to make it your current focus'
                                    : 'Create a new quest to get started'}
                            </p>
                        )}
                    </div>
                </div>

                <div className={styles.allQuestsSection}>
                    <h2>All Quests</h2>
                    <QuestCreateModal
                        isOpen={isQuestCreateModalOpen}
                        onClose={() => setIsQuestCreateModalOpen(false)}
                        onSubmit={createNewQuestHandler}
                        adventurerId={currentAdventurer?.id || ''}
                    />
                    <button
                        className={`${styles.logoutButton} ${styles.createQuestButton}`}
                        onClick={() =>
                            setIsQuestCreateModalOpen(!isQuestCreateModalOpen)
                        }
                        disabled={!currentAdventurer?.id}
                    >
                        Create New Quest
                    </button>

                    {sortedQuests.length === 0 ? (
                        <p className={styles.noQuestMessage}>
                            No quests available. Create your first quest to get started!
                        </p>
                    ) : (
                        sortedQuests.map((quest, index) => {
                            // Skip rendering quests that are currently assigned as the current quest
                            if (quest.id === currentQuestId) {
                                return null;
                            }

                            return (
                                <QuestCard
                                    key={quest.id}
                                    quest={quest}
                                    isUpdating={updatingQuestIds.includes(quest.id)}
                                    onToggleCompletion={toggleQuestCompletion}
                                    onEdit={startEditing}
                                    onSaveEdit={saveEditedValue}
                                    onInputChange={setEditValue}
                                    onInputBlur={handleInputBlur}
                                    onInputKeyDown={handleInputKeyDown}
                                    onSetCurrent={setAsCurrent}
                                    onMoveUp={moveQuestUp}
                                    onMoveDown={moveQuestDown}
                                    onDelete={deleteQuest}
                                    index={index}
                                    isLast={index === sortedQuests.length - 1}
                                    editingQuest={editingQuest}
                                    editValue={editValue}
                                />
                            );
                        })
                    )}
                </div>
            </div>

            <button
                type="button"
                className={styles.logoutButton}
                onClick={handleLogout}
            >
                Logout
            </button>
        </div>
    );
};

export default Dashboard;
