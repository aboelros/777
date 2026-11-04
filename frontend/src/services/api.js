import * as auth from './api/auth';
import * as projects from './api/projects';
import * as orders from './api/orders';
import * as messages from './api/messages';
import * as reports from './api/reports';
import * as integrations from './api/integrations';
import * as assistant from './api/assistant';
import * as subscriptions from './api/subscriptions';
import * as botTraining from './api/botTraining';
import * as socialMedia from './api/socialMedia';
import * as deals from './api/deals';
import * as dripCampaigns from './api/dripCampaigns';
import * as payments from './api/payments';
import * as products from './api/products';
import * as knowledge from './api/knowledge';
import { financeApi as finance } from '@/features/finance/api/financeApi';
import { apiRequest, API_BASE_URL, getAuthToken } from './api/core';

export {
    auth, projects, orders, messages, reports, integrations,
    assistant, subscriptions, botTraining, socialMedia, deals,
    dripCampaigns, payments, products, knowledge, finance,
    apiRequest, API_BASE_URL, getAuthToken
};

export default {
    auth: auth.auth,
    projects: projects.projects,
    orders: orders.orders,
    messages: messages.messages,
    reports: reports.reports,
    integrations: integrations.integrations,
    assistant: assistant.assistant,
    subscriptions: subscriptions.subscriptions,
    botTraining: botTraining.botTraining,
    socialMedia: socialMedia.socialMedia,
    deals: deals.deals,
    dripCampaigns: dripCampaigns.dripCampaigns,
    payments: payments.payments,
    products: products.products,
    knowledge: knowledge.knowledge,
    finance,
    apiRequest,
    API_BASE_URL,
    getAuthToken
};
