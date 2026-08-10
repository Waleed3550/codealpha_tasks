'use client';
import React from 'react';
import { useTasks } from '@/hooks/useTasks';
import { CheckCircle2, Clock, MoreHorizontal, Filter, Plus } from 'lucide-react';
import { motion } from 'framer-motion';

import { useRouter } from 'next/navigation';
import { useDialog } from '@/components/ui/DialogProvider';

export default function TasksPage() {
    const dialog = useDialog();
    const { data: tasks, isLoading } = useTasks();
    const router = useRouter();

    const displayTasks = tasks?.results || tasks || [];

    return (
        <div className="h-full flex flex-col max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8 shrink-0">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">My Tasks</h1>
                    <p className="text-slate-400 mt-1">Manage and track your assigned work across all workspaces.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="p-2 rounded-lg bg-slate-800/50 border border-white/10 text-slate-400 hover:text-white transition">
                        <Filter size={18} />
                    </button>
                    <button onClick={() => router.push('/dashboard/projects')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20">
                        <Plus size={18} /> Go to Projects to add Task
                    </button>
                </div>
            </div>

            <div className="bg-slate-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm flex-1 flex flex-col shadow-2xl">
                <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-slate-800/30 text-xs font-semibold text-slate-400 uppercase tracking-wider shrink-0">
                    <div className="col-span-6">Task Name</div>
                    <div className="col-span-2">Status</div>
                    <div className="col-span-2">Priority</div>
                    <div className="col-span-2 text-right">Due Date</div>
                </div>
                
                <div className="divide-y divide-white/5 overflow-y-auto flex-1">
                    {displayTasks.map((task: any, idx: number) => (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            key={task.id} 
                            className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-slate-800/40 transition-colors group cursor-pointer"
                        >
                            <div className="col-span-6 flex items-center gap-3">
                                <button className={`text-slate-500 hover:text-emerald-400 transition-colors ${task.status === 'done' ? 'text-emerald-500' : ''}`}>
                                    <CheckCircle2 size={20} />
                                </button>
                                <span className={`text-sm font-medium transition-colors ${task.status === 'done' ? 'text-slate-500 line-through' : 'text-white group-hover:text-emerald-300'}`}>
                                    {task.title}
                                </span>
                            </div>
                            <div className="col-span-2">
                                <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                                    task.status === 'in_progress' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 
                                    task.status === 'done' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                    'bg-slate-800 text-slate-300 border-white/5'
                                }`}>
                                    {task.status}
                                </span>
                            </div>
                            <div className="col-span-2">
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${task.priority === 'High' ? 'bg-pink-500' : task.priority === 'Medium' ? 'bg-yellow-500' : 'bg-slate-500'}`} />
                                    <span className="text-sm text-slate-300">{task.priority}</span>
                                </div>
                            </div>
                            <div className="col-span-2 flex items-center justify-between">
                                <span className={`text-sm flex items-center gap-1.5 ${task.due_date ? 'text-slate-400' : 'text-slate-500'}`}>
                                    <Clock size={14} /> {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No date'}
                                </span>
                                <button 
                                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-white transition-opacity p-1 rounded hover:bg-white/10"
                                    onClick={async (e) => {
                                        e.stopPropagation();
                                        const action = await dialog.prompt("Type 'edit' to edit task, or 'delete' to delete task:");
                                        if (action === 'edit') {
                                            const newTitle = await dialog.prompt("New title:", task.title);
                                            if (newTitle) {
                                                import('@/lib/api').then(({ default: api }) => {
                                                    api.patch(`/tasks/${task.id}/`, { title: newTitle })
                                                        .then(() => window.location.reload());
                                                });
                                            }
                                        } else if (action === 'delete') {
                                            if (await dialog.confirm("Are you sure you want to delete this task?")) {
                                                import('@/lib/api').then(({ default: api }) => {
                                                    api.delete(`/tasks/${task.id}/`)
                                                        .then(() => window.location.reload());
                                                });
                                            }
                                        }
                                    }}
                                >
                                    <MoreHorizontal size={18} />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
