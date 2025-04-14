import { User } from './models';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface UserRegistrationRequest {
    username: string;
    email: string;
    password: string;
    [key: string]: unknown;
}

interface UserRegistrationResponse {
    user: User;
    auth_token?: string;
    message?: string;
}

interface UserLoginRequest {
    username: string;
    password: string;
    [key: string]: unknown;
}

interface UserLoginResponse {
    user: User;
    auth_token: string;
    message?: string;
}

interface ApiResponse<T = unknown> {
    data: T;
    status: number;
    headers: Headers;
    timestamp: number;
}

interface APIError {
    message: string;
    code: string;
}

interface RequestOptions {
    method: HttpMethod;
    headers?: Record<string, string>;
    body?: Record<string, unknown> | FormData;
    params?: Record<string, string | number | boolean | undefined>;
    timeout?: number;
    withAuth?: boolean;
    contentType?: 'json' | 'multipart' | 'text';
}

export interface UserUpdateRequest {
    username?: string;
    email?: string;
    password?: string;
}

export type {
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserLoginRequest,
    UserLoginResponse,
    APIError,
    RequestOptions,
    ApiResponse,
};
