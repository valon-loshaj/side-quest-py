import React from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import styles from '../styles/Dashboard.module.css';
import { logout } from '../store/slices/authSlice';

const Dashboard: React.FC = () => {
    const { user } = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch();
    if (!user) return null;

    const handleLogout = () => {
        dispatch(logout());
    };

    return (
        <div className={styles.dashboard}>
            <h1>Dashboard</h1>
            <div className={styles.welcomeMessage}>Welcome, {user.username}!</div>
            <div className={styles.dashboardContent}>
                {/* TODO: Dashboard content will go here */}
                <p>Manage your quests and adventurers here.</p>
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
