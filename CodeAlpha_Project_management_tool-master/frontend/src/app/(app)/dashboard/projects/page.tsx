'use client';
import React, { useState, useEffect } from 'react';
import KanbanBoard from '@/components/KanbanBoard';
import { useProjects } from '@/hooks/useProjects';
import { useDialog } from '@/components/ui/DialogProvider';

export default function ProjectsPage() {
    const dialog = useDialog();
    const { data: projects, isLoading } = useProjects();
    const [activeProject, setActiveProject] = useState<any>(null);

    useEffect(() => {
        if (projects && projects.length > 0 && !activeProject) {
            setActiveProject(projects[0]);
        }
    }, [projects, activeProject]);

    if (isLoading) return <div className="p-6 text-white animate-pulse">Loading projects...</div>;
    
    if (!projects || projects.length === 0) {
        return (
            <div className="h-[calc(100vh-8rem)] flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-xl font-bold text-white mb-2">No Projects Found</h2>
                    <p className="text-slate-400 mb-4">You don't have any projects in this workspace yet.</p>
                    <button onClick={async () => {
                        const name = await dialog.prompt("Project Name:");
                        if (!name) return;
                        const description = await dialog.prompt("Description:");
                        if (name) {
                            import('@/lib/api').then(({ default: api }) => {
                                // Since no workspace context in this exact moment, grab first or default
                                api.get('/organizations/workspaces/').then(res => {
                                    if(res.data.length > 0) {
                                        api.post('/projects/', { name, description, workspace: res.data[0].id }).then(() => window.location.reload());
                                    } else {
                                        dialog.alert("Please create a workspace first.");
                                    }
                                });
                            });
                        }
                    }} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors">
                        Create Project
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 shrink-0">
                <div>
                    <div className="flex items-center gap-2 mb-2 text-sm text-emerald-400 font-medium">
                        <select 
                            className="bg-transparent border-none focus:outline-none cursor-pointer hover:text-emerald-300"
                            value={activeProject?.id || ''}
                            onChange={(e) => setActiveProject(projects.find((p: any) => String(p.id) === e.target.value))}
                        >
                            {projects.map((p: any) => (
                                <option key={p.id} value={p.id} className="bg-slate-900 text-white">{p.name}</option>
                            ))}
                        </select>
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">{activeProject?.name}</h1>
                    <p className="text-slate-400 mt-1">{activeProject?.description || 'No description provided.'}</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex -space-x-3 mr-4">
                        {[1,2,3].map(i => (
                            <div key={i} className="w-8 h-8 rounded-full border-2 border-slate-900 bg-gradient-to-br from-emerald-500 to-teal-500" />
                        ))}
                    </div>
                    <button 
                        onClick={async () => {
                            if (!activeProject) return;
                            const email = await dialog.prompt("Enter the email address of the user to share this project with:");
                            if (email) {
                                import('@/lib/api').then(({ default: api }) => {
                                    api.post(`/projects/${activeProject.id}/share/`, { email })
                                        .then(res => dialog.alert(res.data.status || "Project shared successfully!"))
                                        .catch(err => dialog.alert(err.response?.data?.error || "Failed to share project."));
                                });
                            }
                        }}
                        className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-medium rounded-lg transition-colors border border-white/5"
                    >
                        Share Project
                    </button>
                </div>
            </div>

            {/* Kanban Board Area */}
            <div className="flex-1 overflow-hidden">
                {activeProject && <KanbanBoard projectId={activeProject.id} />}
            </div>
        </div>
    );
}
