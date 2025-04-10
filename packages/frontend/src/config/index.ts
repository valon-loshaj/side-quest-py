interface EnvironmentConfig {
    apiUrl: string;
    environment: 'development' | 'test' | 'production';
    apiVersion: string;
}

const ENV = import.meta.env.VITE_APP_ENV || 'development';
const configs: Record<string, EnvironmentConfig> = {
    development: {
        apiUrl: 'http://127.0.0.1:5000/api/v1',
        environment: 'development',
        apiVersion: 'v1',
    },
    test: {
        apiUrl: 'https://test-api.side-quest.example.com',
        environment: 'test',
        apiVersion: 'v1',
    },
    production: {
        apiUrl: 'https://api.side-quest.example.com',
        environment: 'production',
        apiVersion: 'v1',
    },
};

export const config = configs[ENV] || configs.development;

export const API_BASE_URL = `${config.apiUrl}/api/${config.apiVersion}`;
