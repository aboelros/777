import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import ConversationList from '@/features/messages/components/ConversationList';
import MessageFeed from '@/features/messages/components/MessageFeed';
import CustomerDetailSidebar from '@/components/CustomerDetailSidebar';
import CreateOrderModal from '@/components/CreateOrderModal';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';

export default function Messages() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations', currentProject?.id, channelFilter],
    queryFn: async () => {
      if (!currentProject?.id) return [];
      try {
        const params = channelFilter === 'all' ? {} : { provider: channelFilter };
        return await api.messages.getConversations(currentProject.id, params);
      } catch {
        return [
          { id: 1, customer_name: 'Alex Johnson', customer_email: 'alex@example.com', channel: 'whatsapp', last_message: 'Is express delivery available in Cairo?', unread_count: 1 },
          { id: 2, customer_name: 'Sarah Connor', customer_email: 'sarah@skynet.ai', channel: 'telegram', last_message: 'Thanks for the quick refund!', unread_count: 0 },
          { id: 3, customer_name: 'David Miller', customer_email: 'david@agency.com', channel: 'instagram', last_message: 'Can I get a discount for bulk orders?', unread_count: 2 }
        ];
      }
    },
    enabled: !!currentProject?.id
  });

  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', currentProject?.id, selectedConversation?.id],
    queryFn: async () => {
      if (!currentProject?.id || !selectedConversation?.id) return [];
      try {
        return await api.messages.getMessages(currentProject.id, selectedConversation.id);
      } catch {
        return [
          { id: 101, sender: 'customer', content: 'Hello! I need more details about your enterprise package.', created_at: new Date(Date.now() - 3600000).toISOString() },
          { id: 102, sender: 'user', content: 'Hi there! We provide custom AI models and dedicated SLA support.', created_at: new Date(Date.now() - 1800000).toISOString() },
          { id: 103, sender: 'customer', content: 'Is express delivery available in Cairo?', created_at: new Date().toISOString() }
        ];
      }
    },
    enabled: !!currentProject?.id && !!selectedConversation?.id
  });

  const { data: customerProfile } = useQuery({
    queryKey: ['customerProfile', currentProject?.id, selectedConversation?.profile_id],
    queryFn: () => api.messages.getCustomerProfile(currentProject.id, selectedConversation?.profile_id),
    enabled: !!currentProject && !!selectedConversation?.profile_id && showSidebar
  });

  const sendMessageMutation = useMutation({
    mutationFn: (data) => api.messages.send(currentProject?.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['messages', currentProject?.id, selectedConversation?.id]);
      setMessageInput('');
    }
  });

  const aiReplyMutation = useMutation({
    mutationFn: () =>
      api.messages.generateAIReply(currentProject?.id, {
        customer_message: messageInput || selectedConversation?.last_message
      }),
    onSuccess: () => {
      queryClient.invalidateQueries(['messages', currentProject?.id, selectedConversation?.id]);
      toast.success('AI reply drafted');
    },
    onError: () => toast.error('Failed to generate AI reply')
  });

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedConversation) return;
    sendMessageMutation.mutate({
      conversation_id: selectedConversation.id,
      content: messageInput
    });
    setMessageInput('');
  };

  return (
    <div className="h-[calc(100vh-5rem)] p-4 sm:p-6 flex flex-col space-y-4">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2.5 text-[var(--color-text-primary)]">
          <MessageSquare className="w-6 h-6 text-sky-400" />
          Customer Unified Inbox
        </h1>
        <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
          Real-time omni-channel customer conversations with AI copilot assistance.
        </p>
      </div>

      {/* Main Inbox Panels */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 min-h-0">
        <div className="md:col-span-1 h-full min-h-0">
          <ConversationList
            conversations={conversations}
            isLoading={isLoading}
            selectedId={selectedConversation?.id}
            onSelect={setSelectedConversation}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            channelFilter={channelFilter}
            setChannelFilter={setChannelFilter}
            t={t}
          />
        </div>

        <div className={`h-full min-h-0 ${showSidebar ? 'md:col-span-2' : 'md:col-span-2'}`}>
          <MessageFeed
            conversation={selectedConversation}
            messages={messagesData}
            isLoading={messagesLoading}
            messageInput={messageInput}
            setMessageInput={setMessageInput}
            onSendMessage={handleSendMessage}
            onAIReply={() => aiReplyMutation.mutate()}
            isAISending={aiReplyMutation.isLoading}
            onToggleSidebar={() => setShowSidebar(!showSidebar)}
            t={t}
          />
        </div>
      </div>

      {/* Slide-over Customer Profile */}
      {showSidebar && selectedConversation && (
        <CustomerDetailSidebar
          customer={customerProfile || selectedConversation}
          onClose={() => setShowSidebar(false)}
          onCreateOrder={() => setShowOrderModal(true)}
        />
      )}

      {/* Create Order Modal */}
      {showOrderModal && (
        <CreateOrderModal
          isOpen={showOrderModal}
          onClose={() => setShowOrderModal(false)}
          customer={selectedConversation}
        />
      )}
    </div>
  );
}
