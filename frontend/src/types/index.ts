export interface User {
    id: number;
    email: string;
    name: string;
}

export interface Recruit {
    id: number;
    title: string;
    company: string;
    deadline: string;
    tags: string[];
}

export interface Portfolio {
    id: number;
    title: string;
    type: 'link' | 'file' | 'text';
    content?: string;
    url?: string;
    createdAt: string;
}

export interface CoverLetter {
    id: number;
    title: string;
    content: string;
    recruitId?: number;
    updatedAt: string;
}
