'use client';
import React, { useState } from 'react';
import { Send, Image as ImageIcon, Smile } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TaskComments({ taskId }: { taskId: string }) {
    const [comment, setComment] = useState('');
    const [comments] = useState([
        { id: 1, user: 'John Doe', avatar: 'JD', color: 'bg-emerald-500', time: '2 hours ago', text: 'I have updated the GraphQL schema to support this.' },
        { id: 2, user: 'Sarah Connor', avatar: 'SC', color: 'bg-pink-500', time: '1 hour ago', text: 'Looks good. Let me know when the PR is ready for review.' }
    ]);

    return (
        <div className="flex flex-col h-full bg-slate-900/40 rounded-2xl border border-white/5 shadow-inner">
            <div className="flex-1 overflow-y-auto space-y-4 p-4 scrollbar-thin scrollbar-thumb-white/10">
                {comments.map((c, i) => (
                    <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} transition={{delay: i*0.1}} key={c.id} className="flex gap-3 group">
                        <div className={`w-8 h-8 rounded-full ${c.color} flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-lg`}>
                            {c.avatar}
                        </div>
                        <div className="flex-1">
                            <div className="flex items-baseline gap-2">
                                <span className="font-semibold text-sm text-white">{c.user}</span>
                                <span className="text-xs text-slate-500">{c.time}</span>
                            </div>
                            <p className="text-sm text-slate-300 mt-1 bg-slate-800/50 p-3 rounded-r-xl rounded-bl-xl border border-white/5 group-hover:border-white/10 transition-colors inline-block leading-relaxed">
                                {c.text}
                            </p>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="p-4 border-t border-white/10 bg-slate-900/80 rounded-b-2xl">
                <div className="bg-slate-800/80 border border-white/10 rounded-xl p-2 focus-within:border-emerald-500/50 focus-within:bg-slate-800 transition-all shadow-inner">
                    <textarea 
                        value={comment}
                        onChange={e => setComment(e.target.value)}
                        placeholder="Ask a question or post an update..." 
                        className="w-full bg-transparent border-none text-white text-sm focus:outline-none resize-none p-2"
                        rows={2}
                    />
                    <div className="flex justify-between items-center px-2 pb-1">
                        <div className="flex gap-2 text-slate-400">
                            <button className="p-1.5 hover:text-white hover:bg-white/5 rounded-md transition-colors"><ImageIcon size={16} /></button>
                            <button className="p-1.5 hover:text-white hover:bg-white/5 rounded-md transition-colors"><Smile size={16} /></button>
                        </div>
                        <button className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50" disabled={!comment.trim()}>
                            <Send size={14} /> Comment
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
