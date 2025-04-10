import { User } from './models';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface UserRegistrationRequest {
    username: string;
    email: string;
    password: string;
}

interface UserRegistrationResponse {
    user: User;
    token: string;
}

interface UserLoginRequest {
    email: string;
    password: string;
}

interface UserLoginResponse {
    user: User;
    token: string;
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

export type {
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserLoginRequest,
    UserLoginResponse,
    APIError,
    RequestOptions,
    ApiResponse,
};
