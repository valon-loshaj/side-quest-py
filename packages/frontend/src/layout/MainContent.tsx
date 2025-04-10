import React, { ReactNode } from 'react';
import styles from '../styles/layout.module.css';

interface MainContentProps {
    children: ReactNode;
}

const MainContent: React.FC<MainContentProps> = ({ children }) => {
    return <div className={styles.main}>{children}</div>;
};

export default MainContent;
