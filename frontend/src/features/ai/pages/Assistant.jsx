import { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Send, Bot, Sparkles, TrendingUp, Package, MessageCircle, BarChart3 } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import { NoProjectState } from '@/components/ui/EmptyState';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { generateContextualSuggestions, getInitialGreeting } from '@/services/botInstructions';
import { useTranslation } from '@/lib/translations';

import ChatMessageItem from '../components/ChatMessageItem';
import ThinkingEngine from '../components/ThinkingEngine';
import AssistantSidebar from '../components/AssistantSidebar';

export default function Assistant() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [businessContext, setBusinessContext] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { data: messageStats } = useQuery({
    queryKey: ['messageStats', currentProject?.id],
    queryFn: () => api.messages.getStats(currentProject?.id),
    enabled: !!currentProject?.id,
  });

  const { data: dailyUsage } = useQuery({
    queryKey: ['assistantDailyUsage', currentProject?.id],
    queryFn: () => api.assistant.usage(currentProject?.id, 1),
    enabled: !!currentProject?.id,
  });

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: api.subscriptions.getMySubscription,
  });

  useEffect(() => {
    if (currentProject && messageStats) {
      const context = {
        project_name: currentProject.name,
        total_messages: messageStats?.data?.total_count || 0,
        unread_messages: messageStats?.data?.unread_count || 0,
      };
      setBusinessContext(context);

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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages]);

  const queryMutation = useMutation({
    mutationFn: (queryText) => {
      const conversationHistory = messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp?.toISOString(),
      }));

      return api.assistant.query({
        project_id: currentProject?.id,
        message: queryText,
        use_function_calling: true,
        context: {
          conversation_history: conversationHistory,
          project_name: currentProject?.name,
          total_messages: businessContext?.total_messages || 0,
          unread_messages: businessContext?.unread_messages || 0,
        },
      });
    },
    onSuccess: (response) => {
      const assistantMessage = {
        id: Date.now(),
        role: 'assistant',
        content: response.reply || response.data?.reply || 'Analysis completed.',
        tokens: response.tokens_used || response.data?.tokens_used,
        cost: response.cost || response.data?.cost,
        timestamp: new Date(),
        suggestions: generateContextualSuggestions(messages, businessContext, t) || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: `Operational notice: ${error.message}. Please retry query.`,
          timestamp: new Date(),
        },
      ]);
    },
  });

  const handleSend = () => {
    if (!input.trim() || !currentProject) return;
    const userMessage = { id: Date.now(), role: 'user', content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    queryMutation.mutate(input);
    setInput('');
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleQuickAction = (actionText) => {
    setInput(actionText);
    setTimeout(() => {
      setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: actionText, timestamp: new Date() }]);
      queryMutation.mutate(actionText);
      setInput('');
    }, 100);
  };

  if (!currentProject) {
    return <NoProjectState subtitle={t('assistant.subtitle') || 'Select a project to initiate conversational business automation'} />;
  }

  return (
    <div className="p-4 sm:p-6 h-[calc(100vh-4.5rem)] flex flex-col lg:flex-row gap-6 max-w-7xl mx-auto">
      {/* Interactive Chat Console */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="mb-4">
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <Sparkles className="w-6 h-6" />
            </span>
            {t('assistant.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('assistant.subtitle')}</p>
        </div>

        {/* Message Thread */}
        <GlassCard className="flex-1 p-4 sm:p-6 overflow-y-auto mb-4 space-y-4 rounded-2xl border border-border">
          {messages.map((message) => (
            <ChatMessageItem key={message.id} message={message} onQuickAction={handleQuickAction} />
          ))}

          {queryMutation.isPending && <ThinkingEngine />}
          <div ref={messagesEndRef} />
        </GlassCard>

        {/* Command Input Bar */}
        <GlassCard className="p-3.5 rounded-2xl border border-border">
          <div className="flex gap-2.5 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={t('assistant.placeholder') || 'Ask Automio to analyze sales trends, draft WhatsApp responses...'}
              className="flex-1 input-fluid resize-none text-sm py-2.5"
              rows={2}
              autoFocus
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || queryMutation.isPending}
              variant="primary"
              className="px-4 py-3"
              aria-label="Send query"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </GlassCard>
      </div>

      {/* Intelligence Telemetry Sidebar */}
      <AssistantSidebar
        businessContext={businessContext}
        dailyUsage={dailyUsage}
        subscription={subscription}
      />
    </div>
  );
}
