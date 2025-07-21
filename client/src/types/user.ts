
export type UserModel = {
    userId: string;
    username: string;
    email: string;
    created: Date;
    updated: Date;
    imageKey: string | null;
    fullName: string | null;
    profilePictureUrl: string | null;
    giteaUserId: number | null;
    giteaTokenEncrypted: string | null;
    apiKey: string | null;
};

export type CreateUserRequest = {
    userId: string;
    username: string;
    email: string;
    imageKey: string | null;
    fullName: string | null;
    profilePictureUrl: string | null;
};

export type UpdateUserRequest = {
    userId: string;
    username: string | null;
    email: string | null;
    imageKey: string | null;
    fullName: string | null;
    profilePictureUrl: string | null;
};

export type DeleteUserRequest = {
    userId: string;
};

export type PublicUser = {
    userId: string;
    username: string;
    email: string;
    created: Date;
    updated: Date;
    imageKey: string | null;
    fullName: string | null;
    profilePictureUrl: string | null;
};

export type GetUserRequest = {
    userId: string;
    authorized: boolean;
};

    