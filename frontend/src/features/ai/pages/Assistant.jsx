import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Zap, Code, TrendingUp, Package, MessageCircle, BarChart3 } from 'lucide-react';
import { useMutation, useQuery } from '@tanstack/react-query';
import GlassCard from '../../../components/ui/GlassCard';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import { generateContextualSuggestions, getInitialGreeting } from '../../../services/botInstructions';
import { useTranslation } from '../../../lib/translations';

const ThinkingStep = ({ text, delay }) => {
  const [show, setShow] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const showTimer = setTimeout(() => setShow(true), delay);
    const completeTimer = setTimeout(() => setCompleted(true), delay + 1500);
    return () => {
      clearTimeout(showTimer);
      clearTimeout(completeTimer);
    };
  }, [delay]);

  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-2 text-xs text-gray-400"
    >
      {completed ? (
        <div className="w-4 h-4 rounded-full bg-green-500/20 flex items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-1.5 h-1.5 rounded-full bg-green-400"
          />
        </div>
      ) : (
        <div className="w-4 h-4 rounded-full border border-accent-500/30 border-t-accent-500 animate-spin" />
      )}
      <span className={completed ? 'text-gray-500 line-through decoration-accent-500/50' : 'text-gray-300'}>
        {text}
      </span>
    </motion.div>
  );
};

