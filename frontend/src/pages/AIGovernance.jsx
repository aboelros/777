/**
 * AI Governance Settings Page
 * Configure AI confidence thresholds and escalation rules.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Brain, Shield, AlertTriangle, Settings, Save,
    Users, Bell, CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '../components/GlassCard';
import ApiErrorState from '../components/ApiErrorState';
import SkeletonLoader from '../components/SkeletonLoader';
import { useProjectStore } from '../store/projectStore';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';
import Button from '../components/Button';

export default function AIGovernance() {
    const { currentProject } = useProjectStore();
    const { t } = useTranslation();

    const [settings, setSettings] = useState({
        minConfidence: 0.75,
        escalateOnLowConfidence: true,
        escalateFinancial: true,
        escalatePolicy: true,
        escalateLegal: false,
        allowedOverrideRoles: ['admin', 'manager'],
        notifyOnEscalation: true,
        autoResponseEnabled: true,
        humanReviewRequired: false
    });

    const handleSave = async () => {
        try {
            // TODO: API call to save settings
            toast.success('AI governance settings saved');
        } catch (error) {
            toast.error('Failed to save settings');
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3 text-white">
                        <Brain className="w-10 h-10 text-accent-primary" />
                        AI Governance
                    </h1>
                    <p className="text-gray-400">
                        Configure AI confidence thresholds and human oversight rules
                    </p>
                </div>

                <Button
                    onClick={handleSave}
                    variant="primary"
                    className="shadow-neon"
                    leftIcon={Save}
                >
                    Save Settings
                </Button>
            </div>

            {/* Confidence Threshold */}
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                            <Settings className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Confidence Threshold</h2>
                            <p className="text-sm text-gray-400">
                                Minimum confidence score for automatic responses
                            </p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-sm font-medium">
                                    Minimum Confidence Score
                                </label>
                                <span className="text-lg font-bold text-accent-primary">
                                    {Math.round(settings.minConfidence * 100)}%
                                </span>
                            </div>

                            <input
                                type="range"
                                min="0.5"
                                max="1.0"
                                step="0.05"
                                value={settings.minConfidence}
                                onChange={(e) => setSettings({
                                    ...settings,
                                    minConfidence: parseFloat(e.target.value)
                                })}
                                className="w-full h-2 bg-dark-800 rounded-lg appearance-none cursor-pointer slider"
                            />

                            <div className="flex justify-between text-xs text-gray-400 mt-1">
                                <span>50% (Permissive)</span>
                                <span>75% (Balanced)</span>
                                <span>100% (Strict)</span>
                            </div>
                        </div>

                        <div className="p-4 bg-dark-800/50 rounded-lg border border-white/5">
                            <p className="text-sm text-gray-300">
                                Responses below this threshold will be flagged for human review.
                                Higher values ensure more accurate responses but may require more human intervention.
                            </p>
                        </div>
                    </div>
                </div>
            </GlassCard>

            {/* Escalation Rules */}
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center">
                            <AlertTriangle className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Escalation Rules</h2>
                            <p className="text-sm text-gray-400">
                                Automatically escalate specific types of queries
                            </p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    checked={settings.escalateOnLowConfidence}
                                    onChange={(e) => setSettings({
                                        ...settings,
                                        escalateOnLowConfidence: e.target.checked
                                    })}
                                    className="w-4 h-4 rounded border-gray-600"
                                />
                                <div>
                                    <div className="font-medium">Low Confidence Responses</div>
                                    <div className="text-xs text-gray-400">
                                        Escalate when confidence is below threshold
                                    </div>
                                </div>
                            </div>
                            {settings.escalateOnLowConfidence && (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            )}
                        </label>

                        <label className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    checked={settings.escalateFinancial}
                                    onChange={(e) => setSettings({
                                        ...settings,
                                        escalateFinancial: e.target.checked
                                    })}
                                    className="w-4 h-4 rounded border-gray-600"
                                />
                                <div>
                                    <div className="font-medium">Financial Queries</div>
                                    <div className="text-xs text-gray-400">
                                        Pricing, payments, refunds, billing
                                    </div>
                                </div>
                            </div>
                            {settings.escalateFinancial && (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            )}
                        </label>

                        <label className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    checked={settings.escalatePolicy}
                                    onChange={(e) => setSettings({
                                        ...settings,
                                        escalatePolicy: e.target.checked
                                    })}
                                    className="w-4 h-4 rounded border-gray-600"
                                />
                                <div>
                                    <div className="font-medium">Policy Questions</div>
                                    <div className="text-xs text-gray-400">
                                        Terms of service, privacy, data handling
                                    </div>
                                </div>
                            </div>
                            {settings.escalatePolicy && (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            )}
                        </label>

                        <label className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    checked={settings.escalateLegal}
                                    onChange={(e) => setSettings({
                                        ...settings,
                                        escalateLegal: e.target.checked
                                    })}
                                    className="w-4 h-4 rounded border-gray-600"
                                />
                                <div>
                                    <div className="font-medium">Legal Matters</div>
                                    <div className="text-xs text-gray-400">
                                        Compliance, regulations, legal advice
                                    </div>
                                </div>
                            </div>
                            {settings.escalateLegal && (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            )}
                        </label>
                    </div>
                </div>
            </GlassCard>

            {/* Override Permissions */}
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                            <Users className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Override Permissions</h2>
                            <p className="text-sm text-gray-400">
                                Control who can override AI decisions
                            </p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {['admin', 'manager', 'agent'].map(role => (
                            <label
                                key={role}
                                className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <input
                                        type="checkbox"
                                        checked={settings.allowedOverrideRoles.includes(role)}
                                        onChange={(e) => {
                                            if (e.target.checked) {
                                                setSettings({
                                                    ...settings,
                                                    allowedOverrideRoles: [...settings.allowedOverrideRoles, role]
                                                });
                                            } else {
                                                setSettings({
                                                    ...settings,
                                                    allowedOverrideRoles: settings.allowedOverrideRoles.filter(r => r !== role)
                                                });
                                            }
                                        }}
                                        className="w-4 h-4 rounded border-gray-600"
                                    />
                                    <div className="font-medium capitalize">{role}</div>
                                </div>
                                {settings.allowedOverrideRoles.includes(role) && (
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                )}
                            </label>
                        ))}
                    </div>
                </div>
            </GlassCard>

            {/* Notifications */}
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <Bell className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Notifications</h2>
                            <p className="text-sm text-gray-400">
                                Alert preferences for AI escalations
                            </p>
                        </div>
                    </div>

                    <label className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg cursor-pointer hover:bg-dark-800/50 transition-colors">
                        <div className="flex items-center gap-3">
                            <input
                                type="checkbox"
                                checked={settings.notifyOnEscalation}
                                onChange={(e) => setSettings({
                                    ...settings,
                                    notifyOnEscalation: e.target.checked
                                })}
                                className="w-4 h-4 rounded border-gray-600"
                            />
                            <div>
                                <div className="font-medium">Notify on Escalation</div>
                                <div className="text-xs text-gray-400">
                                    Send alerts when AI escalates to human review
                                </div>
                            </div>
                        </div>
                        {settings.notifyOnEscalation && (
                            <CheckCircle className="w-5 h-5 text-green-400" />
                        )}
                    </label>
                </div>
            </GlassCard>
        </div>
    );
}
