'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Loader2, Check } from 'lucide-react';
import { useAITaskGenerator } from '@/hooks/useTasks';

export default function AIGeneratorModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
    const [prompt, setPrompt] = useState('');
    const { mutate: generateTask, isPending, isSuccess, data } = useAITaskGenerator();

    const handleGenerate = () => {
        if (!prompt.trim()) return;
        generateTask(prompt);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-md">
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="w-full max-w-lg bg-slate-900/90 border border-white/10 rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-xl overflow-hidden relative"
                    >
                        {/* Animated gradient border top */}
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />
                        
                        <div className="p-6">
                            <div className="flex justify-between items-center mb-6">
                                <div className="flex items-center gap-2 text-emerald-400">
                                    <Sparkles size={24} />
                                    <h2 className="text-xl font-bold text-white">AI Task Generator</h2>
                                </div>
                                <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                                    <X size={20} />
                                </button>
                            </div>

                            <p className="text-sm text-slate-400 mb-4">
                                Describe what you want to achieve, and Nexus AI will break it down into a structured project plan with subtasks, risk analysis, and timeline estimates.
                            </p>

                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="e.g. Build a comprehensive authentication system with JWT, social logins, and password reset flows..."
                                className="w-full bg-slate-950/50 border border-white/5 rounded-2xl p-5 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all resize-none h-32 mb-6 shadow-inner"
                            />

                            {isSuccess && (
                                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mb-6 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-emerald-300 text-sm flex items-start gap-3">
                                    <Check className="shrink-0 mt-0.5" size={16} />
                                    <div>
                                        <div className="font-semibold mb-1">Generated Successfully!</div>
                                        <div>Created 1 parent task and 4 subtasks. Risk level calculated.</div>
                                    </div>
                                </motion.div>
                            )}

                            <div className="flex justify-end gap-3 pt-2">
                                <button onClick={onClose} className="px-5 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 transition-colors">
                                    Cancel
                                </button>
                                <button 
                                    onClick={handleGenerate}
                                    disabled={isPending || !prompt.trim()}
                                    className="px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2"
                                >
                                    {isPending ? (
                                        <><Loader2 size={16} className="animate-spin" /> Analyzing...</>
                                    ) : (
                                        <><Sparkles size={16} /> Generate Plan</>
                                    )}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
