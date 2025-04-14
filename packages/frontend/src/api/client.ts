import { config } from '../config';
import { APIError, ApiResponse, RequestOptions } from '../types/api';
import * as tokenService from '../services/token-service';

const DEFAULT_OPTIONS: Partial<RequestOptions> = {
    timeout: 30000, // 30 seconds
    withAuth: true,
    contentType: 'json',
};

const requestCache = new Map<
    string,
    {
        data: unknown;
        timestamp: number;
        expiry: number;
    }
>();

const DEFAULT_CACHE_EXPIRY = 5 * 60 * 1000;

export class ApiClient {
    private baseUrl: string;
    private defaultHeaders: Record<string, string>;
    private tokenProvider: () => string | null;
    private cacheEnabled: boolean;

    constructor(
        baseUrl = config.apiUrl,
        tokenProvider = tokenService.getToken,
        defaultHeaders: Record<string, string> = {},
        cacheEnabled = true
    ) {
        this.baseUrl = baseUrl;
        this.tokenProvider = tokenProvider;
        this.defaultHeaders = {
            Accept: 'application/json',
            ...defaultHeaders,
        };
        this.cacheEnabled = cacheEnabled;
    }

    private getAuthHeaders(): Record<string, string> {
        const token = this.tokenProvider();
        if (!token) {
            console.warn('No auth token found when attempting to create auth headers');
            return {};
        }

        // Log token when in development mode
        if (import.meta.env.MODE !== 'production') {
            // Only log token length and a small prefix for security
            const tokenLength = token.length;
            const tokenPrefix = token.substring(0, 10);
            console.log(
                `Including auth token in request: ${tokenPrefix}... (${tokenLength} chars)`
            );

            // Validate token format (should be a JWT with 3 parts)
            const parts = token.split('.');
            if (parts.length !== 3) {
                console.error(
                    'Warning: Token does not appear to be in valid JWT format (expected 3 parts separated by dots)'
                );
            } else {
                console.log('Token appears to be in valid JWT format');
            }
        }

        return { Authorization: `Bearer ${token}` };
    }

