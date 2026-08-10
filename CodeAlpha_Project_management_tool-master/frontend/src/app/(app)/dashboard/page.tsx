'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
    CheckCircle2, Clock, AlertCircle, Calendar as CalendarIcon, 
    MoreHorizontal, ArrowUpRight, TrendingUp, FolderKanban,
    Users, Building, DollarSign
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import { useDialog } from '@/components/ui/DialogProvider';

export default function DashboardPage() {
    const router = useRouter();
    const dialog = useDialog();
    const { data: dashboard, isLoading, error } = useQuery({
        queryKey: ['dashboard'],
        queryFn: async () => {
            const res = await api.get('/dashboard/');
            return res.data;
        }
    });

    if (isLoading) return <div className="text-white text-center py-20 animate-pulse">Loading Workspace Data...</div>;
    if (error) return <div className="text-red-500 text-center py-20">Failed to load dashboard data.</div>;

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Good Morning, {dashboard?.user?.first_name || 'User'}</h1>
                    <p className="text-slate-400 mt-1">Here's what's happening across your workspace today. Role: <span className="font-semibold text-emerald-400">{dashboard?.user?.role}</span></p>
                </div>
                <button onClick={() => router.push('/dashboard/projects')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2">
                    <span className="text-lg">+</span> Go to Projects
                </button>
            </div>

            {/* Widgets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <WidgetCard title="Total Users" value={dashboard?.total_users || 0} subtitle="Across platform" icon={<Users className="text-teal-400" />} onClick={() => router.push('/dashboard/teams')} />
                <WidgetCard title="Total Organizations" value={dashboard?.organization_count || 0} subtitle="Workspaces" icon={<Building className="text-cyan-400" />} onClick={() => {}} />
                <WidgetCard title="Total Projects" value={dashboard?.project_count || 0} subtitle={`${dashboard?.active_projects || 0} Active`} icon={<FolderKanban className="text-emerald-400" />} onClick={() => router.push('/dashboard/projects')} />
                <WidgetCard title="Completed Projects" value={dashboard?.completed_projects || 0} subtitle="Delivered" icon={<CheckCircle2 className="text-emerald-400" />} onClick={() => router.push('/dashboard/projects')} />
                
                <WidgetCard title="Total Tasks" value={dashboard?.task_count || 0} subtitle={`${dashboard?.completed_tasks || 0} Completed`} icon={<CheckCircle2 className="text-emerald-400" />} onClick={() => router.push('/dashboard/tasks')} />
                <WidgetCard title="Pending Tasks" value={dashboard?.pending_tasks || 0} subtitle={`${dashboard?.todays_tasks || 0} due today`} icon={<Clock className="text-yellow-400" />} onClick={() => router.push('/dashboard/tasks')} />
                <WidgetCard title="Overdue" value={dashboard?.overdue_tasks || 0} subtitle="Needs attention" icon={<AlertCircle className="text-pink-400" />} onClick={() => router.push('/dashboard/tasks')} />
                <WidgetCard title="Revenue" value={`$${(dashboard?.revenue || 0).toLocaleString()}`} subtitle="Monthly recurring" icon={<DollarSign className="text-emerald-400" />} onClick={() => {}} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                {/* Chart Area */}
                <div className="lg:col-span-2 bg-slate-900/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-semibold text-white">Weekly Productivity</h2>
                        <button 
                            className="text-slate-400 hover:text-white"
                            onClick={async () => {
                                const action = await dialog.prompt("Type 'export' to download report, or 'refresh' to reload data:");
                                if (action === 'export') {
                                    await dialog.alert("Exporting Weekly Productivity Report...");
                                } else if (action === 'refresh') {
                                    window.location.reload();
                                }
                            }}
                        >
                            <MoreHorizontal size={20} />
                        </button>
                    </div>
                    <div className="h-64 flex items-end justify-between gap-2 px-2">
                        {/* Custom Animated Bar Chart */}
                        {(dashboard?.weekly_productivity || [0,0,0,0,0,0,0]).map((height: number, i: number) => (
                            <div key={i} className="w-full flex flex-col items-center gap-2 group">
                                <motion.div 
                                    initial={{ height: 0 }}
                                    animate={{ height: `${height}%` }}
                                    transition={{ duration: 1, delay: i * 0.1 }}
                                    className="w-full rounded-t-md bg-gradient-to-t from-emerald-900/50 to-emerald-500/80 relative cursor-pointer hover:from-emerald-600 hover:to-emerald-400 transition-colors"
                                >
                                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-xs px-2 py-1 rounded text-white font-medium z-10 whitespace-nowrap">
                                        {height} Tasks
                                    </div>
                                </motion.div>
                                <span className="text-xs text-slate-500 font-medium">
                                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Upcoming Deadlines */}
                <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <CalendarIcon size={18} className="text-emerald-400" />
                            Upcoming Deadlines
                        </h2>
                    </div>
                    <div className="flex-1 space-y-4">
                        {dashboard?.upcoming_deadlines?.length > 0 ? dashboard.upcoming_deadlines.map((task: any, i: number) => (
                            <div onClick={() => router.push('/dashboard/tasks')} key={i} className="flex items-start justify-between p-3 rounded-xl bg-slate-800/30 border border-white/5 hover:bg-slate-800/50 transition cursor-pointer">
                                <div>
                                    <h4 className="text-sm font-medium text-white mb-1">{task.title}</h4>
                                    <div className="flex items-center gap-2 text-xs text-slate-400">
                                        <span>{task.project__name}</span>
                                        <span>•</span>
                                        <span className={new Date(task.due_date).toDateString() === new Date().toDateString() ? 'text-yellow-400 font-medium' : ''}>{task.due_date}</span>
                                    </div>
                                </div>
                                <div className={`w-2 h-2 rounded-full mt-1 ${task.priority === 'High' ? 'bg-pink-500' : task.priority === 'Medium' ? 'bg-yellow-500' : 'bg-emerald-500'}`} />
                            </div>
                        )) : (
                            <p className="text-sm text-slate-400 text-center mt-8">No upcoming deadlines.</p>
                        )}
                    </div>
                    <button onClick={() => router.push('/dashboard/calendar')} className="w-full mt-4 py-2 text-sm text-emerald-400 hover:text-emerald-300 font-medium flex items-center justify-center gap-1">
                        View Calendar <ArrowUpRight size={16} />
                    </button>
                </div>
            </div>
        </div>
    );
}

function WidgetCard({ title, value, subtitle, icon, onClick }: any) {
    return (
        <motion.div 
            onClick={onClick}
            whileHover={{ y: -2 }}
            className="bg-slate-900/40 border border-white/5 rounded-2xl p-5 backdrop-blur-sm cursor-pointer hover:bg-slate-800/40 transition-colors"
        >
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 rounded-xl bg-white/5">
                    {icon}
                </div>
                <TrendingUp size={16} className="text-emerald-400" />
            </div>
            <div>
                <div className="text-3xl font-bold text-white mb-1">{value}</div>
                <div className="text-sm font-medium text-slate-400 flex items-center justify-between">
                    {title}
                    <span className="text-xs text-slate-500">{subtitle}</span>
                </div>
            </div>
        </motion.div>
    );
}
