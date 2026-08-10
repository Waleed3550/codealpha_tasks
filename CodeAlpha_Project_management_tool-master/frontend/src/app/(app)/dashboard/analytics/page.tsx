'use client';
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';
import api from '@/lib/api';

export default function AnalyticsPage() {
    const [data, setData] = useState<any>(null);
    
    useEffect(() => {
        api.get('/dashboard/').then(res => setData(res.data)).catch(console.error);
    }, []);

    const completionRate = data?.task_count ? Math.round((data.completed_tasks / data.task_count) * 100) : 0;

    return (
        <div className="max-w-7xl mx-auto space-y-6 pb-12">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Project Analytics</h1>
                    <p className="text-slate-400 mt-1">Real-time velocity and productivity metrics.</p>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-lg transition-colors border border-white/5">
                        Last 7 Days
                    </button>
                    <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-emerald-500/20 flex items-center gap-2">
                        <BarChart3 size={16} /> Export PDF
                    </button>
                </div>
            </div>

            {/* Top Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Total Projects" value={data?.project_count || 0} trend="+1" positive />
                <MetricCard title="Completion Rate" value={`${completionRate}%`} trend="+5%" positive />
                <MetricCard title="Pending Tasks" value={data?.pending_tasks || 0} trend="-2" positive />
                <MetricCard title="Overdue Tasks" value={data?.overdue_tasks || 0} trend="+0" positive={data?.overdue_tasks === 0} />
            </div>

            {/* Main Charts Area */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                {/* Burndown Chart Placeholder */}
                <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm shadow-2xl">
                    <div className="flex items-center gap-2 mb-6">
                        <TrendingUp className="text-pink-500" size={20} />
                        <h2 className="text-lg font-semibold text-white">Sprint Burndown</h2>
                    </div>
                    <div className="h-64 relative w-full flex items-end justify-between px-2">
                        {/* CSS-only line chart representation using SVG */}
                        <svg className="absolute inset-0 w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                            {/* Ideal Burn */}
                            <line x1="0" y1="10" x2="100" y2="90" stroke="#475569" strokeWidth="1" strokeDasharray="4 4" />
                            {/* Actual Burn */}
                            <motion.path 
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 1.5, ease: "easeInOut" }}
                                d="M 0 10 L 20 15 L 40 40 L 60 45 L 80 70 L 100 65" 
                                fill="none" 
                                stroke="#ec4899" 
                                strokeWidth="2" 
                            />
                            <path d="M 0 10 L 20 15 L 40 40 L 60 45 L 80 70 L 100 65 L 100 100 L 0 100 Z" fill="url(#gradientPink)" opacity="0.15" />
                            <defs>
                                <linearGradient id="gradientPink" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#ec4899" stopOpacity="1"/>
                                    <stop offset="100%" stopColor="#ec4899" stopOpacity="0"/>
                                </linearGradient>
                            </defs>
                        </svg>
                        {/* X Axis Labels */}
                        {[1, 2, 3, 4, 5, 6].map((day) => (
                            <div key={day} className="text-xs text-slate-500 relative z-10 font-medium">Day {day}</div>
                        ))}
                    </div>
                </div>

                {/* Activity Heatmap */}
                <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm shadow-2xl">
                    <div className="flex items-center gap-2 mb-6">
                        <Activity className="text-emerald-500" size={20} />
                        <h2 className="text-lg font-semibold text-white">Activity Heatmap</h2>
                    </div>
                    <div className="grid grid-cols-12 gap-1 h-64 content-start">
                        {Array.from({ length: 144 }).map((_, i) => {
                            const intensity = Math.random();
                            let bgClass = "bg-slate-800/50";
                            if (intensity > 0.8) bgClass = "bg-emerald-500";
                            else if (intensity > 0.5) bgClass = "bg-emerald-500/60";
                            else if (intensity > 0.2) bgClass = "bg-emerald-500/30";
                            
                            return (
                                <motion.div 
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.005 }}
                                    key={i} 
                                    className={`w-full aspect-square rounded-sm ${bgClass} hover:ring-2 ring-white/50 cursor-pointer transition-all`}
                                />
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value, trend, positive }: any) {
    return (
        <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-5 backdrop-blur-sm shadow-xl hover:-translate-y-1 transition-transform">
            <div className="text-sm font-medium text-slate-400 mb-1">{title}</div>
            <div className="flex items-end justify-between">
                <div className="text-3xl font-bold text-white">{value}</div>
                <div className={`text-sm font-semibold flex items-center gap-1 ${positive ? 'text-emerald-400' : 'text-pink-400'}`}>
                    {trend}
                </div>
            </div>
        </div>
    );
}
