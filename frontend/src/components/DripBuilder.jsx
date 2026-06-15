import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { X, Plus, Clock, MessageSquare, Save } from 'lucide-react';
import { toast } from 'sonner';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { useTranslation } from '../lib/translations';

export default function DripBuilder({ campaign, onClose }) {
    const { currentProject } = useProjectStore();
    const queryClient = useQueryClient();
    const { t } = useTranslation();

    // Local state for new campaign creation
    const [name, setName] = useState(campaign?.name || '');
    const [triggerType, setTriggerType] = useState(campaign?.trigger_type || 'manual');
    const [steps, setSteps] = useState(campaign?.steps || []);

    // New step state
    const [showAddStep, setShowAddStep] = useState(false);
    const [newStepContent, setNewStepContent] = useState('');
    const [newStepDelay, setNewStepDelay] = useState(24);

    const createCampaignMutation = useMutation({
        mutationFn: async () => {
            const newCampaign = await api.dripCampaigns.createCampaign(currentProject.id, { name, trigger_type: triggerType });
            // If we had steps locally (for new creation), we'd loop and add them here. 
            // For simplify, we just create the shell first.
            return newCampaign;
        },
        onSuccess: () => {
            toast.success(t('common.save'));
            queryClient.invalidateQueries(['drip-campaigns']);
            onClose();
        }
    });

    const addStepMutation = useMutation({
        mutationFn: (data) => api.dripCampaigns.addStep(currentProject.id, campaign.id, data),
        onSuccess: (newStep) => {
            setSteps([...steps, newStep]);
            setShowAddStep(false);
            setNewStepContent('');
            toast.success(t('common.save'));
            queryClient.invalidateQueries(['drip-campaigns']);
        }
    });

    const handleSave = () => {
        if (!campaign) {
            createCampaignMutation.mutate();
        } else {
            onClose(); // Update not implemented for simplicity
        }
    };

    const handleAddStep = () => {
        if (!campaign) {
            toast.error(t('common.error'));
            return;
        }

        addStepMutation.mutate({
            step_order: steps.length + 1,
            content_template: newStepContent,
            delay_hours: parseInt(newStepDelay)
        });
    };

    return (
        <div className="fixed inset-0 z-50 flex justify-end">
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

            <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                className="relative w-full max-w-2xl bg-dark-900 h-full border-l border-white/10 shadow-2xl flex flex-col"
            >
                {/* Header */}
                <div className="p-6 border-b border-white/10 flex items-center justify-between">
                    <h2 className="text-xl font-bold">
                        {campaign ? t('common.edit') : t('campaigns.new')}
                    </h2>
                    <button onClick={onClose}><X className="w-5 h-5" /></button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {/* Settings */}
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">{t('campaigns.builder.name')}</label>
                            <input
                                type="text"
                                value={name} onChange={(e) => setName(e.target.value)}
                                className="w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2"
                                placeholder="e.g. Welcome Series"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">{t('campaigns.builder.trigger')}</label>
                            <select
                                value={triggerType} onChange={(e) => setTriggerType(e.target.value)}
                                className="w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2"
                            >
                                <option value="manual">{t('deals.stages.negotiation')}</option>
                                <option value="tag_added">{t('deals.stages.qualified')}</option>
                                <option value="new_customer">{t('deals.stages.new_lead')}</option>
                            </select>
                        </div>
                    </div>

                    <div className="h-px bg-white/10" />

                    {/* Timeline / Steps */}
                    <div>
                        <h3 className="text-lg font-semibold mb-4">{t('reports.charts.revenue')}</h3>

                        <div className="relative space-y-6">
                            {/* Vertical Line */}
                            <div className="absolute left-4 top-2 bottom-0 w-px bg-white/10 -z-10" />

                            {steps.map((step, idx) => (
                                <div key={step.id || idx} className="flex gap-4">
                                    <div className="w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30 font-mono text-sm">
                                        {idx + 1}
                                    </div>
                                    <div className="flex-1 glass-card p-4 rounded-lg">
                                        <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                                            <Clock className="w-3 h-3" />
                                            <span>{t('reports.controls.ranges.last_7').replace('7', step.delay_hours)}</span>
                                        </div>
                                        <p className="text-sm bg-black/20 p-2 rounded border border-white/5">
                                            {step.content_template}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {/* Add Step UI */}
                            {showAddStep ? (
                                <div className="ml-12 glass-card p-4 rounded-lg border border-accent-500/30 animate-in fade-in zoom-in-95">
                                    <h4 className="font-medium text-sm mb-3">{t('campaigns.builder.add_step')}</h4>

                                    <div className="space-y-3">
                                        <div>
                                            <label className="text-xs text-gray-400">{t('reports.controls.ranges.last_30')}</label>
                                            <input
                                                type="number"
                                                value={newStepDelay} onChange={(e) => setNewStepDelay(e.target.value)}
                                                className="w-full bg-dark-950 border border-white/10 rounded px-2 py-1 text-sm"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-gray-400">{t('inbox.chat.input_placeholder')}</label>
                                            <textarea
                                                value={newStepContent} onChange={(e) => setNewStepContent(e.target.value)}
                                                className="w-full bg-dark-950 border border-white/10 rounded px-2 py-1 text-sm h-20"
                                                placeholder="Hello {{name}}, checking in..."
                                            />
                                        </div>
                                        <div className="flex justify-end gap-2">
                                            <button
                                                onClick={() => { setShowAddStep(false); }}
                                                className="text-xs text-gray-400 hover:text-white px-2 py-1"
                                            >
                                                {t('common.cancel')}
                                            </button>
                                            <button
                                                onClick={handleAddStep}
                                                className="bg-accent-500 hover:bg-accent-600 text-white text-xs px-3 py-1.5 rounded"
                                            >
                                                {t('campaigns.builder.add_step')}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <button
                                    onClick={() => setShowAddStep(true)}
                                    className="ml-12 flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors"
                                >
                                    <div className="w-8 h-8 rounded-full border border-dashed border-gray-600 flex items-center justify-center">
                                        <Plus className="w-4 h-4" />
                                    </div>
                                    {t('campaigns.builder.add_step')}
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/10 flex justify-end gap-3">
                    <button onClick={onClose} className="px-4 py-2 rounded-lg text-gray-400 hover:bg-white/5">
                        {t('common.cancel')}
                    </button>
                    <button
                        onClick={handleSave}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" />
                        {t('campaigns.builder.save')}
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
