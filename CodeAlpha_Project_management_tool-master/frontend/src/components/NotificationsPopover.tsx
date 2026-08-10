import React, { useState } from 'react';
import { Bell, CheckCircle2, MessageSquare, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function NotificationsPopover() {
    const [isOpen, setIsOpen] = useState(false);
    
    const [notifications, setNotifications] = useState<any[]>([]);
    
    React.useEffect(() => {
        import('@/lib/api').then(({ default: api }) => {
            api.get('/notifications/notifications/').then(res => {
                // If it returns paginated response use res.data.results, else res.data
                setNotifications(res.data.results || res.data || []);
            }).catch(console.error);
        });
    }, []);

    const unreadCount = notifications.filter(n => !n.is_read).length;
    const popoverRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setIsOpen(false);
        };
        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
            document.addEventListener('keydown', handleEsc);
        }
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('keydown', handleEsc);
        };
    }, [isOpen]);

    const markAsRead = async () => {
        import('@/lib/api').then(({ default: api }) => {
            api.post('/notifications/notifications/mark-all-read/').then(() => {
                setNotifications(notifications.map(n => ({...n, is_read: true})));
            });
        });
    };

    return (
        <div className="relative" ref={popoverRef}>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition relative"
            >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_8px_rgba(236,72,153,0.8)] animate-pulse" />
                )}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div 
                        initial={{ opacity: 0, y: -15, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -15, scale: 0.95 }}
                        transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                        className="absolute right-0 top-[calc(100%+1rem)] w-[calc(100vw-2rem)] sm:w-[24rem] max-w-[24rem] bg-slate-900/80 backdrop-blur-2xl border border-white/20 rounded-3xl shadow-[0_30px_80px_-15px_rgba(0,0,0,0.8)] overflow-hidden z-[9999] origin-top-right ring-1 ring-black/50 flex flex-col"
                    >
                        <div className="p-5 border-b border-white/10 flex justify-between items-center bg-slate-900/90 sticky top-0 z-10">
                            <h3 className="font-semibold text-white tracking-wide">Notifications ({unreadCount})</h3>
                            <button onClick={markAsRead} className="text-xs text-emerald-400 hover:text-emerald-300 font-medium transition-colors">Mark all as read</button>
                        </div>
                        <div className="max-h-[500px] overflow-y-auto divide-y divide-white/5 scrollbar-thin scrollbar-thumb-white/10 bg-slate-900/40 relative">
                            {notifications.length === 0 ? (
                                <div className="p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
                                    <div className="relative mb-6">
                                        <div className="absolute inset-0 bg-emerald-500/20 rounded-full blur-xl scale-150 animate-pulse" />
                                        <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 flex items-center justify-center shadow-xl">
                                            <Bell size={36} className="text-slate-500" />
                                        </div>
                                    </div>
                                    <p className="text-lg font-semibold text-white tracking-wide">All caught up!</p>
                                    <p className="text-sm text-slate-400 mt-2 max-w-[200px] mx-auto leading-relaxed">When you have new notifications, they'll show up here.</p>
                                </div>
                            ) : (
                                notifications.map((note: any) => (
                                    <div key={note.id} className={`p-4 hover:bg-white/5 transition-colors cursor-pointer flex gap-3 group relative ${!note.is_read ? 'bg-emerald-500/5' : ''}`}>
                                        {/* Unread indicator */}
                                        {!note.is_read && (
                                            <span className="absolute left-2 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-pink-500 shadow-[0_0_8px_rgba(236,72,153,0.8)]" />
                                        )}
                                        
                                        {/* Icon */}
                                        <div className={`mt-0.5 p-2.5 rounded-full bg-slate-800 border border-white/5 group-hover:bg-slate-700 group-hover:border-white/10 transition-colors shrink-0 shadow-sm ${!note.is_read ? 'ml-3' : 'ml-4'}`}>
                                            <Bell size={18} className={!note.is_read ? "text-emerald-400" : "text-slate-400"} />
                                        </div>
                                        
                                        {/* Content */}
                                        <div className="flex-1 pr-2 min-w-0">
                                            <p className={`text-sm truncate ${!note.is_read ? 'text-white font-semibold' : 'text-slate-300 font-medium'} group-hover:text-white transition-colors`}>
                                                {note.title || 'System Notification'}
                                            </p>
                                            <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                                                {note.message || note.title || 'You have a new notification.'}
                                            </p>
                                            <p className="text-[11px] text-slate-500 mt-2 font-medium tracking-wide">
                                                {new Date(note.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                        <div className="p-4 border-t border-white/10 text-center bg-slate-900/90 hover:bg-slate-800/90 transition-colors cursor-pointer sticky bottom-0 z-10">
                            <span className="text-xs font-semibold text-slate-400 hover:text-white transition-colors uppercase tracking-wider">View all activity</span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
