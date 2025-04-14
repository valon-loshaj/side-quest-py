import React from 'react';
import CurrentUser from '../components/CurrentUser';
import styles from '../styles/layout.module.css';

const LeftSidebar: React.FC = () => {
    return (
        <aside className={styles.leftSidebar}>
            <h2>Left Sidebar</h2>
            <p>Navigation and main menus will go here</p>
            <CurrentUser />
        </aside>
    );
};

export default LeftSidebar;
