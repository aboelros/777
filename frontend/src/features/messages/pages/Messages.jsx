import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Send,
  Bot,
  User,
  Search,
  Filter,
  ChevronDown,
  Sparkles,
  Instagram,
  Facebook,
  Phone,
  MessageCircle,
  Clock,
  Check,
  CheckCheck,
  ShoppingCart,
  Globe,
  Trash2,
  Smile,
  Frown,
  Meh,
  AlertTriangle,
  MoreVertical,
  Paperclip,
  ChevronRight,
  Info
} from 'lucide-react';
import GlassCard from '../../../components/ui/GlassCard';
import CustomerDetailSidebar from '../../../components/CustomerDetailSidebar';
import CreateOrderModal from '../../../components/CreateOrderModal';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';
import { formatDateTime } from '../../../utils/helpers';
import { toast } from 'sonner';
import { cn } from '../../../lib/utils';
import Button from '../../../components/ui/Button';
import Input from '../../../components/ui/Input';
import ApiErrorState from '../../../components/ApiErrorState';
import SkeletonLoader from '../../../components/ui/SkeletonLoader';

const CHANNEL_ICONS = {
  whatsapp: MessageCircle,
  telegram: Send,
  instagram: Instagram,
  facebook: Facebook,
  sms: Phone,
  email: MessageSquare
};

const CHANNEL_COLORS = {
  whatsapp: 'text-green-400',
  telegram: 'text-blue-400',
  instagram: 'text-sky-400',
  facebook: 'text-indigo-400',
  sms: 'text-sky-400',
  email: 'text-gray-400'
};

function AvatarFallback({ name, avatar, className }) {
  const initials = name?.charAt(0).toUpperCase() || 'U';

  if (!avatar) {
    return (
      <div className={cn("w-full h-full flex items-center justify-center bg-white/5 text-gray-400", className)}>
        {initials}
      </div>
    );
  }

  return (
    <div className={cn("relative w-full h-full", className)}>
      <img
        src={avatar}
        alt={name}
        className="w-full h-full object-cover"
        onError={(e) => {
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'flex';
        }}
      />
      <div className="absolute inset-0 hidden items-center justify-center bg-white/5 text-gray-400 font-bold">
        {initials}
      </div>
    </div>
  );
}

