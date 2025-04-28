import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAdventurer } from '../store/hooks/useAdventurer';
import { useAppSelector } from '../store';
import styles from '../styles/pages/AdventurerHub.module.css';

const adventurerTypes = ['Amazon', 'Sorceress', 'Paladan', 'Barbarian'] as const;
type AdventurerType = (typeof adventurerTypes)[number];

const AdventurerHub: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const {
        currentAdventurer,
        loading: adventurerLoading,
        error: adventurerError,
        createNewAdventurer,
        fetchAdventurerById,
        selectAdventurer,
    } = useAdventurer();

    const { user } = useAppSelector(state => state.auth);
    const [adventurerName, setAdventurerName] = useState('');
    const [adventurerType, setAdventurerType] = useState<AdventurerType>('Amazon');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const isCreating = id === 'new';

    useEffect(() => {
        // Reset error state
        setError(null);

        if (isCreating) {
            // Nothing to fetch for new adventurer
            return;
        }

        if (id) {
            console.log('[AdventurerHub] ID from URL parameter:', id);
            console.log('[AdventurerHub] ID type:', typeof id);

            // Check if adventurer data is already available in user object
            const foundAdventurer = user?.adventurers?.find(
                adv => adv && adv.id === id
            );

            console.log('[AdventurerHub] User data:', user);
            console.log('[AdventurerHub] User adventurers:', user?.adventurers);

            if (foundAdventurer) {
                // Use adventurer from user object
                selectAdventurer(foundAdventurer);
            } else {
                // Fetch from API if not available
                setLoading(true);
                console.log(
                    '[AdventurerHub] Fetching adventurer from API with ID:',
                    id
                );
                fetchAdventurerById(id)
                    .unwrap()
                    .then(adventurer => {
                        console.log('[AdventurerHub] API response:', adventurer);
                        console.log(
                            '[AdventurerHub] API response isEmpty:',
                            !adventurer
                        );
                        console.log(
                            '[AdventurerHub] API response type:',
                            typeof adventurer
                        );

                        // Log detailed structure to debug
                        console.log(
                            '[AdventurerHub] Response structure:',
                            JSON.stringify(adventurer, null, 2)
                        );

                        // The thunk already extracts adventurer from response.data.adventurer
                        // No need to access .adventurer again
                        const adventurerData = adventurer;

                        // More flexible validation
                        if (!adventurerData) {
                            console.error(
                                '[AdventurerHub] No adventurer data received:',
                                adventurerData
                            );
                            throw new Error('No adventurer data received');
                        }

                        if (!adventurerData.id) {
                            console.error(
                                '[AdventurerHub] Missing ID in adventurer data:',
                                adventurerData
                            );
                            throw new Error('Invalid adventurer data: missing ID');
                        }

                        // Successful validation, select the adventurer
                        console.log(
                            '[AdventurerHub] Selecting adventurer:',
                            adventurerData
                        );
                        selectAdventurer(adventurerData);
                    })
                    .catch(err => {
                        console.error(
                            '[AdventurerHub] Error fetching adventurer:',
                            err
                        );
                        setError(
                            typeof err === 'string'
                                ? err
                                : err.message || 'Failed to load adventurer'
                        );
                    })
                    .finally(() => {
                        setLoading(false);
                    });
            }
        }
    }, [id, user, isCreating, fetchAdventurerById, selectAdventurer]);

    useEffect(() => {
        if (
            currentAdventurer &&
            !isCreating &&
            currentAdventurer.name &&
            typeof currentAdventurer.name === 'string'
        ) {
            setAdventurerName(currentAdventurer.name);

            // Set adventurer type if available, default to Amazon if not
            if (
                currentAdventurer.adventurer_type &&
                adventurerTypes.includes(
                    currentAdventurer.adventurer_type as AdventurerType
                )
            ) {
                setAdventurerType(currentAdventurer.adventurer_type as AdventurerType);
            } else {
                setAdventurerType('Amazon');
            }
        }
    }, [currentAdventurer, isCreating]);

    const handleCreateAdventurer = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!adventurerName.trim()) return;

        setLoading(true);
        setError(null);

        try {
            // Check if user exists and has an id before creating adventurer
            if (!user || !user.id) {
                throw new Error('User is not authenticated');
            }

            console.log(
                '[AdventurerHub] Creating new adventurer with name, type and userId:',
                adventurerName,
                adventurerType,
                user.id
            );
            await createNewAdventurer(adventurerName, user.id, adventurerType);
            navigate('/dashboard');
        } catch (err) {
            setError(typeof err === 'string' ? err : 'Failed to create adventurer');
            console.error('Failed to create adventurer:', err);
        } finally {
            setLoading(false);
        }
    };

    const isLoading = loading || adventurerLoading;
    const displayError = error || adventurerError;

    // Validate current adventurer
    const isValidAdventurer =
        currentAdventurer &&
        currentAdventurer.id &&
        currentAdventurer.name &&
        typeof currentAdventurer.name === 'string';

    if (isLoading) {
        return <div className={styles.loading}>Loading...</div>;
    }

    if (displayError) {
        return <div className={styles.error}>{displayError}</div>;
    }

    return (
        <div className={styles.adventurerHub}>
            {isCreating ? (
                <div className={styles.createAdventurer}>
                    <h1>Create New Adventurer</h1>
                    <div className={styles.avatarPreview}>
                        <img
                            src={`/images/${adventurerType.toLowerCase()}.png`}
                            alt={`${adventurerType} avatar`}
                            className={styles.avatarImage}
                        />
                    </div>
                    <form onSubmit={handleCreateAdventurer}>
                        <div className={styles.formGroup}>
                            <label htmlFor="adventurerName">Adventurer Name</label>
                            <input
                                id="adventurerName"
                                type="text"
                                value={adventurerName}
                                onChange={e => setAdventurerName(e.target.value)}
                                placeholder="Enter a name for your adventurer"
                                required
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label htmlFor="adventurerType">Adventurer Type</label>
                            <select
                                id="adventurerType"
                                value={adventurerType}
                                onChange={e =>
                                    setAdventurerType(e.target.value as AdventurerType)
                                }
                                required
                            >
                                {adventurerTypes.map(type => (
                                    <option key={type} value={type}>
                                        {type}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button
                            type="submit"
                            className={styles.createButton}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating...' : 'Create Adventurer'}
                        </button>
                    </form>
                </div>
            ) : isValidAdventurer ? (
                <div className={styles.adventurerDetails}>
                    <div className={styles.avatarNameContainer}>
                        <div className={styles.avatarPreview}>
                            <img
                                src={`/images/${(currentAdventurer.adventurer_type || adventurerType).toLowerCase()}.png`}
                                alt={`${currentAdventurer.adventurer_type || adventurerType} avatar`}
                                className={styles.avatarImage}
                            />
                        </div>
                        <div className={styles.nameTypeContainer}>
                            <h1>{currentAdventurer.name}</h1>
                            <p className={styles.adventurerType}>
                                {currentAdventurer.adventurer_type || adventurerType}
                            </p>
                        </div>
                    </div>
                    <div className={styles.adventurerInfo}>
                        <p>Level: {currentAdventurer.level || 1}</p>
                        <p>Experience: {currentAdventurer.experience || 0}</p>
                    </div>
                    {/* Additional adventurer details will go here in future iterations */}
                </div>
            ) : (
                <div className={styles.noAdventurer}>
                    <p>Adventurer not found. Would you like to create a new one?</p>
                    <button
                        onClick={() => navigate('/adventurer/new')}
                        className={styles.createButton}
                    >
                        Create New Adventurer
                    </button>
                </div>
            )}
            <button
                onClick={() => navigate('/dashboard')}
                className={styles.backButton}
            >
                Back to Dashboard
            </button>
        </div>
    );
};

export default AdventurerHub;
