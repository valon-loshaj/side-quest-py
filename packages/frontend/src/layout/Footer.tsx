import React from 'react';
import styles from '../styles/layout.module.css';

const Footer: React.FC = () => {
    return (
        <footer className={styles.footer}>
            <p>Side Quest &copy; {new Date().getFullYear()}</p>
        </footer>
    );
};

export default Footer;
