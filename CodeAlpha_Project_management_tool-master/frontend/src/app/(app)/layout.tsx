'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { 
    LayoutDashboard, CheckSquare, MessageSquare, 
    Calendar, Search, Menu, Settings, 
    FolderKanban, Plus, LogOut, X, Building, Users
} from 'lucide-react';
import NotificationsPopover from '@/components/NotificationsPopover';
import { motion, AnimatePresence } from 'framer-motion';
import { useDialog } from '@/components/ui/DialogProvider';

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const [isSidebarOpen, setSidebarOpen] = useState(true);

    return (
        <div className="flex h-screen bg-slate-950 text-slate-300 font-sans overflow-hidden">
            {/* Sidebar */}
            <AnimatePresence initial={false}>
                {isSidebarOpen && (
                    <motion.aside 
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 260, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        className="h-full border-r border-white/10 bg-slate-900/50 backdrop-blur-xl flex flex-col z-20 shrink-0 overflow-hidden"
                    >
                        <div className="h-16 flex items-center justify-between px-4 border-b border-white/5 shrink-0">
                            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 truncate">
                                NexusProject
                            </span>
                            <button onClick={() => setSidebarOpen(false)} className="md:hidden text-slate-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-3">Main</div>
                            <NavLink href="/dashboard" icon={<LayoutDashboard size={18} />} label="Dashboard" />
                            <NavLink href="/dashboard/projects" icon={<FolderKanban size={18} />} label="Projects" />
                            <NavLink href="/dashboard/tasks" icon={<CheckSquare size={18} />} label="My Tasks" />
                            <NavLink href="/dashboard/calendar" icon={<Calendar size={18} />} label="Calendar" />
                            <NavLink href="/dashboard/chat" icon={<MessageSquare size={18} />} label="Chat" />
                            <NavLink href="/dashboard/files" icon={<FolderKanban size={18} />} label="Files" />
                            
                            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-6 mb-2 px-3 pt-4 border-t border-white/5">Admin</div>
                            <NavLink href="/dashboard/organizations" icon={<Building size={18} />} label="Organizations" />
                            <NavLink href="/dashboard/teams" icon={<Users size={18} />} label="Users & Teams" />
                            
                            <WorkspaceList />
                        </div>

                        <div className="p-4 border-t border-white/5 shrink-0">
                            <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                                    <LogOut size={16} />
                                </div>
                                <div className="flex-1 truncate" onClick={() => window.location.href = '/login'}>
                                    <div className="text-sm font-medium text-white truncate">Sign Out</div>
                                </div>
                            </div>
                        </div>
                    </motion.aside>
                )}
            </AnimatePresence>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 h-full relative">
                {/* Topbar */}
                <header className="h-16 border-b border-white/10 bg-slate-900/30 backdrop-blur-md flex items-center justify-between px-4 z-40 shrink-0">
                    <div className="flex items-center gap-4">
                        {!isSidebarOpen && (
                            <button onClick={() => setSidebarOpen(true)} className="text-slate-400 hover:text-white transition">
                                <Menu className="w-5 h-5" />
                            </button>
                        )}
                        
                        <div className="relative hidden md:block w-64 lg:w-96">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input 
                                type="text"
                                placeholder="Search tasks, projects, people (Cmd+K)"
                                className="w-full bg-slate-800/50 border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-white placeholder-slate-500"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <NotificationsPopover />
                        <Link href="/dashboard/settings" className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition">
                            <Settings className="w-5 h-5" />
                        </Link>
                        <Link href="/login" className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition ml-2 border border-white/10">
                            <LogOut className="w-4 h-4" />
                        </Link>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-auto bg-slate-950 relative">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950 pointer-events-none" />
                    <div className="relative z-10 p-6">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}

function NavLink({ href, icon, label }: { href: string, icon: React.ReactNode, label: string }) {
    return (
        <Link href={href} className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors group">
            <div className="group-hover:text-emerald-400 transition-colors">{icon}</div>
            <span className="font-medium text-sm">{label}</span>
        </Link>
    );
}

function WorkspaceList() {
    const [workspaces, setWorkspaces] = React.useState<any[]>([]);
    const dialog = useDialog();

    React.useEffect(() => {
        import('@/lib/api').then(({ default: api }) => {
            api.get('/organizations/workspaces/').then(res => setWorkspaces(res.data)).catch(console.error);
        });
    }, []);

    const colors = ['bg-blue-500', 'bg-pink-500', 'bg-emerald-500', 'bg-yellow-500', 'bg-emerald-500'];

    return (
        <>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-6 mb-2 px-3 flex justify-between items-center">
                Workspaces
                <button onClick={async () => {
                    const name = await dialog.prompt("Workspace Name:");
                    if (name) {
                        import('@/lib/api').then(({ default: api }) => {
                            api.post('/organizations/workspaces/', { name }).then(() => window.location.reload());
                        });
                    }
                }} className="hover:text-white"><Plus size={14} /></button>
            </div>
            {workspaces.map((ws: any, i: number) => (
                <NavLink key={ws.id} href={`/dashboard/projects?workspace=${ws.id}`} icon={<div className={`w-2 h-2 rounded-full ${colors[i % colors.length]}`} />} label={ws.name} />
            ))}
            {workspaces.length === 0 && <div className="px-3 text-xs text-slate-500">No workspaces found.</div>}
        </>
    );
}
