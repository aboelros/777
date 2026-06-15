import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Shield } from 'lucide-react';

const ROLE_HIERARCHY = {
    owner: 3,
    moderator: 2,
    worker: 1
};

export default function PermissionGate({
    children,
    requiredRole = 'worker',
    fallback = null,
    showLock = false
}) {
    const { currentProject } = useProjectStore();

    // Find current user's role in this project (mock logic for now, should come from store/API)
    // In a real app, you'd get this from useAuthStore or useProjectStore
    // For now, assuming user has 'owner' role if not specified
    // TODO: Connect this to actual member role from project context
    const userRole = currentProject?.role || 'owner';

    const hasPermission = ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[requiredRole];

    if (!hasPermission) {
        if (showLock) {
            return (
                <div className="flex flex-col items-center justify-center p-8 text-center text-gray-500 bg-white/5 rounded-xl border border-white/5 border-dashed">
                    <Shield className="w-8 h-8 mb-2 opacity-50" />
                    <p className="text-sm font-medium">Access Restricted</p>
                    <p className="text-xs">You need to be a {requiredRole} to view this.</p>
                </div>
            );
        }
        return fallback;
    }

    return children;
}
