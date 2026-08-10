'use client';
import React, { useState, useEffect } from 'react';
import { Search, FolderKanban, CheckSquare, User, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function GlobalSearch({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
    const [query, setQuery] = useState('');

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                isOpen ? onClose() : null;
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    const results = [
        { id: 1, type: 'project', title: 'Nexus Core V2', subtitle: 'Engineering Workspace', icon: <FolderKanban size={16} className="text-blue-400" /> },
        { id: 2, type: 'task', title: 'Design Landing Page V3', subtitle: 'Nexus Core V2 / To Do', icon: <CheckSquare size={16} className="text-emerald-400" /> },
        { id: 3, type: 'user', title: 'John Doe', subtitle: 'Software Engineer', icon: <User size={16} className="text-purple-400" /> },
    ];

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] bg-slate-950/60 backdrop-blur-md">
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ duration: 0.2 }}
                        className="w-full max-w-2xl bg-slate-900/90 border border-white/10 rounded-3xl shadow-[0_0_60px_rgba(0,0,0,0.6)] backdrop-blur-xl overflow-hidden relative"
                    >
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500" />
                        
                        <div className="flex items-center px-6 py-5 border-b border-white/5 bg-white/5">
                            <Search className="w-6 h-6 text-emerald-400 mr-4" />
                            <input 
                                autoFocus
                                value={query}
                                onChange={e => setQuery(e.target.value)}
                                placeholder="Search tasks, projects, people (Cmd+K)" 
                                className="flex-1 bg-transparent border-none text-white focus:outline-none placeholder-slate-500 text-xl font-medium tracking-wide"
                            />
                            <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg text-xs px-3 font-bold uppercase tracking-wider">
                                ESC
                            </button>
                        </div>
                        
                        <div className="p-2 max-h-[60vh] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
                            {results.length > 0 ? (
                                <div className="space-y-1">
                                    <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">Recent Searches</div>
                                    {results.map(res => (
                                        <div key={res.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 hover:border-white/10 border border-transparent transition-colors cursor-pointer group">
                                            <div className="p-2 rounded-lg bg-white/5 group-hover:bg-emerald-500/20 transition-colors shadow-inner">
                                                {res.icon}
                                            </div>
                                            <div>
                                                <div className="font-medium text-slate-200 group-hover:text-white transition-colors">{res.title}</div>
                                                <div className="text-xs text-slate-500">{res.subtitle}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="p-12 text-center text-slate-500">
                                    No results found for "{query}"
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
