import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { useAdventurer } from '../store/hooks/useAdventurer';
import styles from '../styles/Dashboard.module.css';
import { logout } from '../store/slices/authSlice';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
    const { user } = useAppSelector(state => state.auth);
    const { currentAdventurer, fetchAllAdventurers } = useAdventurer();
    const dispatch = useAppDispatch();

    useEffect(() => {
        // Fetch adventurers if they are not available in the user object
        if (!user?.adventurers?.length) {
            fetchAllAdventurers();
        }
    }, [user, fetchAllAdventurers]);

    if (!user) return null;

    const handleLogout = () => {
        dispatch(logout());
    };

    // Validate currentAdventurer before displaying
    const isValidAdventurer =
        currentAdventurer &&
        currentAdventurer.name &&
        typeof currentAdventurer.name === 'string';

    return (
        <div className={styles.dashboard}>
            <h1>Dashboard</h1>
            <div className={styles.welcomeMessage}>Welcome, {user.username}!</div>

            {isValidAdventurer && (
                <div className={styles.currentAdventurer}>
                    <h2>Current Adventurer</h2>
                    <p className={styles.adventurerName}>{currentAdventurer.name}</p>
                    <p className={styles.adventurerLevel}>
                        Level {currentAdventurer.level || 1}
                    </p>
                    <Link
                        to={`/adventurer/${currentAdventurer.name}`}
                        className={styles.manageAdventurerLink}
                    >
                        Manage Adventurer
                    </Link>
                </div>
            )}

            <div className={styles.dashboardContent}>
                <p>Manage your quests and track your progress here.</p>
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
