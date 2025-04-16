import React, { ReactNode } from 'react';
import styles from '../styles/layout.module.css';
import Header from './Header';
import Footer from './Footer';
import LeftSidebar from './LeftSidebar';
import MainContent from './MainContent';

interface LayoutProps {
    children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className={styles.container}>
            <Header />
            <LeftSidebar />
            <MainContent>{children}</MainContent>
            <Footer />
        </div>
    );
};

export default Layout;
