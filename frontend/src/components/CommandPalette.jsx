import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Command,
    LayoutDashboard,
    MessageSquare,
    ShoppingBag,
    Users,
    BarChart,
    Settings,
    Bot,
    Box,
    FileText,
    CreditCard,
    LogOut,
    X
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useProjectStore } from '../store/projectStore';
import { cn } from '../lib/utils';

// Mock data for search - in a real app, this would be dynamic
const SEARCH_GROUPS = [
    {
        name: 'Pages',
        items: [
            { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, path: '/' },
            { id: 'messages', name: 'Messages', icon: MessageSquare, path: '/messages' },
            { id: 'orders', name: 'Orders', icon: ShoppingBag, path: '/orders' },
            { id: 'products', name: 'Products', icon: Box, path: '/products' },
            { id: 'reports', name: 'Reports', icon: BarChart, path: '/reports' },
            { id: 'settings', name: 'Settings', icon: Settings, path: '/settings' },
        ]
    },
    {
        name: 'AI Tools',
        items: [
            { id: 'assistant', name: 'AI Assistant', icon: Bot, path: '/assistant' },
            { id: 'training', name: 'Bot Training', icon: FileText, path: '/bot-training' },
        ]
    },
    {
        name: 'Account',
        items: [
            { id: 'subscription', name: 'Subscription', icon: CreditCard, path: '/subscription' },
            { id: 'logout', name: 'Log Out', icon: LogOut, action: 'logout' },
        ]
    }
];

export default function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const navigate = useNavigate();
    const inputRef = useRef(null);
    const { logout } = useAuthStore();
    const { currentProject } = useProjectStore();

    // Toggle with Ctrl+K
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                setIsOpen((prev) => !prev);
            }

            // Close on Escape
            if (e.key === 'Escape') {
                setIsOpen(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    // Filter items based on query
    const filteredGroups = query === ''
        ? SEARCH_GROUPS
        : SEARCH_GROUPS.map(group => ({
            ...group,
            items: group.items.filter(item =>
                item.name.toLowerCase().includes(query.toLowerCase())
            )
        })).filter(group => group.items.length > 0);

    // Flatten items for keyboard navigation
    const flatItems = filteredGroups.flatMap(group => group.items);

    // Reset selection when query changes
    useEffect(() => {
        setSelectedIndex(0);
    }, [query]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen && inputRef.current) {
            setTimeout(() => inputRef.current.focus(), 10);
        }
    }, [isOpen]);

    // Handle keyboard navigation within the list
    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => (prev + 1) % flatItems.length);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => (prev - 1 + flatItems.length) % flatItems.length);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (flatItems.length > 0) {
                handleSelect(flatItems[selectedIndex]);
            }
        }
    };

    const handleSelect = (item) => {
        if (item.path) {
            navigate(item.path);
        } else if (item.action === 'logout') {
            logout();
        }
        setIsOpen(false);
        setQuery('');
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] px-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsOpen(false)}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ duration: 0.2 }}
                        className="relative w-full max-w-lg overflow-hidden rounded-xl bg-dark-900/90 border border-white/10 shadow-2xl backdrop-blur-xl ring-1 ring-white/10"
                    >
                        {/* Search Input */}
                        <div className="flex items-center border-b border-white/10 px-4">
                            <Search className="w-5 h-5 text-gray-400 mr-3" />
                            <input
                                ref={inputRef}
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type a command or search..."
                                className="flex-1 h-12 bg-transparent border-none outline-none text-white placeholder-gray-400 text-lg"
                            />
                            <div className="flex items-center gap-1 text-xs text-gray-500 font-mono border border-white/10 rounded px-1.5 py-0.5">
                                <span>ESC</span>
                            </div>
                        </div>

                        {/* Results List */}
                        <div className="max-h-[60vh] overflow-y-auto py-2">
                            {flatItems.length === 0 ? (
                                <div className="px-4 py-8 text-center text-gray-500">
                                    <p>No results found.</p>
                                </div>
                            ) : (
                                filteredGroups.map((group, groupIndex) => (
                                    <div key={group.name} className="mb-2 last:mb-0">
                                        <div className="px-4 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                            {group.name}
                                        </div>
                                        {group.items.map((item) => {
                                            // Calculate global index for selection highlighting
                                            const itemIndex = flatItems.indexOf(item);
                                            const isSelected = itemIndex === selectedIndex;

                                            return (
                                                <div
                                                    key={item.id}
                                                    onClick={() => handleSelect(item)}
                                                    onMouseEnter={() => setSelectedIndex(itemIndex)}
                                                    className={`
                            mx-2 px-3 py-2.5 rounded-lg flex items-center justify-between cursor-pointer transition-colors
                            ${isSelected ? 'bg-accent-500/20 text-accent-100' : 'text-gray-300 hover:bg-white/5'}
                          `}
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <item.icon className={`w-5 h-5 ${isSelected ? 'text-accent-400' : 'text-gray-500'}`} />
                                                        <span className={isSelected ? 'font-medium' : ''}>{item.name}</span>
                                                    </div>
                                                    {isSelected && (
                                                        <motion.span
                                                            layoutId="enter-icon"
                                                            className="text-xs text-accent-400 font-mono"
                                                        >
                                                            ↵
                                                        </motion.span>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Footer */}
                        <div className="px-4 py-2 border-t border-white/10 bg-white/5 flex items-center justify-between text-xs text-gray-500">
                            <div className="flex gap-4">
                                <span><strong className="text-gray-400">↑↓</strong> to navigate</span>
                                <span><strong className="text-gray-400">↵</strong> to select</span>
                            </div>
                            {currentProject && (
                                <span className="opacity-70">Project: {currentProject.name}</span>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
