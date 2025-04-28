interface User {
    id: string;
    username: string;
    email: string;
    passwordHash: string;
    authToken: string;
    tokenExpiration: string;
    createdAt: string;
    updatedAt: string;
    adventurers?: Adventure[];
}

interface Adventure {
    id: string;
    name: string;
    level: number;
    experience: number;
    experience_for_next_level: number;
    progress_percentage: number;
    completed_quests_count: number;
    completed_quests: string[];
    adventurer_type?: string;
}

interface Quest {
    id: string;
    title: string;
    experience_reward: number;
    completed: boolean;
    created_at: string;
    updated_at: string;
    adventurer_id: string;
}

interface QuestCompletion {
    id: string;
    questId: string;
    adventureId: string;
    createdAt: string;
    updatedAt: string;
}

export type { User, Adventure, Quest, QuestCompletion };
