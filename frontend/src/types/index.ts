export interface Recruit {
    id: number;
    title: string;
    company: string;
    startDate: string;
    deadline: string;
    tags: string[];
    content?: string; // 상세 내용 (Optional)
}

export interface Portfolio {
    id: number;
    title: string;
    type: 'link' | 'file' | 'github';
    url?: string;
    fileName?: string;
    createdAt: string;
    description?: string;
    content?: string;
}

export interface CoverLetter {
    id: number;
    title: string;
    content: string;
    recruitId?: number;
    recruitTitle?: string;
    recruitCompany?: string;
    recruitDeadline?: string;
    updatedAt: string;
}

export interface User {
    id: number;
    email: string;
    name: string;
}
