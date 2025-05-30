import React from 'react';
import { Quest } from '../types/models';
import styles from '../styles/components/QuestCard.module.css';

interface QuestCardProps {
    quest: Quest;
    isCurrent?: boolean;
    isUpdating?: boolean;
    onToggleCompletion: (questId: string) => void;
    onEdit: (questId: string, field: 'title' | 'experienceReward') => void;
    onSaveEdit: () => void;
    onInputChange: (value: string) => void;
    onInputBlur: () => void;
    onInputKeyDown: (e: React.KeyboardEvent) => void;
    onSetCurrent?: (questId: string) => void;
    onMoveUp?: (index: number) => void;
    onMoveDown?: (index: number) => void;
    onDelete: (questId: string) => void;
    index?: number;
    isLast?: boolean;
    editingQuest: { id: string | null; field: 'title' | 'experienceReward' | null };
    editValue: string;
}

const QuestCard: React.FC<QuestCardProps> = ({
    quest,
    isCurrent = false,
    isUpdating = false,
    onToggleCompletion,
    onEdit,
    onSaveEdit,
    onInputChange,
    onInputBlur,
    onInputKeyDown,
    onSetCurrent,
    onMoveUp,
    onMoveDown,
    onDelete,
    index,
    isLast,
    editingQuest,
    editValue,
}) => {
    const isEditing = editingQuest.id === quest.id;

    const cardStyleClass = `${isCurrent ? styles.currentQuestCard : styles.questCard} ${isUpdating ? styles.updating : ''}`;

    return (
        <div className={cardStyleClass}>
            <div className={styles.questCardHeader}>
                <div
                    className={`${styles.completionIndicator} ${
                        quest.completed ? styles.completed : ''
                    } ${isUpdating ? styles.updating : ''}`}
                    onClick={() => onToggleCompletion(quest.id)}
                >
                    {isUpdating && <span className={styles.loadingSpinner}></span>}
                </div>
                <div className={styles.questInfo}>
                    {isEditing && editingQuest.field === 'title' ? (
                        <div className={styles.inputGroup}>
                            <input
                                type="text"
                                value={editValue}
                                onChange={e => onInputChange(e.target.value)}
                                onBlur={onInputBlur}
                                onKeyDown={onInputKeyDown}
                                autoFocus
                            />
                            <button
                                className={styles.saveButton}
                                onClick={onSaveEdit}
                                title="Save changes"
                            >
                                ✓
                            </button>
                        </div>
                    ) : (
                        <h3 onClick={() => onEdit(quest.id, 'title')}>{quest.title}</h3>
                    )}

                    {isEditing && editingQuest.field === 'experienceReward' ? (
                        <div className={styles.inputGroup}>
                            <input
                                type="number"
                                className={styles.xpInput}
                                value={editValue}
                                onChange={e => onInputChange(e.target.value)}
                                onBlur={onInputBlur}
                                onKeyDown={onInputKeyDown}
                                autoFocus
                                min="1"
                            />
                            <button
                                className={styles.saveButton}
                                onClick={onSaveEdit}
                                title="Save changes"
                            >
                                ✓
                            </button>
                        </div>
                    ) : (
                        <p onClick={() => onEdit(quest.id, 'experienceReward')}>
                            XP: {quest.experience_reward}
                        </p>
                    )}
                </div>
            </div>

            {/* Only show these action buttons if it's not the current quest */}
            {!isCurrent && onSetCurrent && (
                <div className={styles.questCardFooter}>
                    <div className={styles.questActions}>
                        <button
                            className={styles.markCurrentButton}
                            onClick={() => onSetCurrent(quest.id)}
                            title="Mark as current quest"
                            disabled={isUpdating}
                        >
                            ★
                        </button>
                        {index !== undefined && onMoveUp && (
                            <button
                                className={`${styles.moveButton} ${index === 0 ? styles.disabled : ''}`}
                                onClick={() => onMoveUp(index)}
                                disabled={index === 0 || isUpdating}
                                title="Move up"
                            >
                                ▲
                            </button>
                        )}
                        {index !== undefined && onMoveDown && isLast !== undefined && (
                            <button
                                className={`${styles.moveButton} ${isLast ? styles.disabled : ''}`}
                                onClick={() => onMoveDown(index)}
                                disabled={isLast || isUpdating}
                                title="Move down"
                            >
                                ▼
                            </button>
                        )}
                        <button
                            className={styles.deleteButton}
                            onClick={() => onDelete(quest.id)}
                            title="Delete quest"
                            disabled={isUpdating}
                        >
                            🗑️
                        </button>
                    </div>
                </div>
            )}

            {/* For current quest, we only show the delete button */}
            {isCurrent && (
                <div className={styles.questCardFooter}>
                    <div className={styles.questActions}>
                        <button
                            className={styles.deleteButton}
                            onClick={() => onDelete(quest.id)}
                            title="Delete quest"
                        >
                            🗑️
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default QuestCard;
