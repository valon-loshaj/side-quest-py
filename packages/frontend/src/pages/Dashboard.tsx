import React from 'react';
import { useAppSelector } from '../store';
import styles from '../styles/Dashboard.module.css';

const Dashboard: React.FC = () => {
    const { user } = useAppSelector(state => state.auth);

    if (!user) return null;

    return (
        <div className={styles.dashboard}>
            <h1>Dashboard</h1>
            <div className={styles.welcomeMessage}>Welcome, {user.username}!</div>
            <div className={styles.dashboardContent}>
                {/* TODO: Dashboard content will go here */}
                <p>Manage your quests and adventurers here.</p>
            </div>
        </div>
    );
};

export default Dashboard;
