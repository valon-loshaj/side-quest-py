interface User {
    id: string;
    username: string;
    email: string;
    passwordHash: string;
    authToken: string;
    tokenExpiration: string;
    createdAt: string;
    updatedAt: string;
}

interface Adventure {
    id: string;
    name: string;
    userId: string;
    level: number;
    experience: number;
    completedQuests: QuestCompletion[];
    leveledUp: boolean;
    createdAt: string;
    updatedAt: string;
}

interface Quest {
    id: string;
    title: string;
    experienceReward: number;
    completed: boolean;
    createdAt: string;
    updatedAt: string;
}

interface QuestCompletion {
    id: string;
    questId: string;
    adventureId: string;
    createdAt: string;
    updatedAt: string;
}

export type { User, Adventure, Quest, QuestCompletion };
