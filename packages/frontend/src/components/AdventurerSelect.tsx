import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAdventurer } from '../store/hooks/useAdventurer';
import styles from '../styles/components/AdventurerSelect.module.css';

const AdventurerSelect: React.FC = () => {
    const {
        adventurers,
        currentAdventurer,
        loading,
        fetchAllAdventurers,
        selectAdventurer,
    } = useAdventurer();

    useEffect(() => {
        // Fetch adventurers in all cases to ensure we have data
        fetchAllAdventurers();

        // If we have adventurers and no currentAdventurer is selected, select the first one
        if (adventurers?.length && !currentAdventurer) {
            selectAdventurer(adventurers[0]);
        }
    }, [fetchAllAdventurers, selectAdventurer, adventurers, currentAdventurer]);

    // Validate and filter adventurers to ensure all have required fields
    const validAdventurers = React.useMemo(() => {
        // Filter out any invalid adventurers (missing required fields)
        if (adventurers && Array.isArray(adventurers)) {
            return adventurers.filter(
                adv => adv && adv.name && typeof adv.name === 'string'
            );
        }

        // If all else fails, return an empty array
        return [];
    }, [adventurers]);

    if (loading && validAdventurers.length === 0) {
        return <div className={styles.loading}>Loading adventurers...</div>;
    }

    return (
        <div className={styles.adventurerSelectSidebar}>
            <h2 className={styles.title}>Your Adventurers</h2>

            <div className={styles.adventurerListSidebar}>
                {validAdventurers.length === 0 ? (
                    <div className={styles.noAdventurers}>
                        No adventurers found. Create your first adventurer to begin your
                        journey!
                    </div>
                ) : (
                    validAdventurers.map(adventurer => (
                        <div
                            key={adventurer.name}
                            className={`${styles.adventurerCardSidebar} ${currentAdventurer?.name === adventurer.name ? styles.selected : ''}`}
                            onClick={() => selectAdventurer(adventurer)}
                        >
                            <div className={styles.avatarContainer}>
                                <div className={styles.avatar}>
                                    {adventurer.name.charAt(0).toUpperCase()}
                                </div>
                            </div>
                            <div className={styles.adventurerInfo}>
                                <h3 className={styles.adventurerName}>
                                    {adventurer.name}
                                </h3>
                                <p className={styles.adventurerLevel}>
                                    Level {adventurer.level || 1}
                                </p>
                            </div>
                            <Link
                                to={`/adventurer/${adventurer.name}`}
                                className={styles.manageLink}
                            >
                                Manage
                            </Link>
                        </div>
                    ))
                )}

                <Link to="/adventurer/new" className={styles.newAdventurerCardSidebar}>
                    <div className={styles.newAdventurerIcon}>+</div>
                    <div className={styles.newAdventurerText}>New Adventurer</div>
                </Link>
            </div>
        </div>
    );
};

export default AdventurerSelect;