export default function Assistant() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [businessContext, setBusinessContext] = useState(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Fetch business context
  const { data: messageStats } = useQuery({
    queryKey: ['messageStats', currentProject?.id],
    queryFn: () => api.messages.getStats(currentProject?.id),
    enabled: !!currentProject,
    staleTime: 60000,
  });

  // Fetch assistant usage for today
  const { data: dailyUsage } = useQuery({
    queryKey: ['assistantDailyUsage', currentProject?.id],
    queryFn: () => api.assistant.usage(currentProject?.id, 1),
    enabled: !!currentProject,
  });

  // Fetch subscription for limits
  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: api.subscriptions.getMySubscription,
  });

  // Build context for AI and set initial message
  useEffect(() => {
    if (currentProject && messageStats) {
      const context = {
        project_name: currentProject.name,
        total_messages: messageStats?.data?.total_count || 0,
        unread_messages: messageStats?.data?.unread_count || 0,
      };
      setBusinessContext(context);

      // Set initial greeting with context if messages is empty
      if (messages.length === 0) {
        setMessages([{
          id: 1,
          role: 'assistant',
          content: getInitialGreeting(context, t),
          timestamp: new Date(),
          suggestions: generateContextualSuggestions([], context, t),
        }]);
      }
    }
  }, [currentProject, messageStats, t]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages]);

  // Query mutation
  const queryMutation = useMutation({
    mutationFn: (query) => {
      // Build conversation history for context
      const conversationHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp?.toISOString()
      }));

      return api.assistant.query({
        project_id: currentProject?.id,
        message: query,
        use_function_calling: true,
        context: {
          conversation_history: conversationHistory,
          project_name: currentProject?.name,
          total_messages: businessContext?.total_messages || 0,
          unread_messages: businessContext?.unread_messages || 0
        }
      });
    },
    onSuccess: (response) => {
      const assistantMessage = {
        id: Date.now(),
        role: 'assistant',
        content: response.reply || response.data?.reply || 'No response',
        function_calls: response.function_calls || response.data?.function_calls,
        tokens: response.tokens_used || response.data?.tokens_used,
        cost: response.cost || response.data?.cost,
        timestamp: new Date(),
        suggestions: generateContextualSuggestions(messages, businessContext, t) || [],
      };
      setMessages(prev => [...prev, assistantMessage]);
    },
    onError: (error) => {
      console.error('Assistant query failed:', error);
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    },
  });

  const handleSend = () => {
    if (!input.trim() || !currentProject) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Query assistant
    queryMutation.mutate(input);
    setInput('');

    // Keep focus
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (action) => {
    setInput(action);
    // Auto-send the quick action
    setTimeout(() => {
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: action,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
      queryMutation.mutate(action);
      setInput('');
    }, 100);
  };

  // Suggested actions
  const suggestedActions = [
    { icon: TrendingUp, text: t('assistant.suggestions.show_sales'), color: 'from-green-500 to-emerald-600' },
    { icon: Package, text: t('assistant.suggestions.list_orders'), color: 'from-blue-500 to-cyan-600' },
    { icon: MessageCircle, text: t('assistant.suggestions.summarize_unread'), color: 'from-sky-500 to-sky-600' },
    { icon: BarChart3, text: t('assistant.suggestions.generate_report'), color: 'from-orange-500 to-red-600' },
  ];

  return (
    <div className="p-4 sm:p-6 h-[calc(100vh-4rem)] flex flex-col lg:flex-row gap-4 sm:gap-6">
      {/* Chat Area - 50% of screen */}
      <div className="flex-1 lg:w-[50%] flex flex-col min-h-0">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <h1 className="text-3xl font-bold text-gradient mb-2">{t('assistant.title')}</h1>
          <p className="text-gray-400">{t('assistant.subtitle')}</p>
        </motion.div>

        {/* Quick Actions */}
        {/* Quick Actions - Show only at the start (0 or 1 message) */}
        <AnimatePresence>
          {messages.length < 2 && !queryMutation.isPending && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-2 gap-3 mb-4"
            >
              {suggestedActions.map((action, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleQuickAction(action.text)}
                  className="glass-card p-4 text-left rounded-xl hover:border-accent-500/50 transition-all group relative overflow-hidden"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`} />
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <p className="text-sm font-medium leading-tight text-gray-200 group-hover:text-white transition-colors">{action.text}</p>
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages Container - Bigger */}
        <GlassCard ref={chatContainerRef} className="flex-1 p-4 sm:p-6 overflow-y-auto mb-4 space-y-4 max-h-[70vh] sm:max-h-[75vh]">
          <AnimatePresence mode="popLayout">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-cyan-600'
                  : 'bg-gradient-to-br from-accent-500 to-sky-600'
                  }`}>
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>

                {/* Message Content */}
                <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                  <div className={`relative p-5 rounded-2xl shadow-lg ${message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-cyan-700 text-white rounded-tr-sm'
                    : 'glass-card bg-white/5 border-white/10 rounded-tl-sm'
                    }`}>
                    <p className={`text-sm leading-relaxed whitespace-pre-wrap ${message.role === 'user' ? 'text-white' : 'text-gray-200'}`}>
                      {message.content}
                    </p>

                    {/* Dynamic Suggested Actions */}
                    {message.suggestions && Array.isArray(message.suggestions) && message.suggestions.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <p className="text-xs text-gray-400 mb-3 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          {t('assistant.suggested_actions')}
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {message.suggestions.map((suggestion, idx) => {
                            // Validate suggestion object
                            if (!suggestion || typeof suggestion !== 'object') return null;

                            // Map icon names to components with safe fallbacks
                            const iconMap = {
                              'TrendingUp': TrendingUp,
                              'Package': Package,
                              'MessageCircle': MessageCircle,
                              'BarChart3': BarChart3,
                              'User': User,
                            };
                            const IconComponent = iconMap[suggestion.icon] || Sparkles;
                            const suggestionColor = suggestion.color || 'from-cyan-500 to-sky-600';
                            const suggestionText = suggestion.text || 'Action';

                            return (
                              <motion.button
                                key={idx}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => handleQuickAction(suggestionText)}
                                className="glass-card p-3 rounded-lg text-left hover:bg-white/10 transition-all group border border-white/5 hover:border-cyan-500/30"
                              >
                                <div className="flex items-center gap-2">
                                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${suggestionColor} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                                    <IconComponent className="w-4 h-4 text-white" />
                                  </div>
                                  <span className="text-xs font-medium leading-tight text-gray-300 group-hover:text-white">{suggestionText}</span>
                                </div>
                              </motion.button>
                            );
                          }).filter(Boolean)}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    {message.tokens && (
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-white/5">
                        <span className="text-[10px] text-gray-500 bg-black/20 px-2 py-1 rounded-full">
                          {message.tokens} tokens
                        </span>
                        <span className="text-[10px] text-gray-500 bg-black/20 px-2 py-1 rounded-full">
                          ${message.cost?.toFixed(5)}
                        </span>
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 mt-2 px-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Thinking Steps - System 2 Visualization */}
          {queryMutation.isPending && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3 max-w-[80%]"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-500 to-sky-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white animate-pulse" />
              </div>
              <div className="glass-card p-4 rounded-2xl border-accent-500/30 bg-accent-500/5 w-full">
                <div className="flex items-center gap-2 mb-3">
                  <div className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-accent-500"></span>
                  </div>
                  <span className="text-xs font-semibold text-accent-400 uppercase tracking-wider">
                    {t('assistant.reasoning_engine')}
                  </span>
                </div>

                <div className="space-y-2">
                  <ThinkingStep text={t('assistant.steps.analyzing')} delay={0} />
                  <ThinkingStep text={t('assistant.steps.context')} delay={800} />
                  <ThinkingStep text={t('assistant.steps.formulating')} delay={1600} />
                </div>
              </div>
            </motion.div>
          )}

          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </GlassCard>

        {/* Input Area */}
        <GlassCard className="p-4">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={t('assistant.placeholder')}
              className="flex-1 input-glass resize-none focus:ring-2 focus:ring-accent-500/50 transition-all text-black"
              rows="2"
              disabled={!currentProject}
              autoFocus
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSend}
              disabled={!input.trim() || queryMutation.isPending || !currentProject}
              className="btn-neon self-end disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </GlassCard>
      </div>

      {/* Sidebar - Takes remaining 50% on desktop */}
      <div className="hidden lg:flex lg:w-[50%] flex-col space-y-4 overflow-y-auto">
        {/* Model Info */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-accent-400" />
            {t('assistant.model_info.title')}
          </h3>
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-gray-400">{t('assistant.model_info.model')}</p>
              <p className="font-medium">Gemini 2.0 Flash</p>
              <span className="text-xs text-green-400">FREE • Fast</span>
            </div>
            <div>
              <p className="text-gray-400">{t('assistant.model_info.temp')}</p>
              <p className="font-medium">0.7</p>
            </div>
            <div>
              <p className="text-gray-400">{t('assistant.model_info.max_tokens')}</p>
              <p className="font-medium">8,192</p>
            </div>
            <div>
              <p className="text-gray-400">{t('assistant.model_info.context')}</p>
              <p className="font-medium text-green-400">{t('assistant.model_info.enabled')}</p>
            </div>
          </div>
        </GlassCard>

        {/* Business Context */}
        {businessContext && (
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-accent-400" />
              {t('assistant.business_context.title')}
            </h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-400">{t('assistant.business_context.project')}</p>
                <p className="font-medium">{businessContext.project_name}</p>
              </div>
              <div>
                <p className="text-gray-400">{t('assistant.business_context.total_messages')}</p>
                <p className="font-medium">{businessContext.total_messages}</p>
              </div>
              {businessContext.unread_messages > 0 && (
                <div>
                  <p className="text-gray-400">{t('assistant.business_context.unread_messages')}</p>
                  <p className="font-medium text-orange-400">{businessContext.unread_messages}</p>
                </div>
              )}
            </div>
          </GlassCard>
        )}

        {/* Available Functions */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('assistant.capabilities.title')}</h3>
          <div className="space-y-2">
            {[
              t('assistant.capabilities.analyze'),
              t('assistant.capabilities.manage_orders'),
              t('assistant.capabilities.respond'),
              t('assistant.capabilities.reports'),
              t('assistant.capabilities.follow_ups'),
            ].map((action, index) => (
              <motion.div
                key={action}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <div className="w-1.5 h-1.5 bg-accent-400 rounded-full" />
                <span className="text-sm">{action}</span>
              </motion.div>
            ))}
          </div>
        </GlassCard>

        {/* Usage Stats */}
        {/* Usage Stats */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('assistant.usage.title')}</h3>
          <div className="space-y-4">
            {/* Requests */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">{t('assistant.usage.requests')}</span>
                <span className="text-sm font-medium">
                  {dailyUsage?.request_count || 0} / {subscription?.limits_status?.ai_requests?.limit?.toLocaleString() || '∞'}
                </span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{
                    width: `${Math.min(
                      ((dailyUsage?.request_count || 0) / (subscription?.limits_status?.ai_requests?.limit || 100)) * 100,
                      100
                    )}%`
                  }}
                  className="h-full bg-gradient-to-r from-accent-500 to-sky-500"
                />
              </div>
            </div>

            {/* Tokens */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">{t('assistant.usage.tokens')}</span>
                <span className="text-sm font-medium">
                  {(dailyUsage?.total_tokens || 0).toLocaleString()}
                </span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '100%' }}
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500 opacity-50"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1 text-right">
                {t('assistant.usage.cost')} ${(dailyUsage?.total_cost || 0).toFixed(4)}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
