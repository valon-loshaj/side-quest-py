import React from 'react';
import CurrentUser from '../components/CurrentUser';
import AdventurerSelect from '../components/AdventurerSelect';
import styles from '../styles/layout.module.css';
import { useAppSelector } from '../store';

const LeftSidebar: React.FC = () => {
    const { user } = useAppSelector(state => state.auth);

    return (
        <aside className={styles.leftSidebar}>
            <h1 className={styles.sidebarHeader}></h1>
            <CurrentUser />
            <div className={styles.adventurerContainer}>
                {user && <AdventurerSelect />}
            </div>
        </aside>
    );
};

export default LeftSidebar;
