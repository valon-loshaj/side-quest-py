import React, { ReactNode } from 'react';
import styles from '../styles/layout.module.css';

interface MainContentProps {
    children: ReactNode;
}

const MainContent: React.FC<MainContentProps> = ({ children }) => {
    return <main className={styles.main}>{children}</main>;
};

export default MainContent;
