import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  GraduationCap, Plus, Search, BookOpen,
  Sparkles, User, Wrench, Zap
} from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { NoProjectState } from '@/components/ui/EmptyState';

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
    return <NoProjectState subtitle={t('bot_training.subtitle') || 'Select a project to train AI persona, knowledge base, and automated actions'} />;
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
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <GraduationCap className="w-6 h-6" />
            </span>
            {t('bot_training.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('bot_training.subtitle')}</p>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === 'instructions' && (
            <Button
              onClick={() => setShowAddModal(true)}
              variant="primary"
              leftIcon={Plus}
            >
              {t('bot_training.buttons.add_instruction') || 'Add Instruction'}
            </Button>
          )}
          {activeTab === 'knowledge' && (
            <>
              <Button
                onClick={() => setShowScrapeModal(true)}
                variant="secondary"
                leftIcon={Zap}
              >
                {t('bot_training.buttons.scrape_url') || 'Scrape URL'}
              </Button>
              <Button
                onClick={() => setShowAddModal(true)}
                variant="primary"
                leftIcon={Plus}
              >
                {t('bot_training.buttons.add_knowledge') || 'Add Knowledge'}
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 border-b border-border pb-2 overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all relative ${
                isActive ? 'text-text-primary bg-surface-subtle border border-border' : 'text-text-muted hover:text-text-primary hover:bg-surface-subtle/50'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-brand-primary' : ''}`} />
              {tab.label}
              {isActive && (
                <motion.div layoutId="trainingTabIndicator" className="absolute bottom-0 left-2 right-2 h-0.5 bg-brand-primary" />
              )}
            </button>
          );
        })}
      </div>

      {(activeTab === 'instructions' || activeTab === 'knowledge') && (
        <div className="glass-panel p-3 rounded-2xl border border-border">
          <Input
            icon={Search}
            placeholder={t('bot_training.search_placeholder') || 'Filter entries...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
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
            if (window.confirm('Delete this instruction?')) {
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
            if (window.confirm('Delete this knowledge item?')) {
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
