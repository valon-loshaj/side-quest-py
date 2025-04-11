export enum RouteNames {
    LOGIN = 'login',
    DASHBOARD = 'dashboard',
}

export interface RouteConfig {
    path: string;
    exact?: boolean;
    isProtected: boolean;
}

export type RoutesMap = {
    [key in RouteNames]: RouteConfig;
};

export const ROUTES: RoutesMap = {
    [RouteNames.LOGIN]: {
        path: '/login',
        exact: true,
        isProtected: false,
    },
    [RouteNames.DASHBOARD]: {
        path: '/dashboard',
        exact: true,
        isProtected: true,
    },
};
