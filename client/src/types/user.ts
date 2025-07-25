
export type PublicUser = {
    userId: string;
    username: string;
    created: string;
    profilePictureUrl?: string | null;
    fullName?: string | null;
    bio?: string | null;
    githubUrl?: string | null;
    linkedinUrl?: string | null;
    xUrl?: string | null;
    websiteUrl?: string | null;
}

export interface PrivateUser extends PublicUser {
    email: string;
    updated: string;
}

export type EntityType = PrivateUser | PublicUser;

export type CreateUserRequest = {
    userId: string;
    username: string;
    email: string;
    profilePictureUrl?: string | null;
    fullName?: string | null;
};

export type UpdateUserRequest = {
    fullName?: string | null;
    profilePictureUrl?: string | null;
    bio?: string | null;
    githubUrl?: string | null;
    linkedinUrl?: string | null;
    xUrl?: string | null;
    websiteUrl?: string | null;
};

export type DeleteUserRequest = {
    userId: string;
};
    