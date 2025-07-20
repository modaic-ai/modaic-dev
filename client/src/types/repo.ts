
export type Repo = {
    repoId: string;
    name: string;
    description: string;
    adminId: string;
    created: Date;
    updated: Date;
    visibility: "private" | "public";
    stars: number;
    forks: number;
    imageKeys: string[];
    forkedFrom: string | null;
}

export type CreateRepoRequest = {
    name: string;
    description: string;
    visibility: "private" | "public";
    adminId: string;
}

export type UpdateRepoRequest = {
    repoId: string;
    name?: string;
    description?: string;
    visibility?: "private" | "public";
    adminId?: string;
    stars?: number;
    forks?: number;
    imageKeys?: string[];
    forkedFrom?: string | null;
}

export type PublicRepo = {
    name: string;
    description: string;
    visibility: "private" | "public";
    adminId: string;
    created: Date;
    updated: Date;
    stars: number;
    forks: number;
    imageKeys: string[];
    forkedFrom: string | null;
}

export type DeleteRepoRequest = {
    repoId: string;
}

export type GetRepoRequest = {
    repoId: string;
    authorized: boolean;
}

