import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Sparkles, MessageSquare, ThumbsUp, Calendar, ExternalLink } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../services/api';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

export default function PostDetailDrawer({ isOpen, onClose, post, projectId }) {
    const [replyText, setReplyText] = useState('');
    const [generatingFor, setGeneratingFor] = useState(null);
    const queryClient = useQueryClient();
    const { t } = useTranslation();

    // Send response mutation
    const sendMutation = useMutation({
        mutationFn: ({ commentId, text }) =>
            api.socialMedia.sendResponse(projectId, commentId, text),
        onSuccess: () => {
            queryClient.invalidateQueries(['social-feed']);
            queryClient.invalidateQueries(['social-comments']);
            setReplyText('');
            toast.success('Response sent successfully!');
        },
        onError: (error) => {
            toast.error(error.message || 'Failed to send response');
        },
    });

    // Generate response mutation
    const generateMutation = useMutation({
        mutationFn: async (commentId) => {
            setGeneratingFor(commentId);
            return api.socialMedia.generateResponse(projectId, commentId);
        },
        onSuccess: (data) => {
            toast.success('Response generated!');
            setGeneratingFor(null);
            const response = data.generated_response;
            if (confirm(`Generated: ${response}\n\nSend now?`)) {
                sendMutation.mutate({ commentId: data.comment_id, text: response });
            }
        },
        onError: (error) => {
            setGeneratingFor(null);
            toast.error('Failed to generate response');
        },
    });

    if (!isOpen || !post) return null;

    const comments = post.comments || [];


    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Drawer */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed inset-y-0 right-0 w-full md:w-[800px] bg-dark-900 border-l border-white/10 shadow-2xl z-50 flex flex-col"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-white/10 flex items-center justify-between">
                            <h2 className="text-xl font-bold flex items-center gap-2">
                                <MessageSquare className="w-5 h-5 text-sky-400" />
                                {t('social.drawer.title')}
                            </h2>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-400" />
                            </button>
                        </div>

                        {/* Content Body */}
                        <div className="flex-1 overflow-y-auto p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">

                                {/* Left Col: Post Content */}
                                <div className="space-y-6">
                                    <div className="rounded-xl overflow-hidden border border-white/10 bg-dark-800/50">
                                        {post.full_picture ? (
                                            <img
                                                src={post.full_picture}
                                                alt="Post media"
                                                className="w-full h-auto object-contain max-h-[400px] bg-black"
                                            />
                                        ) : (
                                            <div className="w-full h-48 bg-dark-800 flex items-center justify-center text-gray-500">
                                                {t('social.drawer.no_media')}
                                            </div>
                                        )}
                                        <div className="p-4">
                                            <div className="flex items-center justify-between mb-3 text-sm text-gray-400">
                                                <span className="flex items-center gap-1">
                                                    <Calendar className="w-4 h-4" />
                                                    {post.created_time ? new Date(post.created_time).toLocaleDateString() : 'Recent'}
                                                </span>
                                                <a
                                                    href={post.permalink_url}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="flex items-center gap-1 hover:text-sky-400 transition-colors"
                                                >
                                                    {t('social.drawer.view_original')} <ExternalLink className="w-3 h-3" />
                                                </a>
                                            </div>
                                            <p className="text-gray-200 whitespace-pre-wrap">{post.message || post.caption || "No caption"}</p>
                                        </div>
                                    </div>

                                    {/* Stats */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="glass-card p-4 rounded-lg flex items-center gap-3">
                                            <ThumbsUp className="w-5 h-5 text-blue-400" />
                                            <div>
                                                <p className="text-sm text-gray-400">{t('social.drawer.likes')}</p>
                                                <p className="text-xl font-bold">{post.likes_count || 0}</p>
                                            </div>
                                        </div>
                                        <div className="glass-card p-4 rounded-lg flex items-center gap-3">
                                            <MessageSquare className="w-5 h-5 text-sky-400" />
                                            <div>
                                                <p className="text-sm text-gray-400">{t('social.drawer.comments')}</p>
                                                <p className="text-xl font-bold">{post.comments_count || 0}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Right Col: Comment Thread */}
                                <div className="flex flex-col h-full bg-dark-800/30 rounded-xl border border-white/5 overflow-hidden">
                                    <div className="p-4 border-b border-white/5 bg-white/5">
                                        <h3 className="font-semibold">{t('social.drawer.thread')}</h3>
                                    </div>

                                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                                        {/* Placeholder for fetching specific comments for this post if not already in 'post' object */}
                                        {/* For now, checking if 'comments' array exists on post, or we rely on the main comments list passed down */}
                                        {(!comments || comments.length === 0) ? (
                                            <div className="text-center py-10 text-gray-500">
                                                <MessageSquare className="w-10 h-10 mx-auto mb-2 opacity-20" />
                                                <p>{t('social.drawer.no_thread')}</p>
                                            </div>
                                        ) : (
                                            comments.map((comment) => (
                                                <div key={comment.id} className="glass-card p-3 rounded-lg border border-white/5">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <span className="font-medium text-sky-300">{comment.author_username || "User"}</span>
                                                        <span className="text-xs text-gray-500">
                                                            {comment.created_at ? new Date(comment.created_at).toLocaleDateString() : ''}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-300 mb-3">{comment.content}</p>

                                                    {comment.response_content && (
                                                        <div className="bg-green-500/10 border border-green-500/20 p-2 rounded text-xs text-green-300 mb-2">
                                                            {comment.response_content}
                                                        </div>
                                                    )}

                                                    {!comment.responded && (
                                                        <button
                                                            onClick={() => generateMutation.mutate(comment.id)}
                                                            disabled={generatingFor === comment.id}
                                                            className="text-xs flex items-center gap-1 text-sky-400 hover:text-sky-300 transition-colors"
                                                        >
                                                            <Sparkles className="w-3 h-3" />
                                                            {generatingFor === comment.id ? t('social.drawer.thinking') : t('social.drawer.generate_reply')}
                                                        </button>
                                                    )}
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>

                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
