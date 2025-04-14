import React from 'react';
import CurrentUser from '../components/CurrentUser';
import AdventurerSelect from '../components/AdventurerSelect';
import styles from '../styles/layout.module.css';
import { useAppSelector } from '../store';

const LeftSidebar: React.FC = () => {
    const { user } = useAppSelector(state => state.auth);

    return (
        <aside className={styles.leftSidebar}>
            <CurrentUser />
            {user && <AdventurerSelect />}
        </aside>
    );
};

export default LeftSidebar;
