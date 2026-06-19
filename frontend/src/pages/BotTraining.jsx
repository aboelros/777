import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  GraduationCap, Plus, Edit2, Trash2, Search,
  X, AlertCircle, BookOpen, Zap, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import ApiErrorState from '../components/ApiErrorState';
import SkeletonLoader from '../components/SkeletonLoader';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

export default function BotTraining() {
  const queryClient = useQueryClient();
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('instructions'); // 'instructions' or 'knowledge'

  const [showAddModal, setShowAddModal] = useState(false);
  const [showScrapeModal, setShowScrapeModal] = useState(false);
  const [editingInstruction, setEditingInstruction] = useState(null);
  const [editingKnowledge, setEditingKnowledge] = useState(null);

  // Fetch instructions
  const { data: instructionsData, isLoading: isLoadingInstructions } = useQuery({
    queryKey: ['bot-instructions', currentProject?.id],
    queryFn: () => api.botTraining.getInstructions(currentProject.id),
    enabled: !!currentProject && activeTab === 'instructions',
  });

  const instructions = instructionsData?.instructions || [];

  // Fetch knowledge base
  const { data: knowledgeData, isLoading: isLoadingKnowledge } = useQuery({
    queryKey: ['knowledge-base', currentProject?.id],
    queryFn: () => api.knowledge.list(currentProject.id),
    enabled: !!currentProject && activeTab === 'knowledge',
  });

  const knowledgeItems = knowledgeData || [];

  // Knowledge mutations
  const createKnowledgeMutation = useMutation({
    mutationFn: (data) => api.knowledge.create(currentProject.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('Knowledge item added!');
      setShowAddModal(false);
    },
    onError: (err) => toast.error('Failed to add knowledge item'),
  });

  const updateKnowledgeMutation = useMutation({
    mutationFn: ({ id, data }) => api.knowledge.update(currentProject.id, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('Knowledge item updated!');
      setEditingKnowledge(null);
    },
    onError: (err) => toast.error('Failed to update knowledge item'),
  });

  const deleteKnowledgeMutation = useMutation({
    mutationFn: (id) => api.knowledge.delete(currentProject.id, id),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('Knowledge item deleted');
    },
    onError: (err) => toast.error('Failed to delete knowledge item'),
  });

  const scrapeMutation = useMutation({
    mutationFn: (url) => api.knowledge.scrape(currentProject.id, { url }),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('Knowledge scraped and added!');
      setShowScrapeModal(false);
    },
    onError: (err) => toast.error('Failed to scrape content. Please try manual entry.'),
  });

  // Instruction mutations
  const createMutation = useMutation({
    mutationFn: (data) => api.botTraining.createInstruction(currentProject.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('Instruction added successfully!');
      setShowAddModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create instruction');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) =>
      api.botTraining.updateInstruction(currentProject.id, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('Instruction updated successfully!');
      setEditingInstruction(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update instruction');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) =>
      api.botTraining.deleteInstruction(currentProject.id, id),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('Instruction deleted successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete instruction');
    },
  });

  // Seed instructions mutation
  const seedMutation = useMutation({
    mutationFn: () => api.botTraining.seedInstructions(currentProject.id),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success(data.message || '🚀 Amazing default instructions created!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to seed instructions');
    },
  });

  const filteredInstructions = instructions.filter(inst =>
    inst.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inst.instruction.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredKnowledge = knowledgeItems.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

  const isLoading = activeTab === 'instructions' ? isLoadingInstructions : isLoadingKnowledge;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <GraduationCap className="w-8 h-8 text-accent-primary" />
            {t('bot_training.title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('bot_training.subtitle')}</p>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === 'instructions' && instructions.length === 0 && (
            <button
              onClick={() => seedMutation.mutate()}
              disabled={seedMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-lg hover:bg-sky-500/20 transition-all font-medium"
            >
              <Zap className="w-4 h-4" />
              {t('bot_training.buttons.auto_train')}
            </button>
          )}
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-600 transition-all font-medium"
          >
            <Plus className="w-4 h-4" />
            {activeTab === 'instructions' ? t('bot_training.buttons.add_instruction') : t('bot_training.buttons.add_knowledge')}
          </button>

          {activeTab === 'knowledge' && (
            <button
              onClick={() => setShowScrapeModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg hover:from-emerald-600 hover:to-teal-700 transition-all font-medium border border-white/10"
            >
              <Zap className="w-4 h-4" />
              {t('bot_training.buttons.scrape_url')}
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-4 mb-6 border-b border-white/5">
        <button
          onClick={() => setActiveTab('instructions')}
          className={`pb-4 px-2 font-medium transition-all relative ${activeTab === 'instructions' ? 'text-accent-primary' : 'text-gray-400 hover:text-white'
            }`}
        >
          {t('bot_training.tabs.instructions')}
          {activeTab === 'instructions' && (
            <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-primary" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('knowledge')}
          className={`pb-4 px-2 font-medium transition-all relative ${activeTab === 'knowledge' ? 'text-accent-primary' : 'text-gray-400 hover:text-white'
            }`}
        >
          {t('bot_training.tabs.knowledge')}
          {activeTab === 'knowledge' && (
            <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-primary" />
          )}
        </button>
      </div>

      {/* Search and Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-2 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder={t('bot_training.search_placeholder')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all font-medium text-white"
          />
        </div>

        <div className="glass-card px-6 py-3 rounded-xl border border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${activeTab === 'instructions' ? 'bg-accent-primary/10 text-accent-primary' : 'bg-green-500/10 text-green-400'}`}>
              {activeTab === 'instructions' ? <Sparkles className="w-5 h-5" /> : <BookOpen className="w-5 h-5" />}
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wider font-bold">
                {activeTab === 'instructions' ? t('bot_training.stats.total_instructions') : t('bot_training.stats.total_knowledge')}
              </p>
              <p className="text-xl font-bold">{activeTab === 'instructions' ? instructions.length : knowledgeItems.length}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400 uppercase tracking-wider font-bold">{t('bot_training.stats.status')}</p>
            <p className="text-sm font-medium text-green-500">{t('bot_training.stats.live')}</p>
          </div>
        </div>
      </div>

      {/* Content Section */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mb-4"></div>
          <p className="text-gray-400">Loading your {activeTab}...</p>
        </div>
      ) : activeTab === 'instructions' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredInstructions.length === 0 ? (
            <div className="md:col-span-2 text-center py-20 glass-card">
              <GraduationCap className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">{t('bot_training.empty.no_instructions')}</h3>
              <p className="text-gray-400">{t('bot_training.empty.add_instruction_desc')}</p>
            </div>
          ) : (
            filteredInstructions.map((instruction) => (
              <InstructionCard
                key={instruction.id}
                instruction={instruction}
                onEdit={() => setEditingInstruction(instruction)}
                onDelete={() => {
                  if (window.confirm('Are you sure you want to delete this instruction?')) {
                    deleteMutation.mutate(instruction.id);
                  }
                }}
              />
            ))
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKnowledge.length === 0 ? (
            <div className="md:col-span-2 lg:col-span-3 text-center py-20 glass-card">
              <BookOpen className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">{t('bot_training.empty.no_knowledge')}</h3>
              <p className="text-gray-400">{t('bot_training.empty.add_knowledge_desc')}</p>
            </div>
          ) : (
            filteredKnowledge.map((item) => (
              <KnowledgeCard
                key={item.id}
                item={item}
                onEdit={() => setEditingKnowledge(item)}
                onDelete={() => {
                  if (window.confirm('Are you sure you want to delete this knowledge item?')) {
                    deleteKnowledgeMutation.mutate(item.id);
                  }
                }}
              />
            ))
          )}
        </div>
      )}

      {/* Modals */}
      <InstructionModal
        show={(showAddModal && activeTab === 'instructions') || !!editingInstruction}
        instruction={editingInstruction}
        onClose={() => {
          setShowAddModal(false);
          setEditingInstruction(null);
        }}
        onSave={(data) => {
          if (editingInstruction) {
            updateMutation.mutate({ id: editingInstruction.id, data });
          } else {
            createMutation.mutate(data);
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
          if (editingKnowledge) {
            updateKnowledgeMutation.mutate({ id: editingKnowledge.id, data });
          } else {
            createKnowledgeMutation.mutate(data);
          }
        }}
      />

      <ScrapeModal
        show={showScrapeModal}
        onClose={() => setShowScrapeModal(false)}
        onScrape={(url) => scrapeMutation.mutate(url)}
        isLoading={scrapeMutation.isPending}
      />
    </div>
  );
}

function InstructionCard({ instruction, onEdit, onDelete }) {
  const categoryColors = {
    tone: 'from-accent-primary to-accent-600',
    product_knowledge: 'from-green-500 to-emerald-600',
    response_style: 'from-indigo-500 to-blue-600',
    promotions: 'from-yellow-500 to-orange-600',
    service: 'from-red-500 to-sky-600',
  };

  const categoryColor = categoryColors[instruction.category] || 'from-gray-500 to-gray-600';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 rounded-xl hover:bg-white/5 transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-semibold text-white">{instruction.title}</h3>
            {instruction.category && (
              <span className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${categoryColor} text-white`}>
                {instruction.category}
              </span>
            )}
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-accent-primary/20 text-accent-primary">
              Priority: {instruction.priority}
            </span>
          </div>
          <p className="text-gray-400 text-sm line-clamp-3">{instruction.instruction}</p>
        </div>
        <div className={`ml-4 w-12 h-12 rounded-lg flex items-center justify-center ${instruction.is_active ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
          {instruction.is_active ? (
            <span className="text-green-400 text-xs font-bold">ON</span>
          ) : (
            <span className="text-gray-400 text-xs font-bold">OFF</span>
          )}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onEdit}
          className="flex-1 glass-card px-4 py-2 rounded-lg hover:bg-white/10 transition-colors flex items-center justify-center gap-2 text-sm font-medium text-white"
        >
          <Edit2 className="w-4 h-4" />
          Edit
        </button>
        <button
          onClick={onDelete}
          className="glass-card px-4 py-2 rounded-lg hover:bg-red-500/20 transition-colors flex items-center justify-center group"
        >
          <Trash2 className="w-4 h-4 text-gray-500 group-hover:text-red-400" />
        </button>
      </div>
    </motion.div>
  );
}

function KnowledgeCard({ item, onEdit, onDelete }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 rounded-xl hover:bg-white/5 transition-all flex flex-col h-full"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-4 h-4 text-green-400" />
            <h3 className="text-lg font-bold line-clamp-1 text-white">{item.title}</h3>
          </div>
          <div className="text-sm text-gray-400 line-clamp-4 bg-black/20 p-3 rounded-lg border border-white/5">
            {item.content}
          </div>
        </div>
        <div className={`ml-3 px-2 py-1 rounded text-[10px] font-bold uppercase ${item.is_active ? 'bg-green-500/10 text-green-400' : 'bg-gray-500/10 text-gray-400'}`}>
          {item.is_active ? 'Active' : 'Draft'}
        </div>
      </div>

      <div className="mt-auto flex items-center justify-between pt-4 border-t border-white/5">
        <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">{item.source_type || 'Text'}</span>
        <div className="flex gap-2">
          <button onClick={onEdit} className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-all">
            <Edit2 className="w-4 h-4 text-white" />
          </button>
          <button onClick={onDelete} className="p-2 hover:bg-red-500/10 rounded-lg text-gray-500 hover:text-red-400 transition-all">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function InstructionModal({ show, instruction, onClose, onSave }) {
  const [formData, setFormData] = useState({
    title: '',
    instruction: '',
    category: 'tone',
    priority: 5,
    is_active: true,
  });

  useEffect(() => {
    if (instruction) {
      setFormData({
        title: instruction.title || '',
        instruction: instruction.instruction || '',
        category: instruction.category || 'tone',
        priority: instruction.priority || 5,
        is_active: instruction.is_active !== false,
      });
    } else {
      setFormData({
        title: '',
        instruction: '',
        category: 'tone',
        priority: 5,
        is_active: true,
      });
    }
  }, [instruction, show]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-lg w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">{instruction ? t('bot_training.modals.edit_instruction') : t('bot_training.modals.add_instruction')}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X className="w-6 h-6" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Title</label>
            <input
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              placeholder="e.g., Friendly Greeting"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Instruction</label>
            <textarea
              value={formData.instruction}
              onChange={e => setFormData({ ...formData, instruction: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 h-32 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              placeholder="Describe how the AI should behave..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Category</label>
              <select
                value={formData.category}
                onChange={e => setFormData({ ...formData, category: e.target.value })}
                className="w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white"
              >
                <option value="tone">Tone</option>
                <option value="product_knowledge">Product Knowledge</option>
                <option value="response_style">Response Style</option>
                <option value="promotions">Promotions</option>
                <option value="service">Service</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Priority</label>
              <input
                type="number"
                value={formData.priority}
                onChange={e => setFormData({ ...formData, priority: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              />
            </div>
          </div>
        </div>
        <div className="flex gap-3 mt-8">
          <button onClick={onClose} className="flex-1 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all font-medium text-white">Cancel</button>
          <button onClick={() => onSave(formData)} className="flex-1 px-4 py-2 rounded-lg bg-accent-primary hover:bg-accent-600 transition-all font-medium text-white shadow-lg shadow-accent-primary/20">Save changes</button>
        </div>
      </motion.div>
    </div>
  );
}

function KnowledgeModal({ show, item, onClose, onSave }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    source_type: 'text',
    is_active: true,
  });

  useEffect(() => {
    if (item) {
      setFormData({
        title: item.title || '',
        content: item.content || '',
        source_type: item.source_type || 'text',
        is_active: item.is_active !== false,
      });
    } else {
      setFormData({
        title: '',
        content: '',
        source_type: 'text',
        is_active: true,
      });
    }
  }, [item, show]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-lg w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">{item ? 'Edit Knowledge' : 'Add Knowledge'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors"><X className="w-6 h-6" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 text-white/60">{t('bot_training.modals.fields.title')}</label>
            <input
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-accent-primary/50 focus:outline-none transition-all"
              placeholder="e.g., Refund Policy"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 text-white/60">{t('bot_training.modals.fields.content')}</label>
            <textarea
              value={formData.content}
              onChange={e => setFormData({ ...formData, content: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 h-40 text-white focus:ring-2 focus:ring-accent-primary/50 focus:outline-none transition-all resize-none"
              placeholder="Paste business knowledge, rules, or FAQs here..."
            />
          </div>
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={e => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-5 h-5 rounded bg-white/5 border-white/20 accent-accent-primary cursor-pointer"
                id="kb-active"
              />
              <label htmlFor="kb-active" className="text-sm font-medium cursor-pointer select-none text-white">{t('bot_training.modals.fields.published')}</label>
            </div>
            <select
              value={formData.source_type}
              onChange={e => setFormData({ ...formData, source_type: e.target.value })}
              className="bg-dark-800 border border-white/10 rounded-lg px-3 py-1 text-[10px] font-bold uppercase text-white outline-none cursor-pointer"
            >
              <option value="text">Text</option>
              <option value="faq">FAQ</option>
              <option value="policy">Policy</option>
              <option value="document">Document</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 mt-8">
          <button onClick={onClose} className="flex-1 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all font-bold text-sm text-white">{t('bot_training.buttons.cancel')}</button>
          <button onClick={() => onSave(formData)} className="flex-1 px-4 py-3 rounded-xl bg-accent-primary hover:bg-accent-600 transition-all font-bold text-sm text-white shadow-lg shadow-accent-primary/20">{t('bot_training.buttons.save')}</button>
        </div>
      </motion.div>
    </div>
  );
}

function ScrapeModal({ show, onClose, onScrape, isLoading }) {
  const [url, setUrl] = useState('');

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-md w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
              <Zap className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white">{t('bot_training.modals.scrape_title')}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors"><X className="w-6 h-6" /></button>
        </div>

        <p className="text-gray-400 text-sm mb-6">
          {t('bot_training.modals.scrape_desc')}
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">{t('bot_training.modals.fields.website_url')}</label>
            <input
              value={url}
              onChange={e => setUrl(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 focus:outline-none transition-all"
              placeholder="https://example.com/faq"
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all font-bold text-sm disabled:opacity-50 text-white"
          >
            {t('bot_training.buttons.cancel')}
          </button>
          <button
            onClick={() => onScrape(url)}
            disabled={isLoading || !url}
            className="flex-1 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 transition-all font-bold text-sm text-white shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                Scraping...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Extract Knowledge
              </>
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
