import { NavigateFunction } from 'react-router-dom';
import { ROUTES, RouteNames } from '../types/routes';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export const scrollToNextPage = (
    navigate: NavigateFunction,
    isAuthenticated: boolean
) => {
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    gsap.killTweensOf('*');

    const targetRoute = isAuthenticated
        ? ROUTES[RouteNames.DASHBOARD].path
        : ROUTES[RouteNames.LOGIN].path;

    setTimeout(() => {
        navigate(targetRoute);
    }, 100);
};
