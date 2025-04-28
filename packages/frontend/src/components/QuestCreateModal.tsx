import React, { useState } from 'react';
import { Modal, Button, Form, Input, InputNumber, Typography } from 'antd';
import { CloseOutlined } from '@ant-design/icons';
import { Quest } from '../types/models';
import styles from '../styles/components/QuestCreateModal.module.css';

interface QuestCreateModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (quest: Partial<Quest>) => void;
    adventurerId: string;
}

const QuestCreateModal: React.FC<QuestCreateModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    adventurerId,
}) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        try {
            setLoading(true);
            const values = await form.validateFields();
            const newQuest: Partial<Quest> = {
                title: values.title,
                experience_reward: values.experienceReward,
                adventurer_id: adventurerId,
            };

            onSubmit(newQuest);
            form.resetFields();
        } catch (error) {
            console.error('Error creating quest:', error);
        } finally {
            setLoading(false);
            onClose();
        }
    };

    return (
        <Modal
            title={
                <Typography.Title level={4} className={styles['modal-title']}>
                    Create New Quest
                </Typography.Title>
            }
            open={isOpen}
            onCancel={onClose}
            className={styles.modal}
            closeIcon={<CloseOutlined className={styles['modal-close']} />}
            footer={null}
        >
            <Form form={form} layout="vertical" className={styles['modal-form']}>
                <Form.Item
                    label="Title"
                    name="title"
                    className={styles['modal-form-item']}
                    rules={[{ required: true, message: 'Title is required' }]}
                >
                    <Input
                        className={styles['modal-form-item-input']}
                        placeholder="Enter quest title"
                    />
                </Form.Item>

                <Form.Item
                    label="Experience Reward"
                    name="experienceReward"
                    className={styles['modal-form-item']}
                    rules={[
                        { required: true, message: 'Experience reward is required' },
                    ]}
                >
                    <InputNumber
                        className={styles['modal-form-item-input-number']}
                        min={0}
                        placeholder="Enter XP reward amount"
                    />
                </Form.Item>

                <div className={styles['modal-form-buttons']}>
                    <Button onClick={onClose} className={styles['cancel-button']}>
                        Cancel
                    </Button>
                    <Button
                        type="primary"
                        loading={loading}
                        onClick={handleSubmit}
                        className={styles['create-button']}
                    >
                        Create Quest
                    </Button>
                </div>
            </Form>
        </Modal>
    );
};

export default QuestCreateModal;
