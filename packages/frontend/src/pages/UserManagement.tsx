import React, { useState, FormEvent } from 'react';
import { useAuth } from '../store/hooks/useAuth';
import styles from '../styles/pages/UserManagement.module.css';

const UserManagement: React.FC = () => {
    const { user, updateUserProfile, loading } = useAuth();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [showError, setShowError] = useState('');

    if (!user) {
        return <div>Loading user data...</div>;
    }

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setSuccessMessage('');
        setShowError('');

        // Basic validation
        if (password && password !== confirmPassword) {
            setShowError('Passwords do not match');
            return;
        }

        // Create update object with only the fields that have changed
        const updateData: {
            username?: string;
            email?: string;
            password?: string;
        } = {};

        if (username && username !== user.username) {
            updateData.username = username;
        }

        if (email && email !== user.email) {
            updateData.email = email;
        }

        if (password) {
            updateData.password = password;
        }

        // Only proceed if there's something to update
        if (Object.keys(updateData).length === 0) {
            setShowError('No changes detected');
            return;
        }

        try {
            const result = await updateUserProfile(user.id, updateData);

            if (result.meta.requestStatus === 'fulfilled') {
                setSuccessMessage('Profile updated successfully');
                // Clear password fields after successful update
                setPassword('');
                setConfirmPassword('');
            }
        } catch (error) {
            setShowError('Failed to update profile');
            console.error(error);
        }
    };

    return (
        <div className={styles.userManagement}>
            <h1>User Management</h1>

            {/* Current user info */}
            <div className={styles.userInfo}>
                <h2>Current Information</h2>
                <div className={styles.infoRow}>
                    <span className={styles.label}>Username:</span>
                    <span className={styles.value}>{user.username}</span>
                </div>
                <div className={styles.infoRow}>
                    <span className={styles.label}>Email:</span>
                    <span className={styles.value}>{user.email}</span>
                </div>
            </div>

            {/* Update form */}
            <div className={styles.updateForm}>
                <h2>Update Profile</h2>

                {successMessage && (
                    <div className={styles.successMessage}>{successMessage}</div>
                )}

                {showError && <div className={styles.errorMessage}>{showError}</div>}

                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username">New Username</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            placeholder={user.username}
                            className={styles.input}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="email">New Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            placeholder={user.email}
                            className={styles.input}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password">New Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            placeholder="Leave blank to keep current password"
                            className={styles.input}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="confirmPassword">Confirm New Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={e => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your new password"
                            className={styles.input}
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Updating...' : 'Update Profile'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default UserManagement;
