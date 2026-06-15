import { lazy } from 'react';

// Lazy load heavy components
export const Dashboard = lazy(() => import('./pages/Dashboard'));
export const Messages = lazy(() => import('./pages/Messages'));
export const Reports = lazy(() => import('./pages/Reports'));
export const Products = lazy(() => import('./pages/Products'));
export const Orders = lazy(() => import('./pages/Orders'));
export const Deals = lazy(() => import('./pages/Deals'));
export const Integrations = lazy(() => import('./pages/Integrations'));
export const BotTraining = lazy(() => import('./pages/BotTraining'));
export const AIGovernance = lazy(() => import('./pages/AIGovernance'));
export const Settings = lazy(() => import('./pages/Settings'));
export const Projects = lazy(() => import('./pages/Projects'));
export const Assistant = lazy(() => import('./pages/Assistant'));
export const SocialMedia = lazy(() => import('./pages/SocialMedia'));
export const DripCampaigns = lazy(() => import('./pages/DripCampaigns'));
export const Payments = lazy(() => import('./pages/Payments'));
export const Subscription = lazy(() => import('./pages/Subscription'));
export const UsageDashboard = lazy(() => import('./pages/UsageDashboard'));
export const About = lazy(() => import('./pages/About'));
