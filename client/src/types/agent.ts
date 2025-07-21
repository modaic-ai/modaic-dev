export type Agent = {
    agentId: string;
    repoId: string;
    name: string;
    description: string;
    adminId: string;
    configYaml: Record<string, any>;
    readmeContent: string;
    tags: string[];
    version: string;
    lastMirrored: Date;
    created: Date;
    updated: Date;
};

export type CreateAgentRequest = {
    name: string;
    description: string;
    repoId: string;
    adminId: string;
    configYaml?: Record<string, any>;
    tags?: string[];
};

export type UpdateAgentRequest = {
    agentId: string;
    name?: string;
    description?: string;
    configYaml?: Record<string, any>;
    readmeContent?: string;
    tags?: string[];
    version?: string;
};

export type PublicAgent = {
    agentId: string;
    name: string;
    description: string;
    adminId: string;
    configYaml: Record<string, any>;
    readmeContent: string;
    tags: string[];
    version: string;
    created: Date;
    updated: Date;
    lastMirrored: Date;
};