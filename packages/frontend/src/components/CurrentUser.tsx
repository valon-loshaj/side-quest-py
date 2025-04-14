import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../store/hooks/useAuth';
import styles from '../styles/components/CurrentUser.module.css';

const CurrentUser: React.FC = () => {
    const { user } = useAuth();

    if (!user) {
        return null;
    }

    return (
        <div>
            <h2>Current User</h2>
            <div className={styles.currentUser}>
                <div className={styles.profilePicture}>
                    {/* Placeholder for profile picture, using the first letter of username */}
                    <div className={styles.avatarPlaceholder}>
                        {user.username.charAt(0).toUpperCase()}
                    </div>
                </div>
                <div className={styles.userInfo}>
                    <span className={styles.username}>{user.username}</span>
                    <Link to="/user-management" className={styles.manageLink}>
                        Manage
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default CurrentUser;
