'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Info, CheckCircle2, X } from 'lucide-react';

type DialogType = 'alert' | 'confirm' | 'prompt';

interface DialogOptions {
    title?: string;
    message?: string;
    defaultValue?: string;
    type?: DialogType;
    resolve?: (value: any) => void;
    placeholder?: string;
}

interface DialogContextType {
    alert: (message: string, title?: string) => Promise<void>;
    confirm: (message: string, title?: string) => Promise<boolean>;
    prompt: (message: string, defaultValue?: string, title?: string) => Promise<string | null>;
}

const DialogContext = createContext<DialogContextType | null>(null);

export function useDialog() {
    const context = useContext(DialogContext);
    if (!context) throw new Error("useDialog must be used within DialogProvider");
    return context;
}

export function DialogProvider({ children }: { children: ReactNode }) {
    const [dialogs, setDialogs] = useState<(DialogOptions & { id: string })[]>([]);

    const createDialog = (options: DialogOptions) => {
        return new Promise<any>((resolve) => {
            const id = Math.random().toString(36).substring(7);
            setDialogs(prev => [...prev, { ...options, id, resolve }]);
        });
    };

    const handleClose = (id: string, value: any) => {
        setDialogs(prev => {
            const d = prev.find(x => x.id === id);
            if (d && d.resolve) d.resolve(value);
            return prev.filter(x => x.id !== id);
        });
    };

    return (
        <DialogContext.Provider value={{
            alert: (message, title) => createDialog({ type: 'alert', message, title }),
            confirm: (message, title) => createDialog({ type: 'confirm', message, title }),
            prompt: (message, defaultValue, title) => createDialog({ type: 'prompt', message, defaultValue, title })
        }}>
            {children}
            <div className="fixed inset-0 z-[200] pointer-events-none">
                <AnimatePresence>
                    {dialogs.map(dialog => (
                        <DialogComponent key={dialog.id} dialog={dialog} onClose={(val) => handleClose(dialog.id, val)} />
                    ))}
                </AnimatePresence>
            </div>
        </DialogContext.Provider>
    );
}

function DialogComponent({ dialog, onClose }: { dialog: any, onClose: (val: any) => void }) {
    const [inputValue, setInputValue] = useState(dialog.defaultValue || '');
    const isPrompt = dialog.type === 'prompt';
    const isConfirm = dialog.type === 'confirm';

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (isPrompt) onClose(inputValue);
        else onClose(true);
    };

    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose(isPrompt ? null : false);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isPrompt, onClose]);

    return (
        <div className="fixed inset-0 pointer-events-auto flex items-center justify-center p-4 z-[200]">
            <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }} 
                className="absolute inset-0 bg-slate-950/60 backdrop-blur-md"
                onClick={() => onClose(isPrompt ? null : false)}
            />
            <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden relative"
            >
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-80" />
                
                <div className="p-8">
                    <div className="flex items-start gap-4 mb-6">
                        <div className={`p-3 rounded-2xl flex-shrink-0 shadow-inner border border-white/5 ${
                            dialog.type === 'confirm' ? 'bg-orange-500/10 text-orange-400' :
                            dialog.type === 'prompt' ? 'bg-emerald-500/10 text-emerald-400' :
                            'bg-emerald-500/10 text-emerald-400'
                        }`}>
                            {dialog.type === 'confirm' ? <AlertTriangle size={24} /> :
                             dialog.type === 'prompt' ? <Info size={24} /> :
                             <CheckCircle2 size={24} />}
                        </div>
                        <div className="flex-1 mt-1">
                            <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
                                {dialog.title || (dialog.type === 'confirm' ? 'Please Confirm' : dialog.type === 'prompt' ? 'Input Required' : 'Notice')}
                            </h3>
                            <p className="text-sm text-slate-400 leading-relaxed">{dialog.message}</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {isPrompt && (
                            <div className="relative group">
                                <label className="absolute -top-2 left-3 px-1 bg-slate-900 text-[10px] font-bold uppercase tracking-wider text-emerald-400 transition-colors z-10">
                                    Response
                                </label>
                                <input
                                    autoFocus
                                    type="text"
                                    value={inputValue}
                                    onChange={e => setInputValue(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner relative z-0"
                                    placeholder="Enter your value..."
                                />
                            </div>
                        )}

                        <div className="flex justify-end gap-3">
                            {(isConfirm || isPrompt) && (
                                <button 
                                    type="button" 
                                    onClick={() => onClose(isPrompt ? null : false)}
                                    className="px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 transition-colors shadow-inner"
                                >
                                    Cancel
                                </button>
                            )}
                            <button 
                                type="submit"
                                className={`px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition-all shadow-lg flex items-center gap-2 ${
                                    isConfirm 
                                    ? 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 shadow-red-500/25' 
                                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-emerald-500/25'
                                }`}
                            >
                                {isConfirm ? 'Confirm Action' : isPrompt ? 'Submit' : 'Understood'}
                            </button>
                        </div>
                    </form>
                </div>
            </motion.div>
        </div>
    );
}