    private buildUrl(
        endpoint: string,
        params?: Record<string, string | number | boolean | undefined>
    ): string {
        // If baseUrl is empty, use relative URL
        let url: URL;
        if (this.baseUrl) {
            url = new URL(
                `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
            );
        } else {
            // Use relative URL with the current origin for the proxy
            url = new URL(
                `${window.location.origin}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
            );
        }

        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    url.searchParams.append(key, String(value));
                }
            });
        }

        // For relative URLs with proxy, return path + query string only
        if (!this.baseUrl) {
            return `${url.pathname}${url.search}`;
        }

        return url.toString();
    }

    private getCacheKey(url: string, options: RequestOptions): string {
        return `${options.method}:${url}:${JSON.stringify(options.headers)}`;
    }

    private getFromCache(cacheKey: string): unknown | null {
        if (!this.cacheEnabled) return null;

        const cached = requestCache.get(cacheKey);
        if (!cached) return null;

        const now = Date.now();
        if (now > cached.expiry) {
            requestCache.delete(cacheKey);
            return null;
        }

        return cached.data;
    }

    private addToCache(
        cacheKey: string,
        data: unknown,
        expiry = DEFAULT_CACHE_EXPIRY
    ): void {
        if (!this.cacheEnabled) return;

        requestCache.set(cacheKey, {
            data,
            timestamp: Date.now(),
            expiry: Date.now() + expiry,
        });
    }

    private prepareHeaders(options: RequestOptions): Record<string, string> {
        const headers: Record<string, string> = {
            ...this.defaultHeaders,
            ...options.headers,
        };

        if (options.withAuth) {
            Object.assign(headers, this.getAuthHeaders());
        }

        // Set content type header based on the request type
        if (options.body && options.contentType !== 'multipart') {
            headers['Content-Type'] =
                options.contentType === 'text' ? 'text/plain' : 'application/json';
        }

        return headers;
    }

    private prepareBody(options: RequestOptions): BodyInit | undefined {
        if (!options.body) return undefined;

        if (options.body instanceof FormData) {
            return options.body;
        }

        if (options.contentType === 'text') {
            return String(options.body);
        }

        return JSON.stringify(options.body);
    }

    private createTimeoutPromise(ms: number): Promise<Response> {
        return new Promise((_, reject) => {
            setTimeout(() => {
                reject(new Error(`Request timed out after ${ms}ms`));
            }, ms);
        });
    }

    private async processResponse(response: Response): Promise<unknown> {
        const contentType = response.headers.get('content-type');

        if (contentType?.includes('application/json')) {
            return await response.json();
        }

        if (contentType?.includes('text/')) {
            return await response.text();
        }

        if (contentType?.includes('application/octet-stream')) {
            return await response.blob();
        }

        return await response.text();
    }

    private async handleErrorResponse(response: Response): Promise<never> {
        let errorData: Record<string, unknown> = {};

        try {
            errorData = (await this.processResponse(response)) as Record<
                string,
                unknown
            >;
        } catch {
            errorData = { message: 'Unknown error occurred', code: 'UNKNOWN_ERROR' };
        }

        console.error('API Error:', {
            status: response.status,
            url: response.url,
            errorData,
        });

        const apiError: APIError = {
            message:
                (errorData.message as string) ||
                `Request failed with status ${response.status}`,
            code: (errorData.code as string) || `HTTP_ERROR_${response.status}`,
        };

        throw apiError;
    }

    public async request<T = unknown>(
        endpoint: string,
        options: RequestOptions
    ): Promise<ApiResponse<T>> {
        const mergedOptions: RequestOptions = { ...DEFAULT_OPTIONS, ...options };
        const url = this.buildUrl(endpoint, mergedOptions.params);
        const headers = this.prepareHeaders(mergedOptions);
        const body = this.prepareBody(mergedOptions);

        // Log the request details in development
        if (import.meta.env.MODE !== 'production') {
            // Enhanced logging for authentication debugging
            const authHeader = headers['Authorization'];
            console.log('API Request:', {
                url,
                method: mergedOptions.method,
                withAuth: mergedOptions.withAuth,
                hasAuthHeader: !!authHeader,
                authHeaderValue: authHeader
                    ? `${authHeader.substring(0, 15)}...`
                    : 'none',
                headers: { ...headers },
                body: mergedOptions.body ? { ...mergedOptions.body } : null,
            });
        }

        const cacheKey = this.getCacheKey(url, mergedOptions);
        if (mergedOptions.method === 'GET') {
            const cachedData = this.getFromCache(cacheKey);
            if (cachedData) {
                return cachedData as ApiResponse<T>;
            }
        }

        try {
            const fetchPromise = fetch(url, {
                method: mergedOptions.method,
                headers,
                body,
                credentials: 'include',
                mode: 'cors',
            });

            const response = await Promise.race([
                fetchPromise,
                this.createTimeoutPromise(
                    mergedOptions.timeout || DEFAULT_OPTIONS.timeout!
                ),
            ]);

            if (!response.ok) {
                await this.handleErrorResponse(response);
            }

            const data = await this.processResponse(response);

            const apiResponse: ApiResponse<T> = {
                data: data as T,
                status: response.status,
                headers: response.headers,
                timestamp: Date.now(),
            };

            if (mergedOptions.method === 'GET') {
                this.addToCache(cacheKey, apiResponse);
            }

            return apiResponse;
        } catch (error) {
            console.error('API Client Error:', {
                url,
                method: mergedOptions.method,
                error:
                    error instanceof Error
                        ? {
                              message: error.message,
                              stack: error.stack,
                              name: error.name,
                          }
                        : error,
            });

            if (error instanceof Error) {
                if (!(error as Error & { code?: string }).code) {
                    const apiError: APIError = {
                        message: error.message || 'Unknown error occurred',
                        code: 'CLIENT_ERROR',
                    };
                    throw apiError;
                }
            }
            throw error;
        }
    }

    public async get<T = unknown>(
        endpoint: string,
        options: Omit<RequestOptions, 'method'> = {}
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { ...options, method: 'GET' });
    }

    public async post<T = unknown, B = Record<string, unknown>>(
        endpoint: string,
        body?: B,
        options: Omit<RequestOptions, 'method' | 'body'> = {}
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: body as Record<string, unknown>,
        });
    }

    public async put<T = unknown, B = Record<string, unknown>>(
        endpoint: string,
        body?: B,
        options: Omit<RequestOptions, 'method' | 'body'> = {}
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'PUT',
            body: body as Record<string, unknown>,
        });
    }

    public async patch<T = unknown, B = Record<string, unknown>>(
        endpoint: string,
        body?: B,
        options: Omit<RequestOptions, 'method' | 'body'> = {}
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'PATCH',
            body: body as Record<string, unknown>,
        });
    }

    public async delete<T = unknown>(
        endpoint: string,
        options: Omit<RequestOptions, 'method'> = {}
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { ...options, method: 'DELETE' });
    }

    public clearCache(pattern?: RegExp): void {
        if (!pattern) {
            requestCache.clear();
            return;
        }

        for (const key of requestCache.keys()) {
            if (pattern.test(key)) {
                requestCache.delete(key);
            }
        }
    }

    public async uploadFile<T = unknown>(
        endpoint: string,
        file: File,
        onProgress?: (progress: number) => void,
        options: Omit<RequestOptions, 'method' | 'body' | 'contentType'> = {}
    ): Promise<ApiResponse<T>> {
        const formData = new FormData();
        formData.append('file', file);

        if (onProgress) {
            const xhr = new XMLHttpRequest();

            return new Promise((resolve, reject) => {
                xhr.open('POST', this.buildUrl(endpoint, options.params));

                // Add headers
                const headers = this.prepareHeaders({
                    ...options,
                    method: 'POST',
                    contentType: 'multipart',
                });

                Object.entries(headers).forEach(([key, value]) => {
                    xhr.setRequestHeader(key, value);
                });

                xhr.upload.onprogress = event => {
                    if (event.lengthComputable) {
                        const progress = Math.round((event.loaded / event.total) * 100);
                        onProgress(progress);
                    }
                };

                xhr.onload = async () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        let data;
                        try {
                            data = JSON.parse(xhr.responseText);
                        } catch {
                            data = xhr.responseText;
                        }

                        resolve({
                            data,
                            status: xhr.status,
                            headers: new Headers(
                                xhr
                                    .getAllResponseHeaders()
                                    .split('\r\n')
                                    .reduce((obj: Record<string, string>, line) => {
                                        const parts = line.split(': ');
                                        if (parts[0] && parts[1]) {
                                            obj[parts[0]] = parts[1];
                                        }
                                        return obj;
                                    }, {})
                            ),
                            timestamp: Date.now(),
                        });
                    } else {
                        try {
                            const errorData = JSON.parse(xhr.responseText);
                            reject({
                                message:
                                    errorData.message ||
                                    `Upload failed with status ${xhr.status}`,
                                code: errorData.code || `HTTP_ERROR_${xhr.status}`,
                            });
                        } catch {
                            reject({
                                message: `Upload failed with status ${xhr.status}`,
                                code: `HTTP_ERROR_${xhr.status}`,
                            });
                        }
                    }
                };

                xhr.onerror = () => {
                    reject({
                        message: 'Network error during upload',
                        code: 'NETWORK_ERROR',
                    });
                };

                xhr.ontimeout = () => {
                    reject({
                        message: `Upload timed out after ${options.timeout || DEFAULT_OPTIONS.timeout}ms`,
                        code: 'TIMEOUT_ERROR',
                    });
                };

                xhr.timeout = options.timeout || DEFAULT_OPTIONS.timeout!;

                xhr.send(formData);
            });
        }

        // Fallback to regular upload without progress
        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: formData as FormData,
            contentType: 'multipart',
        });
    }

    public async downloadFile(
        endpoint: string,
        filename: string,
        options: Omit<RequestOptions, 'method'> = {}
    ): Promise<void> {
        const url = this.buildUrl(endpoint, options.params);
        const headers = this.prepareHeaders({ ...options, method: 'GET' });

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers,
                credentials: 'include',
            });

            if (!response.ok) {
                await this.handleErrorResponse(response);
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
        } catch (error) {
            if (error instanceof Error) {
                if (!(error as Error & { code?: string }).code) {
                    const apiError: APIError = {
                        message: error.message || 'File download failed',
                        code: 'DOWNLOAD_ERROR',
                    };
                    throw apiError;
                }
            }
            throw error;
        }
    }
}

const apiClient = new ApiClient(config.apiUrl, tokenService.getToken);
export default apiClient;
