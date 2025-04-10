import React, { ReactNode } from 'react';
import styles from '../styles/layout.module.css';
import Header from './Header';
import Footer from './Footer';
import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';

interface LayoutProps {
    children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className={styles.container}>
            <Header />
            <LeftSidebar />
            <main className={styles.main}>{children}</main>
            <RightSidebar />
            <Footer />
        </div>
    );
};

export default Layout;
