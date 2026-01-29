export interface Recruit {
    id: number;
    title: string;
    company: string;
    startDate?: string;
    deadline?: string;
    tags?: string[];
    content?: string;
    reason?: string;

    // New Detailed Fields
    link?: string;
    experience?: string;
    education?: string;
    employment_type?: string;
    salary?: string;
    job_sector?: string;
    key_responsibilities?: string;
    required_qualifications?: string;
    preferred_qualifications?: string;
    category?: string;
    location?: string;
    view_count?: number;
}

export interface PortfolioJobQuery {
    type: 'A' | 'B' | 'C';
    query_text: string;
    evidence: string[];
}

export interface Portfolio {
    id: number;
    project_name: string;
    type: 'link' | 'file' | 'github' | 'notion';
    url?: string;
    fileName?: string;
    createdAt: string;
    content?: string;

    // Status
    processingStatus?: 'PENDING' | 'COMPLETED' | 'FAILED';

    // Flattened Project Data
    period?: string;
    role?: string;
    description?: string;
    tech_stack?: string[];
    source_url?: string;
    job_queries?: PortfolioJobQuery[];
}

export interface CoverLetterItem {
    id: number;
    question: string;
    content: string;
    category?: string;
    key_points?: string[];
    suggested_improvements?: string[];
}

export interface CoverLetter {
    id: number;
    title: string;
    content?: string;
    recruitId?: number;
    recruitTitle?: string;
    recruitCompany?: string;
    recruitDeadline?: string;
    updatedAt: string;

    // AI Analysis
    status?: 'PENDING' | 'COMPLETED' | 'FAILED';
    gap_analysis?: any;
    items?: CoverLetterItem[];
}

export interface User {
    id: number;
    email: string;
    name: string;
    profileImage?: string;
    profile_summary?: string;
    desired_job_title?: string;
}
