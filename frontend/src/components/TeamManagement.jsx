import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, Shield, Trash2, MoreVertical, X, Check, Loader2 } from 'lucide-react';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { toast } from 'sonner';
import Button from './Button';

const ROLES = {
    owner: { label: 'Owner', color: 'text-cyan-400', badge: 'bg-cyan-400/10 border-cyan-400/20' },
    moderator: { label: 'Moderator', color: 'text-blue-400', badge: 'bg-blue-400/10 border-blue-400/20' },
    worker: { label: 'Worker', color: 'text-gray-400', badge: 'bg-gray-400/10 border-gray-400/20' }
};

export default function TeamManagement() {
    const { currentProject } = useProjectStore();
    const queryClient = useQueryClient();
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState('worker');

    // Fetch Members
    const { data: members, isLoading } = useQuery({
        queryKey: ['project-members', currentProject?.id],
        queryFn: () => api.projects.listMembers(currentProject?.id),
        enabled: !!currentProject?.id,
    });

    // Invite Member
    const inviteMutation = useMutation({
        mutationFn: (data) => api.projects.addMember(currentProject?.id, data.email, data.role),
        onSuccess: () => {
            queryClient.invalidateQueries(['project-members']);
            setShowInviteModal(false);
            setInviteEmail('');
            toast.success('Member added successfully');
        },
        onError: (error) => toast.error(error.message)
    });

    // Remove Member
    const removeMutation = useMutation({
        mutationFn: (userId) => api.projects.removeMember(currentProject?.id, userId),
        onSuccess: () => {
            queryClient.invalidateQueries(['project-members']);
            toast.success('Member removed');
        },
        onError: (error) => toast.error(error.message)
    });

    // Update Role
    const updateRoleMutation = useMutation({
        mutationFn: ({ userId, role }) => projects.updateMemberRole(currentProject?.id, userId, role),
        onSuccess: () => {
            queryClient.invalidateQueries(['project-members']);
            toast.success('Role updated');
        },
        onError: (error) => toast.error(error.message)
    });

    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin text-accent-500" /></div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold text-white ">Team Members</h2>
                    <p className="text-gray-400 text-sm">Manage access and roles for your project.</p>
                </div>
                <Button
                    variant="primary"
                    leftIcon={UserPlus}
                    onClick={() => setShowInviteModal(true)}
                >
                    Invite Member
                </Button>
            </div>

            <div className="glass-panel p-1">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <th className="px-6 py-4">User</th>
                            <th className="px-6 py-4">Role</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {members?.map((member) => (
                            <tr key={member.user_id} className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-cyan-600 flex items-center justify-center text-xs font-bold text-black border border-white/20">
                                            {member.name?.[0] || member.email[0]}
                                        </div>
                                        <div>
                                            <div className="font-medium text-white">{member.name || 'Unknown'}</div>
                                            <div className="text-sm text-gray-500">{member.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <select
                                        value={member.role}
                                        onChange={(e) => updateRoleMutation.mutate({ userId: member.user_id, role: e.target.value })}
                                        className={`text-xs px-2 py-1 rounded-md border ${ROLES[member.role]?.badge || ROLES.worker.badge} ${ROLES[member.role]?.color || ROLES.worker.color} bg-transparent outline-none cursor-pointer hover:bg-white/5 disabled:opacity-50`}
                                        disabled={updateRoleMutation.isPending}
                                    >
                                        <option value="owner" className="bg-dark-900 text-cyan-400">Owner</option>
                                        <option value="moderator" className="bg-dark-900 text-blue-400">Moderator</option>
                                        <option value="worker" className="bg-dark-900 text-gray-400">Worker</option>
                                    </select>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => {
                                            if (confirm('Are you sure you want to remove this member?')) {
                                                removeMutation.mutate(member.user_id);
                                            }
                                        }}
                                        className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
                                        disabled={member.role === 'owner'}
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Invite Modal */}
            <AnimatePresence>
                {showInviteModal && (
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="glass-card w-full max-w-md p-6"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-bold text-white">Invite Team Member</h3>
                                <button onClick={() => setShowInviteModal(false)} className="text-gray-400 hover:text-white">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <form onSubmit={(e) => {
                                e.preventDefault();
                                inviteMutation.mutate({ email: inviteEmail, role: inviteRole });
                            }} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-400 mb-1">Email Address</label>
                                    <input
                                        type="email"
                                        value={inviteEmail}
                                        onChange={(e) => setInviteEmail(e.target.value)}
                                        placeholder="colleague@example.com"
                                        className="input-fluid"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-400 mb-1">Role</label>
                                    <div className="grid grid-cols-3 gap-3">
                                        {Object.entries(ROLES).map(([key, config]) => (
                                            <button
                                                key={key}
                                                type="button"
                                                onClick={() => setInviteRole(key)}
                                                className={`px-3 py-2 rounded-lg text-sm transition-all border ${inviteRole === key
                                                    ? 'bg-accent-500/20 border-accent-500 text-white shadow-neon-glow'
                                                    : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                                                    }`}
                                            >
                                                {config.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex gap-3 mt-6">
                                    <Button type="button" variant="ghost" className="flex-1" onClick={() => setShowInviteModal(false)}>
                                        Cancel
                                    </Button>
                                    <Button
                                        type="submit"
                                        variant="primary"
                                        className="flex-1"
                                        isLoading={inviteMutation.isPending}
                                    >
                                        Send Invite
                                    </Button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