export default function Messages() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [showAIOptions, setShowAIOptions] = useState(false);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch conversations
  const { data: conversations, isLoading, error: conversationsError, refetch: refetchConversations } = useQuery({
    queryKey: ['conversations', currentProject?.id, channelFilter],
    queryFn: () => {
      if (!currentProject?.id) return [];
      const params = channelFilter === 'all' ? {} : { provider: channelFilter };
      return api.messages.getConversations(currentProject.id, params);
    },
    enabled: !!currentProject?.id,
    retry: 1,
  });

  // Fetch conversation messages
  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', currentProject?.id, selectedConversation?.id],
    queryFn: () => {
      if (!currentProject?.id || !selectedConversation?.id) return [];
      const params = selectedConversation.channel
        ? { provider: selectedConversation.channel }
        : {};
      return api.messages.getMessages(
        currentProject.id,
        selectedConversation.id,
        params
      );
    },
    enabled: !!currentProject?.id && !!selectedConversation?.id,
    refetchInterval: 5000,
  });

  // Fetch full customer profile for sidebar
  const { data: customerProfile } = useQuery({
    queryKey: ['customerProfile', currentProject?.id, selectedConversation?.profile_id],
    queryFn: () => api.messages.getCustomerProfile(currentProject.id, selectedConversation.profile_id),
    enabled: !!currentProject && !!selectedConversation?.profile_id && showSidebar,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (data) => api.messages.send(currentProject?.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['messages', currentProject?.id, selectedConversation?.id]);
      setMessageInput('');
    },
  });

  // AI auto-reply mutation
  const aiReplyMutation = useMutation({
    mutationFn: ({ orderId, customerMessage }) =>
      api.messages.generateAIReply(currentProject?.id, {
        order_id: orderId,
        customer_message: customerMessage,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries(['messages', currentProject?.id, selectedConversation?.id]);
    },
    onError: (error) => {
      toast.error(t('common.error') + ': ' + (error.response?.data?.detail || error.message));
    },
  });

  // Mark conversation as read
  const markReadMutation = useMutation({
    mutationFn: (conversationId) => api.messages.markConversationRead(currentProject?.id, conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations', currentProject?.id]);
    },
    onError: (error) => {
      console.error("Failed to mark read:", error);
    },
  });

  // Toggle AI for individual customer
  const toggleAIMutation = useMutation({
    mutationFn: (profileId) => api.messages.toggleAI(currentProject?.id, profileId),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations', currentProject?.id]);
      queryClient.invalidateQueries(['customerProfile', currentProject?.id, selectedConversation?.profile_id]);
      toast.success(t('common.active'));
    },
    onError: (error) => {
      toast.error(t('common.error') + ': ' + (error.response?.data?.detail || error.message));
    }
  });

  // WebSocket for real-time messages
  useEffect(() => {
    if (!currentProject?.id) return;

    const API_URL = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');
    const wsBase = API_URL ? API_URL.replace('http', 'ws') : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;
    const wsUrl = `${wsBase}/ws/${currentProject.id}`;

    console.log('Connecting to WebSocket:', wsUrl);
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'new_message') {
          // Refresh conversations list
          queryClient.invalidateQueries(['conversations', currentProject.id]);

          // If the message is for the currently selected conversation, refresh its messages
          if (selectedConversation && (data.message.customer_id === selectedConversation.id || data.message.customer_id === selectedConversation.profile_id)) {
            queryClient.invalidateQueries(['messages', currentProject.id, selectedConversation.id]);
          }
        }
      } catch (err) {
        console.error('WebSocket message error:', err);
      }
    };

    socket.onerror = (err) => {
      console.error('WebSocket connection error');
    };

    return () => {
      socket.close();
    };
  }, [currentProject?.id, queryClient, selectedConversation]);

  // Clear conversation mutation
  const clearChatMutation = useMutation({
    mutationFn: (conversationId) => api.messages.clearConversation(currentProject?.id, conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries(['messages', currentProject?.id, selectedConversation?.id]);
      queryClient.invalidateQueries(['conversations', currentProject?.id]);
      toast.success(t('inbox.chat.clear_chat'));
    },
    onError: (error) => {
      toast.error(t('common.error') + ': ' + (error.response?.data?.detail || error.message));
    },
  });

  const handleClearChat = () => {
    if (!selectedConversation) return;
    if (window.confirm(t('common.delete_confirm'))) {
      clearChatMutation.mutate(selectedConversation.id);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedConversation) return;

    const recipient = selectedConversation.recipient && Object.keys(selectedConversation.recipient).length > 0
      ? selectedConversation.recipient
      : {
        customer_id: selectedConversation.customer_id,
        phone: selectedConversation.customer_phone,
        email: selectedConversation.customer_email,
      };

    // Normalize provider/channel to match backend Enum
    // We send the specific platform (like 'instagram') to the backend
    // even though the backend might store it as 'meta' provider.
    let provider = selectedConversation.channel || selectedConversation.provider;
    if (provider === 'meta') {
      // Fallback for generic meta - try to guess from customer metadata or default
      provider = 'facebook';
    }

    if (!['shopify', 'whatsapp', 'instagram', 'facebook', 'telegram', 'sms', 'tiktok'].includes(provider)) {
      provider = 'facebook'; // Default fallback
    }

    sendMessageMutation.mutate({
      content: messageInput,
      provider: provider,
      recipient,
      order_id: selectedConversation.order_id || null,
    }, {
      onError: (error) => {
        toast.error(t('common.error') + ': ' + (error.response?.data?.detail || error.message));
      }
    });
  };

  const handleAIReply = () => {
    if (!selectedConversation || !messagesData?.length) return;

    const latestInbound = [...messagesData]
      .reverse()
      .find((msg) => msg.direction === 'inbound');

    if (!latestInbound) return;

    aiReplyMutation.mutate({
      orderId: selectedConversation.order_id,
      customerMessage: latestInbound.content,
    });
  };

  const filteredConversations = conversations?.filter(conv =>
    searchQuery === '' ||
    conv.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.customer_email?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const getSentimentInfo = (sentiment) => {
    switch (sentiment) {
      case 'positive': return { icon: Smile, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/20' };
      case 'negative': return { icon: Frown, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' };
      case 'urgent': return { icon: AlertTriangle, color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', animate: 'animate-pulse' };
      case 'neutral': return { icon: Meh, color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/20' };
      default: return null;
    }
  };

  const handleConversationSelect = (convo) => {
    setSelectedConversation(convo);
    // Mark as read
    if (convo.unread_count > 0) {
      markReadMutation.mutate(convo.id);
    }
    // Clear input
    setMessageInput('');
  };

  return (
    <div className="h-full bg-[#050505] p-4 sm:p-6 lg:p-8 flex flex-col overflow-hidden relative">
      {/* Global Background Glow */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-accent-primary/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-[1800px] mx-auto w-full flex-1 flex flex-col min-h-0 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-gray-400 mb-2 flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-accent-primary to-accent-dark shadow-lg shadow-accent-primary/20">
              <MessageSquare className="w-6 h-6 text-black" />
            </div>
            {t('inbox.title')}
          </h1>
          <p className="text-gray-400 font-light tracking-wide max-w-2xl">
            {t('inbox.subtitle') || 'Manage omni-channel communications with AI-assisted intelligence.'}
          </p>
        </motion.div>

        <div className={`grid grid-cols-1 ${showSidebar && selectedConversation ? 'lg:grid-cols-4' : 'lg:grid-cols-3'} gap-6 flex-1 min-h-0 relative`}>
          {/* Conversations List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-1"
          >
            <GlassCard className="h-full flex flex-col border-white/5 bg-black/40 backdrop-blur-xl">
              {/* Search and Filter */}
              <div className="p-4 border-b border-white/10 space-y-4">
                <Input
                  icon={Search}
                  placeholder={t('inbox.search_placeholder')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  containerClassName="w-full"
                  className="bg-white/5 border-white/10 focus:border-accent-primary/30"
                />

                {/* Channel Filter */}
                <div className="flex flex-wrap gap-2">
                  {['all', 'whatsapp', 'telegram', 'instagram', 'facebook'].map((channel) => {
                    const IconComponent = CHANNEL_ICONS[channel] || MessageSquare;
                    const isActive = channelFilter === channel;

                    return (
                      <Button
                        key={channel}
                        onClick={() => setChannelFilter(channel)}
                        size="sm"
                        variant="ghost"
                        className={cn(
                          "transition-all border",
                          isActive
                            ? "bg-accent-primary/10 text-accent-primary border-accent-primary/20 shadow-[0_0_10px_rgba(14,165,233,0.1)]"
                            : "bg-transparent border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5 hover:border-white/5"
                        )}
                      >
                        <IconComponent className="w-3.5 h-3.5 mr-2" />
                        {channel === 'all' ? t('inbox.tabs.all') : channel.charAt(0).toUpperCase() + channel.slice(1)}
                      </Button>
                    );
                  })}
                </div>
              </div>

              {/* Conversations */}
              <div className="flex-1 overflow-y-auto custom-scrollbar">
                {isLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="animate-spin w-8 h-8 border-2 border-accent-primary/30 border-t-accent-primary rounded-full" />
                  </div>
                ) : filteredConversations.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500 p-4">
                    <div className="w-16 h-16 mb-4 rounded-2xl bg-white/5 flex items-center justify-center border border-white/5">
                      <MessageSquare className="w-8 h-8 opacity-20 text-white" />
                    </div>
                    <p className="text-sm font-medium">{t('inbox.empty.no_conversations')}</p>
                  </div>
                ) : (
                  <AnimatePresence>
                    {filteredConversations.map((conv) => {
                      const ChannelIcon = CHANNEL_ICONS[conv.channel] || MessageSquare;
                      const channelColor = CHANNEL_COLORS[conv.channel] || 'text-gray-400';
                      const isActive = selectedConversation?.id === conv.id;

                      return (
                        <motion.div
                          key={conv.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}
                          onClick={() => handleConversationSelect(conv)}
                          className={`p-4 border-b border-white/[0.05] cursor-pointer transition-all relative ${isActive
                            ? 'bg-gradient-to-r from-white/[0.08] to-transparent'
                            : ''
                            }`}
                        >
                          {isActive && (
                            <motion.div
                              layoutId="active-indicator"
                              className="absolute left-0 top-0 bottom-0 w-[2px] bg-accent-primary shadow-[0_0_15px_rgba(14,165,233,0.5)]"
                            />
                          )}
                          <div className="flex items-start gap-4">
                            <div className="relative">
                              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white text-lg font-bold shadow-lg overflow-hidden transition-all ${isActive ? 'ring-1 ring-accent-primary/50' : 'ring-1 ring-white/10'}`}>
                                <AvatarFallback name={conv.customer_name} avatar={conv.customer_avatar} />
                              </div>
                              <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-md bg-dark-950 border border-white/10 flex items-center justify-center`}>
                                <ChannelIcon className={`w-3 h-3 ${channelColor}`} />
                              </div>
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2 max-w-[70%]">
                                  <span className={`font-bold truncate text-sm ${isActive ? 'text-white' : 'text-gray-300'}`}>
                                    {conv.customer_name || t('social.accounts.unnamed')}
                                  </span>
                                  {conv.is_vip && (
                                    <div className="flex-shrink-0" title={t('inbox.chat.vip_customer')}>
                                      <Sparkles className="w-3 h-3 text-accent-primary fill-accent-primary" />
                                    </div>
                                  )}
                                  {conv.overall_sentiment && (
                                    <div
                                      className={cn(
                                        "w-1 h-1 rounded-full flex-shrink-0",
                                        conv.overall_sentiment === 'positive' ? 'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]' :
                                          conv.overall_sentiment === 'negative' ? 'bg-rose-500 shadow-[0_0_5px_rgba(244,63,94,0.5)]' :
                                            'bg-gray-500'
                                      )}
                                      title={`Sentiment: ${conv.overall_sentiment}`}
                                    />
                                  )}
                                </div>
                                <span className="text-[10px] text-gray-600 whitespace-nowrap font-mono">
                                  {formatDateTime(conv.last_message_at, 'relative')}
                                </span>
                              </div>
                              <div className="flex items-center justify-between mb-0.5">
                                <p className={`text-xs truncate ${conv.unread_count > 0 ? 'text-gray-200 font-medium' : 'text-gray-500'}`}>
                                  {conv.last_message}
                                </p>
                              </div>

                              <div className="flex items-center justify-between mt-2">
                                <span className="text-[9px] text-gray-600 font-mono opacity-50">
                                  ID: {conv.customer_id?.slice(0, 8)}...
                                </span>
                                <div className="flex items-center gap-2">
                                  {conv.unread_count > 0 && (
                                    <span className="px-1.5 py-0.5 bg-accent-primary text-black text-[10px] font-bold rounded shadow-[0_0_10px_rgba(14,165,233,0.4)]">
                                      {conv.unread_count}
                                    </span>
                                  )}
                                  {conv.ai_enabled && (
                                    <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-accent-primary bg-accent-primary/10 px-1.5 py-0.5 rounded border border-accent-primary/20">
                                      {t('inbox.chat.auto')}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </AnimatePresence>
                )}
              </div>
            </GlassCard>
          </motion.div>

          {/* Chat Window */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <GlassCard className="h-full flex flex-col border-white/5 bg-black/40 backdrop-blur-2xl shadow-2xl relative overflow-hidden group">
              {/* Background ambient glow */}
              <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent-primary/5 blur-[100px] pointer-events-none transition-opacity duration-1000 group-hover:opacity-100 opacity-50" />
              <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-accent-dark/5 blur-[100px] pointer-events-none" />

              {selectedConversation ? (
                <>
                  {/* Chat Header */}
                  <div className="p-5 border-b border-white/5 bg-white/[0.02] backdrop-blur-xl z-10 relative">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="relative">
                          <div className="w-12 h-12 rounded-xl border border-white/10 bg-[#050505] overflow-hidden flex items-center justify-center shadow-2xl">
                            <AvatarFallback
                              name={selectedConversation.customer_name}
                              avatar={selectedConversation.customer_avatar}
                            />
                          </div>
                          <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-md bg-[#050505] border border-white/10 flex items-center justify-center shadow-lg`}>
                            {/* Icon would go here but we use generic indicator for now */}
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center gap-3">
                            <h2 className="text-lg font-bold text-white leading-tight tracking-tight">
                              {selectedConversation.customer_name || t('social.accounts.unnamed')}
                            </h2>
                            {selectedConversation.overall_sentiment && (
                              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-white/5 bg-white/5">
                                <span className={cn(
                                  "w-1.5 h-1.5 rounded-full animate-pulse",
                                  selectedConversation.overall_sentiment === 'positive' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' :
                                    selectedConversation.overall_sentiment === 'negative' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' :
                                      'bg-slate-400'
                                )} />
                                <span className="text-[9px] font-bold tracking-widest text-gray-400 capitalize">
                                  {selectedConversation.overall_sentiment}
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-[10px] font-mono text-gray-600">
                              {selectedConversation.customer_id?.slice(0, 12)}...
                            </span>
                            <div className="h-3 w-[1px] bg-white/10" />
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">
                                {selectedConversation.channel}
                              </span>
                              {selectedConversation.ai_enabled ? (
                                <span className="flex items-center gap-1 text-[9px] text-accent-primary font-bold uppercase tracking-widest animate-pulse">
                                  <Bot className="w-3 h-3" /> {t('inbox.chat.auto')}
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-[9px] text-gray-600 font-bold uppercase tracking-widest">
                                  <User className="w-3 h-3" /> {t('inbox.chat.manual')}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          onClick={() => setShowSidebar(!showSidebar)}
                          variant="ghost"
                          size="icon"
                          className={cn(
                            "w-10 h-10 rounded-lg border border-white/5 hover:bg-white/5 text-gray-400 hover:text-white transition-all",
                            showSidebar && "bg-accent-primary/10 text-accent-primary border-accent-primary/20"
                          )}
                          title="Customer Intelligence"
                        >
                          <Info className="w-5 h-5" />
                        </Button>

                        <div className="h-10 w-[1px] bg-white/10 mx-2" />

                        <Button
                          onClick={() => toggleAIMutation.mutate(selectedConversation.profile_id || selectedConversation.id)}
                          variant="secondary"
                          className={`
                            border border-white/10 bg-white/5 hover:bg-white/10 text-xs font-bold uppercase tracking-widest
                            ${selectedConversation.ai_enabled ? 'text-accent-primary border-accent-primary/20 shadow-[0_0_15px_rgba(14,165,233,0.1)]' : 'text-gray-400'}
                          `}
                        >
                          {selectedConversation.ai_enabled ? t('inbox.chat.disable_ai') : t('inbox.chat.enable_ai')}
                        </Button>

                        <Button
                          onClick={handleAIReply}
                          disabled={aiReplyMutation.isLoading}
                          variant="primary"
                          className="bg-gradient-to-r from-accent-primary to-accent-dark hover:shadow-[0_0_20px_rgba(14,165,233,0.3)] text-black border-none font-bold tracking-wide"
                          isLoading={aiReplyMutation.isLoading}
                          leftIcon={Sparkles}
                        >
                          {t('inbox.chat.ai_assistant')}
                        </Button>

                        <Button
                          onClick={handleClearChat}
                          disabled={clearChatMutation.isLoading || !selectedConversation}
                          variant="ghost"
                          className="w-10 h-10 p-0 rounded-lg border border-white/5 hover:bg-red-500/10 hover:border-red-500/20 text-gray-500 hover:text-red-400"
                          isLoading={clearChatMutation.isLoading}
                        >
                          <Trash2 className="w-5 h-5" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar scroll-smooth relative z-10">
                    <AnimatePresence>
                      {messagesLoading ? (
                        <div className="flex items-center justify-center py-20">
                          <div className="flex gap-1.5">
                            {[0, 1, 2].map((i) => (
                              <motion.div
                                key={i}
                                animate={{ y: [0, -6, 0] }}
                                transition={{ repeat: Infinity, duration: 0.6, delay: i * 0.1 }}
                                className="w-2 h-2 rounded-full bg-accent-primary"
                              />
                            ))}
                          </div>
                        </div>
                      ) : (
                        messagesData?.map((msg, index) => {
                          const isOutbound = msg.direction === 'outbound';
                          const isAI = msg.ai_generated;

                          return (
                            <motion.div
                              key={msg.id}
                              initial={{ opacity: 0, y: 10, scale: 0.95 }}
                              animate={{ opacity: 1, y: 0, scale: 1 }}
                              className={`flex w-full ${isOutbound ? 'justify-end' : 'justify-start'}`}
                            >
                              {(msg.content_type === 'event_order' || msg.content_type === 'event_customer' || msg.content.startsWith('System Event:')) ? (
                                <div className="w-full flex justify-center my-6">
                                  <div className="bg-accent-primary/5 border border-accent-primary/20 px-5 py-2.5 rounded-2xl text-[10px] font-bold uppercase tracking-widest text-accent-primary flex items-center gap-3 backdrop-blur-md shadow-[0_0_15px_rgba(14,165,233,0.1)]">
                                    <div className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" />
                                    {msg.content.replace('System Event:', t('inbox.chat.system_event') + ':').trim()}
                                  </div>
                                </div>
                              ) : (
                                <div className={`flex flex-col max-w-[75%] ${isOutbound ? 'items-end' : 'items-start'}`}>
                                  <div className={`flex items-center gap-2 mb-1.5 px-2`}>
                                    {!isOutbound && (
                                      <span className="text-[10px] font-bold uppercase tracking-tighter text-gray-500">
                                        {selectedConversation.customer_name || t('social.accounts.unnamed')}
                                      </span>
                                    )}
                                    {isOutbound && (
                                      <span className={`text-[10px] font-bold uppercase tracking-tighter ${isAI ? 'text-accent-primary flex items-center gap-1' : 'text-gray-500'}`}>
                                        {isAI && <Bot className="w-3 h-3" />}
                                        {isAI ? t('inbox.chat.ai_assistant') : t('common.save')}
                                      </span>
                                    )}
                                  </div>

                                  <div
                                    className={`relative p-5 rounded-2xl text-[15px] leading-relaxed shadow-xl border backdrop-blur-md ${isOutbound
                                      ? isAI
                                        ? 'bg-gradient-to-br from-[#1a1500] to-[#050505] border-accent-primary/30 text-white rounded-se-none shadow-[0_4px_20px_rgba(0,0,0,0.5)]'
                                        : 'bg-[#111] border-white/10 text-gray-200 rounded-se-none'
                                      : 'bg-white/[0.03] border-white/5 text-gray-100 rounded-ss-none shadow-black/20'
                                      }`}
                                  >
                                    <p className="break-words select-text font-light tracking-wide text-start">{msg.content}</p>

                                    {/* Metallic Sheen for AI messages */}
                                    {isAI && (
                                      <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-accent-primary/40 to-transparent opacity-50" />
                                    )}
                                  </div>

                                  <div className={`flex items-center gap-2 mt-2 px-1`}>
                                    <span className="text-[10px] font-medium text-gray-600 font-mono">
                                      {formatDateTime(msg.created_at, 'time')}
                                    </span>

                                    {/* Sentiment Badge */}
                                    {msg.extra_data?.sentiment && (
                                      (() => {
                                        const sent = getSentimentInfo(msg.extra_data.sentiment);
                                        if (!sent) return null;
                                        return (
                                          <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md border ${sent.bg} ${sent.border} ${sent.animate || ''}`}>
                                            <sent.icon className={`w-3 h-3 ${sent.color}`} />
                                            <span className={`text-[9px] font-bold uppercase tracking-wider ${sent.color}`}>
                                              {msg.extra_data.sentiment}
                                            </span>
                                          </div>
                                        );
                                      })()
                                    )}

                                    {isOutbound && (
                                      <div className="flex items-center">
                                        {msg.status === 'sent' ? (
                                          <CheckCheck className="w-3.5 h-3.5 text-accent-primary shadow-[0_0_5px_rgba(14,165,233,0.5)]" />
                                        ) : (
                                          <Clock className="w-3.5 h-3.5 text-gray-600" />
                                        )}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </motion.div>
                          );
                        })
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Message Input Area */}
                  <div className="p-6 border-t border-white/5 bg-[#050505]/80 backdrop-blur-2xl z-10">
                    <form onSubmit={handleSendMessage} className="flex gap-4 items-end max-w-5xl mx-auto w-full">
                      <div className="flex-1 relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-accent-primary/5 to-accent-dark/5 rounded-2xl blur-lg transition-opacity opacity-0 group-focus-within:opacity-100" />
                        <textarea
                          value={messageInput}
                          onChange={(e) => setMessageInput(e.target.value)}
                          placeholder={t('inbox.chat.input_placeholder')}
                          rows={1}
                          className="relative w-full px-5 py-4 bg-white/[0.03] border border-white/10 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-accent-primary/30 focus:border-accent-primary/30 transition-all resize-none shadow-inner"
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                              e.preventDefault();
                              handleSendMessage(e);
                            }
                          }}
                        />
                      </div>

                      <motion.button
                        type="submit"
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={!messageInput.trim() || sendMessageMutation.isLoading}
                        className="p-4 bg-gradient-to-br from-accent-primary to-[#AA771C] text-black rounded-2xl shadow-lg shadow-accent-primary/20 hover:shadow-accent-primary/40 transition-all disabled:opacity-50 disabled:grayscale"
                      >
                        {sendMessageMutation.isLoading ? (
                          <div className="animate-spin w-6 h-6 border-3 border-black/50 border-t-black rounded-full" />
                        ) : (
                          <Send className="w-6 h-6" />
                        )}
                      </motion.button>
                    </form>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-gray-500 space-y-6">
                  <motion.div
                    animate={{
                      y: [0, -10, 0],
                      scale: [1, 1.05, 1],
                      filter: ["drop-shadow(0 0 0px rgba(14,165,233,0))", "drop-shadow(0 0 20px rgba(14,165,233,0.2))", "drop-shadow(0 0 0px rgba(14,165,233,0))"]
                    }}
                    transition={{ repeat: Infinity, duration: 4 }}
                    className="w-24 h-24 rounded-3xl bg-[#0A0A0A] flex items-center justify-center border border-accent-primary/20 shadow-lg group-hover:border-accent-primary/40 transition-colors"
                  >
                    <MessageSquare className="w-12 h-12 text-accent-primary opacity-50" />
                  </motion.div>
                  <div className="text-center space-y-2">
                    <p className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-500">
                      {t('inbox.empty.select')}
                    </p>
                    <p className="text-sm font-light tracking-wide max-w-xs mx-auto">
                      {t('inbox.empty.select_desc')}
                    </p>
                  </div>
                </div>
              )}
            </GlassCard>
          </motion.div>

          {/* Customer Detail Sidebar */}
          <AnimatePresence>
            {showSidebar && selectedConversation && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="lg:col-span-1 h-full"
              >
                <GlassCard className="h-full p-0 overflow-hidden border-white/5 bg-white/[0.01] shadow-2xl">
                  <CustomerDetailSidebar
                    customer={customerProfile || selectedConversation}
                    onClose={() => setShowSidebar(false)}
                    onToggleAI={() => toggleAIMutation.mutate(selectedConversation.profile_id || selectedConversation.id)}
                  />
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Order Creation Modal */}
        <CreateOrderModal
          isOpen={showOrderModal}
          onClose={() => setShowOrderModal(false)}
          customer={{
            id: selectedConversation?.profile_id,
            name: selectedConversation?.customer_name,
            email: selectedConversation?.customer_email,
          }}
        />
      </div>

      {/* Custom Global Styles for scrollbar */}
      <style dangerouslySetInnerHTML={{
        __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}} />
    </div >
  );
}
