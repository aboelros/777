/**
 * Event Monitor Dashboard
 * Real-time monitoring of event bus activity and worker status.
 */
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, AlertCircle, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function EventMonitor() {
    const [stats, setStats] = useState({
        eventsProcessed: 0,
        eventsPerSecond: 0,
        pendingEvents: 0,
        failedEvents: 0,
        workers: 0,
        avgProcessingTime: 0
    });

    const [recentEvents, setRecentEvents] = useState([]);
    const [workerStatus, setWorkerStatus] = useState([]);

    useEffect(() => {
        // TODO: Fetch real-time stats from API
        const interval = setInterval(() => {
            // Simulate real-time updates
            setStats(prev => ({
                ...prev,
                eventsProcessed: prev.eventsProcessed + Math.floor(Math.random() * 10),
                eventsPerSecond: Math.floor(Math.random() * 50)
            }));
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                    <Activity className="w-10 h-10 text-purple-400" />
                    Event Bus Monitor
                </h1>
                <p className="text-gray-400">Real-time event processing and worker status</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Events Processed</span>
                            <CheckCircle className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="text-3xl font-bold">{stats.eventsProcessed.toLocaleString()}</div>
                        <div className="text-xs text-gray-500 mt-1">Total lifetime</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Events/Second</span>
                            <Zap className="w-5 h-5 text-yellow-400" />
                        </div>
                        <div className="text-3xl font-bold">{stats.eventsPerSecond}</div>
                        <div className="text-xs text-gray-500 mt-1">Current throughput</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Pending</span>
                            <Clock className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="text-3xl font-bold">{stats.pendingEvents}</div>
                        <div className="text-xs text-gray-500 mt-1">In queue</div>
                    </div>
                </GlassCard>

                <GlassCard>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Failed</span>
                            <AlertCircle className="w-5 h-5 text-red-400" />
                        </div>
                        <div className="text-3xl font-bold">{stats.failedEvents}</div>
                        <div className="text-xs text-gray-500 mt-1">In DLQ</div>
                    </div>
                </GlassCard>
            </div>

            {/* Recent Events */}
            <GlassCard>
                <div className="p-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-purple-400" />
                        Recent Events
                    </h2>

                    <div className="space-y-2">
                        {[1, 2, 3, 4, 5].map((i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="flex items-center justify-between p-3 bg-dark-800/30 rounded-lg"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-2 h-2 rounded-full bg-green-400"></div>
                                    <div>
                                        <div className="font-medium">orders.created</div>
                                        <div className="text-xs text-gray-400">Order #12345 created</div>
                                    </div>
                                </div>
                                <div className="text-xs text-gray-500">2s ago</div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </GlassCard>

            {/* Worker Status */}
            <GlassCard>
                <div className="p-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-400" />
                        Worker Status
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {[
                            { name: 'AI Worker', status: 'active', tasks: 12 },
                            { name: 'Analytics Worker', status: 'active', tasks: 5 },
                            { name: 'Social Worker', status: 'idle', tasks: 0 },
                            { name: 'Integration Worker', status: 'active', tasks: 8 }
                        ].map((worker, i) => (
                            <div key={i} className="p-4 bg-dark-800/30 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium">{worker.name}</span>
                                    <span className={`text-xs px-2 py-1 rounded ${worker.status === 'active'
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-gray-500/20 text-gray-400'
                                        }`}>
                                        {worker.status}
                                    </span>
                                </div>
                                <div className="text-sm text-gray-400">
                                    {worker.tasks} tasks processing
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </GlassCard>
        </div>
    );
}
