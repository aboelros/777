import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  GraduationCap, Plus, Search, AlertCircle, BookOpen,
  Sparkles, User, Wrench, Zap
} from 'lucide-react';
import { useProjectStore } from '../../../store/projectStore';
import { useTranslation } from '../../../lib/translations';

import PersonaSettingsTab from '../components/PersonaSettingsTab';
import InstructionsTab from '../components/InstructionsTab';
import ToolsTab from '../components/ToolsTab';
import KnowledgeTab from '../components/KnowledgeTab';
import InstructionModal from '../components/InstructionModal';
import KnowledgeModal from '../components/KnowledgeModal';
import ScrapeModal from '../components/ScrapeModal';
import { useBotTrainingData } from '../components/useBotTrainingData';

export default function BotTraining() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('persona');

  const [showAddModal, setShowAddModal] = useState(false);
  const [showScrapeModal, setShowScrapeModal] = useState(false);
  const [editingInstruction, setEditingInstruction] = useState(null);
  const [editingKnowledge, setEditingKnowledge] = useState(null);

  const {
    instructions,
    createInstructionMutation,
    updateInstructionMutation,
    deleteInstructionMutation,
    seedMutation,
    knowledgeItems,
    createKnowledgeMutation,
    updateKnowledgeMutation,
    deleteKnowledgeMutation,
    scrapeMutation,
  } = useBotTrainingData(currentProject, activeTab);

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">No Project Selected</h2>
          <p className="text-gray-400">Please select a project to train the AI bot</p>
        </div>
      </div>
    );
  }

  const filteredInstructions = instructions.filter(
    (i) => i.title.toLowerCase().includes(searchTerm.toLowerCase()) || i.instruction.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredKnowledge = knowledgeItems.filter(
    (k) => k.title.toLowerCase().includes(searchTerm.toLowerCase()) || k.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const TABS = [
    { id: 'persona', label: t('bot_training.tabs.persona') || 'Human Persona & Voice', icon: User },
    { id: 'instructions', label: t('bot_training.tabs.instructions') || 'AI Instructions', icon: Sparkles },
    { id: 'tools', label: t('bot_training.tabs.tools') || 'AI Tools & Capabilities', icon: Wrench },
    { id: 'knowledge', label: t('bot_training.tabs.knowledge') || 'Knowledge Base (RAG)', icon: BookOpen },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <GraduationCap className="w-8 h-8 text-accent-primary" />
            {t('bot_training.title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('bot_training.subtitle')}</p>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === 'instructions' && (
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-accent-primary text-white rounded-xl hover:bg-accent-600 transition-all font-bold text-sm shadow-lg shadow-accent-primary/20"
            >
              <Plus className="w-4 h-4" />
              {t('bot_training.buttons.add_instruction')}
            </button>
          )}
          {activeTab === 'knowledge' && (
            <>
              <button
                onClick={() => setShowScrapeModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-bold text-sm hover:from-emerald-600 hover:to-teal-700 transition-all"
              >
                <Zap className="w-4 h-4" />
                {t('bot_training.buttons.scrape_url')}
              </button>
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-accent-primary text-white rounded-xl hover:bg-accent-600 transition-all font-bold text-sm shadow-lg shadow-accent-primary/20"
              >
                <Plus className="w-4 h-4" />
                {t('bot_training.buttons.add_knowledge')}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 border-b border-white/10 pb-2 overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold transition-all relative ${
                isActive ? 'text-white bg-white/10' : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-accent-primary' : ''}`} />
              {tab.label}
              {isActive && (
                <motion.div layoutId="trainingTabIndicator" className="absolute bottom-0 left-2 right-2 h-0.5 bg-accent-primary" />
              )}
            </button>
          );
        })}
      </div>

      {(activeTab === 'instructions' || activeTab === 'knowledge') && (
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder={t('bot_training.search_placeholder')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/50 text-white font-medium"
          />
        </div>
      )}

      {activeTab === 'persona' && <PersonaSettingsTab />}

      {activeTab === 'instructions' && (
        <InstructionsTab
          instructions={filteredInstructions}
          onAdd={() => setShowAddModal(true)}
          onEdit={(inst) => setEditingInstruction(inst)}
          onDelete={(id) => {
            if (window.confirm('هل أنت متأكد من حذف هذه التعليمات؟')) {
              deleteInstructionMutation.mutate(id);
            }
          }}
          onSeed={() => seedMutation.mutate()}
          isSeeding={seedMutation.isPending}
        />
      )}

      {activeTab === 'tools' && <ToolsTab />}

      {activeTab === 'knowledge' && (
        <KnowledgeTab
          items={filteredKnowledge}
          onAdd={() => setShowAddModal(true)}
          onEdit={(item) => setEditingKnowledge(item)}
          onDelete={(id) => {
            if (window.confirm('هل أنت متأكد من حذف هذا العنصر؟')) {
              deleteKnowledgeMutation.mutate(id);
            }
          }}
          onScrape={() => setShowScrapeModal(true)}
          onApplyTemplate={(tmpl) => setEditingKnowledge({ ...tmpl, is_active: true })}
        />
      )}

      <InstructionModal
        show={(showAddModal && activeTab === 'instructions') || !!editingInstruction}
        instruction={editingInstruction}
        onClose={() => {
          setShowAddModal(false);
          setEditingInstruction(null);
        }}
        onSave={(data) => {
          if (editingInstruction) {
            updateInstructionMutation.mutate({ id: editingInstruction.id, data }, { onSuccess: () => setEditingInstruction(null) });
          } else {
            createInstructionMutation.mutate(data, { onSuccess: () => setShowAddModal(false) });
          }
        }}
      />

      <KnowledgeModal
        show={(showAddModal && activeTab === 'knowledge') || !!editingKnowledge}
        item={editingKnowledge}
        onClose={() => {
          setShowAddModal(false);
          setEditingKnowledge(null);
        }}
        onSave={(data) => {
          if (editingKnowledge && editingKnowledge.id) {
            updateKnowledgeMutation.mutate({ id: editingKnowledge.id, data }, { onSuccess: () => setEditingKnowledge(null) });
          } else {
            createKnowledgeMutation.mutate(data, { onSuccess: () => { setShowAddModal(false); setEditingKnowledge(null); } });
          }
        }}
      />

      <ScrapeModal
        show={showScrapeModal}
        onClose={() => setShowScrapeModal(false)}
        onScrape={(url) => scrapeMutation.mutate(url, { onSuccess: () => setShowScrapeModal(false) })}
        isLoading={scrapeMutation.isPending}
      />
    </div>
  );
}
