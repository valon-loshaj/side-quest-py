import React, { useEffect, useState, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { useAdventurer } from '../store/hooks/useAdventurer';
import { useQuest } from '../store/hooks/useQuest';
import styles from '../styles/Dashboard.module.css';
import { logout } from '../store/slices/authSlice';
import { Link } from 'react-router-dom';
import { Quest } from '../types/models';
import { EditingQuestState } from '../store/slices/questSlice';

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
    } = useQuest();
    const dispatch = useAppDispatch();
    const [currentQuestId, setCurrentQuestId] = useState<string | null>(null);
    const [editingQuest, setEditingQuest] = useState<EditingQuestState>({
        id: null,
        field: null,
    });
    const [editValue, setEditValue] = useState<string>('');
    const [initialLoadAttempted, setInitialLoadAttempted] = useState(false);
    const [adventurersLoading, setAdventurersLoading] = useState(false);
    const [questsLoading, setQuestsLoading] = useState(false);
    const adventurersFetchedRef = useRef(false);

    // Debug information
    useEffect(() => {
        console.log('Dashboard: Auth state', {
            user: user?.id,
            authLoading,
            initialLoadAttempted,
            adventurers: adventurers.length,
            currentAdventurer: currentAdventurer?.id || 'none',
            adventurersFetched: adventurersFetchedRef.current,
        });
    }, [
        user,
        authLoading,
        initialLoadAttempted,
        adventurers.length,
        currentAdventurer,
    ]);

    // First useEffect - fetch adventurers once user data is available
    useEffect(() => {
        // Only fetch if we have a user but no adventurers
        if (user && !adventurers.length && !adventurersFetchedRef.current) {
            console.log('Dashboard: No adventurers found, fetching adventurers');
            adventurersFetchedRef.current = true;
            setInitialLoadAttempted(true);
            setAdventurersLoading(true);
            fetchAllAdventurers()
                .then(() => {
                    console.log('Dashboard: Adventurers fetched successfully');
                })
                .catch(err => {
                    console.error('Dashboard: Error fetching adventurers:', err);
                })
                .finally(() => {
                    setAdventurersLoading(false);
                });
        } else if (user && user.adventurers?.length && !adventurersFetchedRef.current) {
            console.log('Dashboard: User has adventurers:', user.adventurers);
            adventurersFetchedRef.current = true;
        }
    }, [user, adventurers.length, fetchAllAdventurers]);

    // Second useEffect - select the first adventurer if none is selected but adventurers are available
    useEffect(() => {
        if (!currentAdventurer && adventurers.length > 0) {
            console.log(
                'Dashboard: No current adventurer selected, selecting the first one:',
                adventurers[0].name
            );
            selectAdventurer(adventurers[0]);
        }
    }, [adventurers, currentAdventurer, selectAdventurer]);

    // Third useEffect - fetch quests for the current adventurer
    useEffect(() => {
        // Fetch quests if we have an adventurer
        if (currentAdventurer?.id) {
            console.log(`Fetching quests for adventurer ID: ${currentAdventurer.id}`);
            console.log('Current adventurer:', currentAdventurer);
            setQuestsLoading(true);
            fetchAllQuests(currentAdventurer.id)
                .then(result => {
                    console.log('Fetch quests result:', result);
                    if (result.meta.requestStatus === 'fulfilled') {
                        console.log('Quests fetched successfully:', result.payload);
                    } else {
                        console.error('Failed to fetch quests:', result.payload);
                    }
                })
                .catch(err => {
                    console.error('Error in fetchAllQuests:', err);
                })
                .finally(() => {
                    setQuestsLoading(false);
                });
        } else {
            console.log('No current adventurer or adventurer ID, skipping quest fetch');
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
        console.log('Dashboard: Auth loading');
        return <div className={styles.loadingContainer}>Authenticating...</div>;
    }

    if (!user) {
        console.log('Dashboard: User not available yet');
        return <div className={styles.loadingContainer}>Loading user data...</div>;
    }

    // Show a loading state for adventurers
    if (adventurersLoading) {
        console.log('Dashboard: Loading adventurers');
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

                {/* Debug section */}
                <div className={styles.debugSection}>
                    <h3>Debug Info:</h3>
                    <p>Loading: {loading ? 'true' : 'false'}</p>
                    <p>Quests Loading: {questsLoading ? 'true' : 'false'}</p>
                    <p>Error: {error || 'none'}</p>
                    <p>Current Adventurer ID: {currentAdventurer?.id || 'none'}</p>
                    <button className={styles.logoutButton} onClick={handleLogout}>
                        Logout
                    </button>
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
            updateQuestDetails(questId, {
                completed: !quest.completed,
                adventurer_id: currentAdventurer.id,
            }).then(result => {
                if (result.meta.requestStatus !== 'fulfilled') {
                    // Show an error message
                    alert(
                        `Error updating quest completion status: ${error || 'Unknown error'}`
                    );
                }
            });
        }
    };

    // Set a quest as current
    const setAsCurrent = (questId: string) => {
        setCurrentQuestId(questId);
        const quest = quests.find(q => q.id === questId);
        if (quest) {
            selectQuest(quest);
        }
    };

    // Move a quest up in the list
    const moveQuestUp = (index: number) => {
        if (index <= 0) return; // Can't move up if already at the top

        // For an actual implementation we might need an endpoint to update quest positions
        // This is a client-side only solution for now
        const questToMove = quests[index];
        const questToSwap = quests[index - 1];

        // Since we don't have a position field in the backend, we're just reordering in the UI
        const newQuests = [...quests];
        newQuests[index] = questToSwap;
        newQuests[index - 1] = questToMove;

        // Update currentQuestId if needed
        // Note: In a real implementation we would need to update the backend
    };

    // Move a quest down in the list
    const moveQuestDown = (index: number) => {
        if (index >= quests.length - 1) return; // Can't move down if already at the bottom

        // For an actual implementation we might need an endpoint to update quest positions
        // This is a client-side only solution for now
        const questToMove = quests[index];
        const questToSwap = quests[index + 1];

        // Since we don't have a position field in the backend, we're just reordering in the UI
        const newQuests = [...quests];
        newQuests[index] = questToSwap;
        newQuests[index + 1] = questToMove;

        // Update currentQuestId if needed
        // Note: In a real implementation we would need to update the backend
    };

    // Delete a quest from the list
    const deleteQuest = (questId: string) => {
        // If this is the current quest, clear current quest
        if (questId === currentQuestId) {
            setCurrentQuestId(null);
        }

        // Remove quest through API
        removeQuest(questId).then(result => {
            if (result.meta.requestStatus !== 'fulfilled') {
                // Show an error message
                alert(`Error deleting quest: ${error || 'Unknown error'}`);
            }
        });
    };

    // Handle editing a quest field
    const startEditing = (questId: string, field: 'title' | 'experienceReward') => {
        const quest = quests.find(q => q.id === questId);
        if (!quest) return;

        setEditingQuest({ id: questId, field });

        // Map frontend field names to API field names
        const fieldMapping: Record<string, string> = {
            title: 'title',
            experienceReward: 'experience_reward',
        };

        // Use the mapped field name to access the quest property
        setEditValue(String(quest[fieldMapping[field] as keyof Quest]));
    };

    // Save edited value
    const saveEditedValue = () => {
        if (!editingQuest.id || !editingQuest.field || !currentAdventurer?.id) return;

        const quest = quests.find(q => q.id === editingQuest.id);
        if (!quest) return;

        if (editingQuest.field === 'title') {
            updateQuestDetails(editingQuest.id, {
                title: editValue,
                adventurer_id: currentAdventurer.id,
            }).then(result => {
                if (result.meta.requestStatus !== 'fulfilled') {
                    alert(`Error updating quest title: ${error || 'Unknown error'}`);
                }
            });
        } else if (editingQuest.field === 'experienceReward') {
            const xpValue = parseInt(editValue, 10);
            if (!isNaN(xpValue)) {
                updateQuestDetails(editingQuest.id, {
                    experience_reward: xpValue,
                    adventurer_id: currentAdventurer.id,
                }).then(result => {
                    if (result.meta.requestStatus !== 'fulfilled') {
                        alert(
                            `Error updating quest experience reward: ${error || 'Unknown error'}`
                        );
                    }
                });
            }
        }

        // Reset editing state
        setEditingQuest({ id: null, field: null });
        setEditValue('');
    };

    // Handle input blur or Enter key to save
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

    // Create a new quest
    const createNewQuestHandler = () => {
        if (!currentAdventurer?.id) {
            alert('Please select an adventurer first');
            return;
        }

        console.log(`Creating quest for adventurer ID: ${currentAdventurer.id}`);

        // Create new quest through API
        createNewQuest('New Quest', currentAdventurer.id, 100).then(result => {
            if (result.meta.requestStatus === 'fulfilled') {
                const newQuest = result.payload as Quest;
                // Start editing the title of the new quest
                startEditing(newQuest.id, 'title');
                // Set as current quest
                setCurrentQuestId(newQuest.id);
            } else {
                alert(`Error creating quest: ${error || 'Unknown error'}`);
            }
        });
    };

    // Sort quests by completion status (incomplete first)
    const sortedQuests = [...quests].sort((a, b) => {
        if (a.completed === b.completed) return 0;
        return a.completed ? 1 : -1;
    });

    // Render quest card content - used by both current quest and quest list
    const renderQuestContent = (quest: Quest) => {
        const isEditing = editingQuest.id === quest.id;

        return (
            <>
                <div className={styles.questCardHeader}>
                    <div
                        className={`${styles.completionIndicator} ${
                            quest.completed ? styles.completed : ''
                        }`}
                        onClick={() => toggleQuestCompletion(quest.id)}
                    ></div>
                    <div className={styles.questInfo}>
                        {isEditing && editingQuest.field === 'title' ? (
                            <input
                                type="text"
                                value={editValue}
                                onChange={e => setEditValue(e.target.value)}
                                onBlur={handleInputBlur}
                                onKeyDown={handleInputKeyDown}
                                autoFocus
                            />
                        ) : (
                            <h3 onClick={() => startEditing(quest.id, 'title')}>
                                {quest.title}
                            </h3>
                        )}

                        {isEditing && editingQuest.field === 'experienceReward' ? (
                            <input
                                type="number"
                                className={styles.xpInput}
                                value={editValue}
                                onChange={e => setEditValue(e.target.value)}
                                onBlur={handleInputBlur}
                                onKeyDown={handleInputKeyDown}
                                autoFocus
                                min="1"
                            />
                        ) : (
                            <p
                                onClick={() =>
                                    startEditing(quest.id, 'experienceReward')
                                }
                            >
                                XP: {quest.experience_reward}
                            </p>
                        )}
                    </div>
                </div>
            </>
        );
    };

    // Show loading state
    if (loading && quests.length === 0) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.loadingMessage}>
                    Loading quests... Adventurer ID: {currentAdventurer?.id}
                </div>

                {/* Debug section */}
                <div className={styles.debugSection}>
                    <h3>Debug Info:</h3>
                    <p>Loading: {loading ? 'true' : 'false'}</p>
                    <p>Error: {error || 'none'}</p>
                    <p>Current Adventurer ID: {currentAdventurer?.id || 'none'}</p>
                    <p>Quests Count: {quests.length}</p>
                    <details>
                        <summary>Current Adventurer Data</summary>
                        <pre>
                            {currentAdventurer
                                ? JSON.stringify(currentAdventurer, null, 2)
                                : 'No adventurer'}
                        </pre>
                    </details>
                    <details>
                        <summary>Quests Data</summary>
                        <pre>
                            {quests.length
                                ? JSON.stringify(quests, null, 2)
                                : 'No quests'}
                        </pre>
                    </details>
                    <h4>Actions</h4>
                    <div className={styles.debugActions}>
                        <button
                            onClick={() => {
                                if (currentAdventurer?.id) {
                                    console.log(
                                        'Retrying fetch with adventurer ID:',
                                        currentAdventurer.id
                                    );
                                    fetchAllQuests(currentAdventurer.id);
                                }
                            }}
                            className={styles.debugButton}
                            disabled={!currentAdventurer?.id}
                        >
                            Retry Fetch Quests
                        </button>

                        <button
                            onClick={() => {
                                console.log('Forcing adventurer refresh');
                                fetchAllAdventurers();
                            }}
                            className={styles.debugButton}
                        >
                            Refresh Adventurers
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Show error state if we have an error and no quests
    if (error && quests.length === 0) {
        return (
            <div className={styles.dashboard}>
                <h1>Dashboard</h1>
                <div className={styles.errorMessage}>Error loading quests: {error}</div>

                {/* Debug section */}
                <div className={styles.debugSection}>
                    <h3>Debug Info:</h3>
                    <p>Loading: {loading ? 'true' : 'false'}</p>
                    <p>Error: {error || 'none'}</p>
                    <p>Current Adventurer ID: {currentAdventurer?.id || 'none'}</p>
                    <p>Quests Count: {quests.length}</p>
                    <details>
                        <summary>Current Adventurer Data</summary>
                        <pre>
                            {currentAdventurer
                                ? JSON.stringify(currentAdventurer, null, 2)
                                : 'No adventurer'}
                        </pre>
                    </details>
                    <details>
                        <summary>Quests Data</summary>
                        <pre>
                            {quests.length
                                ? JSON.stringify(quests, null, 2)
                                : 'No quests'}
                        </pre>
                    </details>
                    <h4>Actions</h4>
                    <div className={styles.debugActions}>
                        <button
                            onClick={() => {
                                if (currentAdventurer?.id) {
                                    console.log(
                                        'Retrying fetch with adventurer ID:',
                                        currentAdventurer.id
                                    );
                                    fetchAllQuests(currentAdventurer.id);
                                }
                            }}
                            className={styles.debugButton}
                            disabled={!currentAdventurer?.id}
                        >
                            Retry Fetch Quests
                        </button>

                        <button
                            onClick={() => {
                                console.log('Forcing adventurer refresh');
                                fetchAllAdventurers();
                            }}
                            className={styles.debugButton}
                        >
                            Refresh Adventurers
                        </button>
                    </div>
                </div>

                <button className={styles.logoutButton} onClick={handleLogout}>
                    Logout
                </button>
            </div>
        );
    }

    // Show message if no adventurer is selected
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
                            <div className={styles.currentQuestCard}>
                                {renderQuestContent(currentQuest)}
                                <div className={styles.questCardFooter}>
                                    <div className={styles.questActions}>
                                        <button
                                            className={styles.deleteButton}
                                            onClick={() => deleteQuest(currentQuest.id)}
                                            title="Delete quest"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            </div>
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
                    <button
                        className={`${styles.logoutButton} ${styles.createQuestButton}`}
                        onClick={createNewQuestHandler}
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
                                <div key={quest.id} className={styles.questCard}>
                                    {renderQuestContent(quest)}
                                    <div className={styles.questCardFooter}>
                                        <div className={styles.questActions}>
                                            <button
                                                className={styles.markCurrentButton}
                                                onClick={() => setAsCurrent(quest.id)}
                                                title="Mark as current quest"
                                            >
                                                ★
                                            </button>
                                            <button
                                                className={`${styles.moveButton} ${index === 0 ? styles.disabled : ''}`}
                                                onClick={() => moveQuestUp(index)}
                                                disabled={index === 0}
                                                title="Move up"
                                            >
                                                ▲
                                            </button>
                                            <button
                                                className={`${styles.moveButton} ${index === sortedQuests.length - 1 ? styles.disabled : ''}`}
                                                onClick={() => moveQuestDown(index)}
                                                disabled={
                                                    index === sortedQuests.length - 1
                                                }
                                                title="Move down"
                                            >
                                                ▼
                                            </button>
                                            <button
                                                className={styles.deleteButton}
                                                onClick={() => deleteQuest(quest.id)}
                                                title="Delete quest"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                </div>
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
