'use client';
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, MoreHorizontal, MessageSquare, Paperclip, CheckCircle2 } from 'lucide-react';

import { useTasks, useUpdateTask, useCreateTask } from '@/hooks/useTasks';
import { useColumns } from '@/hooks/useProjects';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

export default function KanbanBoard({ projectId }: { projectId: string }) {
    const dialog = useDialog();
    const [boardId, setBoardId] = useState<string | null>(null);
    
    useEffect(() => {
        if (projectId) {
            api.get(`/projects/boards/?project=${projectId}`).then(res => {
                if (res.data.length > 0) setBoardId(res.data[0].id);
            });
        }
    }, [projectId]);

    const { data: fetchedTasks, isLoading: tasksLoading } = useTasks(projectId);
    const { data: fetchedColumns, isLoading: columnsLoading } = useColumns(boardId || undefined);
    const updateTaskMutation = useUpdateTask();

    // Rely on fetched tasks, fallback to empty array
    // Optimistic updates are handled by useUpdateTask
    const displayTasks = fetchedTasks || [];
    const displayColumns = fetchedColumns || [];

    const handleDrop = (taskId: string, targetColId: string) => {
        updateTaskMutation.mutate({ id: taskId, status: targetColId });
    };

    if (tasksLoading || columnsLoading || !boardId) {
        return <div className="text-white">Loading board...</div>;
    }

    return (
        <div className="flex h-full gap-6 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-white/10">
            {displayColumns.map((col: any) => (
                <Column 
                    key={col.id} 
                    column={col} 
                    tasks={displayTasks.filter((t: any) => (t.status || 'todo') === String(col.id))} 
                    onDrop={handleDrop} 
                    projectId={projectId}
                />
            ))}
            <div className="min-w-[320px] max-w-[320px] h-full">
                <button 
                    onClick={async () => {
                        const title = await dialog.prompt("Column Name:");
                        if (title) api.post('/projects/columns/', { board: boardId, title, order: displayColumns.length + 1 }).then(() => window.location.reload());
                    }}
                    className="w-full flex items-center justify-center gap-2 py-4 rounded-xl border-2 border-dashed border-white/10 text-slate-400 hover:text-white hover:border-white/20 hover:bg-white/5 transition">
                    <Plus size={20} />
                    <span className="font-medium">Add Column</span>
                </button>
            </div>
        </div>
    );
}

function Column({ column, tasks, onDrop, projectId }: any) {
    const dialog = useDialog();
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.currentTarget.classList.add('bg-white/5');
    };
    
    const handleDragLeave = (e: React.DragEvent) => {
        e.currentTarget.classList.remove('bg-white/5');
    };

    const handleDropEvent = (e: React.DragEvent) => {
        e.preventDefault();
        e.currentTarget.classList.remove('bg-white/5');
        const taskId = e.dataTransfer.getData('taskId');
        onDrop(taskId, column.id);
    };

    const handleAddTask = async () => {
        const title = await dialog.prompt("Task title:");
        if (title) {
            import('@/lib/api').then(({ default: api }) => {
                api.post('/tasks/', { title, status: column.id, project: projectId }).then(() => {
                    window.location.reload(); // Simple refresh for now to avoid refetching complexities
                });
            });
        }
    };

    return (
        <div 
            className="min-w-[320px] max-w-[320px] flex flex-col h-full bg-slate-900/40 rounded-2xl border border-white/5 transition-colors duration-200"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDropEvent}
        >
            <div className="p-4 flex items-center justify-between border-b border-white/5">
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${column.color}`} />
                    <h3 className="font-semibold text-white">{column.title}</h3>
                    <span className="px-2 py-0.5 rounded-full bg-white/10 text-xs text-slate-300 font-medium">
                        {tasks.length}
                    </span>
                </div>
                <button 
                    className="text-slate-400 hover:text-white transition"
                    onClick={async () => {
                        const action = await dialog.prompt("Type 'rename' to rename column, or 'delete' to delete column:");
                        if (action === 'rename') {
                            const newTitle = await dialog.prompt("New title:", column.title);
                            if (newTitle) {
                                import('@/lib/api').then(({ default: api }) => {
                                    api.patch(`/projects/columns/${column.id}/`, { title: newTitle })
                                        .then(() => window.location.reload());
                                });
                            }
                        } else if (action === 'delete') {
                            if (await dialog.confirm("Are you sure you want to delete this column?")) {
                                import('@/lib/api').then(({ default: api }) => {
                                    api.delete(`/projects/columns/${column.id}/`)
                                        .then(() => window.location.reload());
                                });
                            }
                        }
                    }}
                >
                    <MoreHorizontal size={18} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {tasks.map((task: any) => (
                    <TaskCard key={task.id} task={task} />
                ))}
            </div>

            <div className="p-3 border-t border-white/5 mt-auto">
                <button onClick={handleAddTask} className="w-full flex items-center gap-2 py-2 px-3 rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition">
                    <Plus size={16} /> <span className="text-sm font-medium">Add Task</span>
                </button>
            </div>
        </div>
    );
}

function TaskCard({ task }: any) {
    const dialog = useDialog();
    const handleDragStart = (e: any) => {
        e.dataTransfer.setData('taskId', String(task.id));
    };

    return (
        <motion.div
            layoutId={String(task.id)}
            draggable
            onDragStart={handleDragStart as any}
            whileHover={{ y: -2, scale: 1.02 }}
            className="bg-slate-800/80 p-4 rounded-xl shadow-lg border border-white/10 cursor-grab active:cursor-grabbing hover:border-emerald-500/50 hover:shadow-emerald-500/20 transition-all relative group"
        >
            <div className="flex justify-between items-start mb-3">
                <div className="flex gap-2">
                    {task.tags && task.tags.map ? task.tags.map((tag: any, i: number) => (
                        <span key={i} className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-300 text-xs font-semibold">
                            {tag.name || tag}
                        </span>
                    )) : null}
                </div>
                <button 
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white"
                    onClick={async () => {
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
                    <MoreHorizontal size={16} />
                </button>
            </div>
            
            <h4 className="text-white font-medium mb-4 leading-tight">{task.title}</h4>
            
            <div className="flex items-center justify-between mt-4 text-slate-400">
                <div className="flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1 hover:text-white cursor-pointer"><MessageSquare size={14} /> 3</div>
                    <div className="flex items-center gap-1 hover:text-white cursor-pointer"><Paperclip size={14} /> 1</div>
                    <div className="flex items-center gap-1 hover:text-white cursor-pointer"><CheckCircle2 size={14} /> 2/4</div>
                </div>
                <div className="flex -space-x-2">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 via-teal-300 to-cyan-400 border-2 border-slate-800" />
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-pink-400 to-red-400 border-2 border-slate-800" />
                </div>
            </div>
        </motion.div>
    );
}
