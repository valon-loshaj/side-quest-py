import React from 'react';
import styles from '../styles/layout.module.css';

const RightSidebar: React.FC = () => {
    return (
        <aside className={styles.rightSidebar}>
            <h2>Right Sidebar</h2>
            <p>Additional info, stats, and side content will go here</p>
        </aside>
    );
};

export default RightSidebar;
