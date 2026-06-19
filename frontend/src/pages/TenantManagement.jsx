/**
 * Tenant Management Dashboard
 * Manage tenants, quotas, and billing.
 */
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Building2, Users, Package, DollarSign, Settings, TrendingUp } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function TenantManagement() {
    const [tenants, setTenants] = useState([]);
    const [selectedTenant, setSelectedTenant] = useState(null);

    const plans = [
        { name: 'Free', price: 0, users: 1, projects: 1, messages: '50', ai: '500', color: 'from-gray-500 to-gray-600' },
        { name: 'Starter', price: 29, users: 1, projects: 3, messages: '1K', ai: '10K', color: 'from-blue-500 to-cyan-600' },
        { name: 'Growth', price: 59, users: 2, projects: 5, messages: '5K', ai: '50K', color: 'from-green-500 to-emerald-600' },
        { name: 'Professional', price: 119, users: 3, projects: 10, messages: '10K', ai: '100K', color: 'from-sky-500 to-sky-600' },
        { name: 'Scale', price: 199, users: 4, projects: 15, messages: '25K', ai: '250K', color: 'from-orange-500 to-red-600' },
        { name: 'Business', price: 349, users: 10, projects: 30, messages: '100K', ai: '1M', color: 'from-indigo-500 to-blue-600' },
        { name: 'Enterprise', price: 799, users: 'Unlimited', projects: 'Unlimited', messages: 'Unlimited', ai: 'Unlimited', color: 'from-yellow-500 to-orange-600' }
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                    <Building2 className="w-10 h-10 text-sky-400" />
                    Tenant Management
                </h1>
                <p className="text-gray-400">Manage multi-tenant organizations and quotas</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Total Tenants</span>
                            <Building2 className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="text-3xl font-bold">24</div>
                        <div className="text-xs text-green-400 mt-1">+3 this month</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Total Users</span>
                            <Users className="w-5 h-5 text-sky-400" />
                        </div>
                        <div className="text-3xl font-bold">342</div>
                        <div className="text-xs text-gray-400 mt-1">Across all tenants</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">MRR</span>
                            <DollarSign className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="text-3xl font-bold">$4,250</div>
                        <div className="text-xs text-green-400 mt-1">+15% vs last month</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Avg Usage</span>
                            <TrendingUp className="w-5 h-5 text-yellow-400" />
                        </div>
                        <div className="text-3xl font-bold">67%</div>
                        <div className="text-xs text-gray-400 mt-1">Of quota limits</div>
                    </div>
                </GlassCard>
            </div>

            {/* Subscription Plans */}
            <div>
                <h2 className="text-xl font-bold mb-4">Subscription Plans</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {plans.map((plan, i) => (
                        <GlassCard key={i}>
                            <div className="p-6">
                                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${plan.color} flex items-center justify-center mb-4`}>
                                    <Package className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                                <div className="text-3xl font-bold mb-4">
                                    ${plan.price}<span className="text-sm text-gray-400">/mo</span>
                                </div>
                                <div className="space-y-2 text-sm text-gray-300">
                                    <div>• {plan.users} {typeof plan.users === 'number' ? 'user' + (plan.users > 1 ? 's' : '') : 'users'}</div>
                                    <div>• {plan.projects} {typeof plan.projects === 'number' ? 'project' + (plan.projects > 1 ? 's' : '') : 'projects'}</div>
                                    <div>• {plan.messages} messages/mo</div>
                                    <div>• {plan.ai} AI requests/mo</div>
                                </div>
                            </div>
                        </GlassCard>
                    ))}
                </div>
            </div>

            {/* Tenant List */}
            <GlassCard>
                <div className="p-6">
                    <h2 className="text-xl font-bold mb-4">Active Tenants</h2>
                    <div className="space-y-3">
                        {[
                            { name: 'Acme Corp', subdomain: 'acme', plan: 'Enterprise', users: 45, usage: 78 },
                            { name: 'TechStart Inc', subdomain: 'techstart', plan: 'Professional', users: 12, usage: 45 },
                            { name: 'Small Biz', subdomain: 'smallbiz', plan: 'Starter', users: 3, usage: 92 }
                        ].map((tenant, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="p-4 bg-dark-800/30 rounded-lg hover:bg-dark-800/50 transition-colors cursor-pointer"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
                                            <Building2 className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <div className="font-medium">{tenant.name}</div>
                                            <div className="text-sm text-gray-400">{tenant.subdomain}.platform.com</div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <div className="text-center">
                                            <div className="text-sm text-gray-400">Plan</div>
                                            <div className="font-medium">{tenant.plan}</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-sm text-gray-400">Users</div>
                                            <div className="font-medium">{tenant.users}</div>
                                        </div>
                                        <div className="text-center min-w-[100px]">
                                            <div className="text-sm text-gray-400 mb-1">Usage</div>
                                            <div className="w-full h-2 bg-dark-900 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full ${tenant.usage > 80 ? 'bg-red-500' : tenant.usage > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                                    style={{ width: `${tenant.usage}%` }}
                                                />
                                            </div>
                                            <div className="text-xs text-gray-500 mt-1">{tenant.usage}%</div>
                                        </div>
                                        <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                                            <Settings className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </GlassCard>
        </div>
    );
}
