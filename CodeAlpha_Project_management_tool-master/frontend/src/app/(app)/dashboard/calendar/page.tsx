'use client';
import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

export default function CalendarPage() {
    const dialog = useDialog();
    const [events, setEvents] = useState<any[]>([]);
    
    // Generate simple month grid for UI completeness
    const days = Array.from({ length: 35 }, (_, i) => i + 1);

    const fetchEvents = () => {
        api.get('/calendar/calendarevents/').then(res => setEvents(res.data)).catch(console.error);
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    const handleAddEvent = async () => {
        const title = await dialog.prompt("Event Title:");
        if (!title) return;
        const dateStr = await dialog.prompt("Date (YYYY-MM-DD):", new Date().toISOString().split('T')[0]);
        if (title && dateStr) {
            // Need a workspace, let's grab the first one user belongs to, or let backend assign default
            // In a real app we would select workspace
            api.get('/organizations/workspaces/').then(res => {
                if (res.data.length > 0) {
                    api.post('/calendar/calendarevents/', {
                        title,
                        workspace: res.data[0].id,
                        start_time: `${dateStr}T09:00:00Z`,
                        end_time: `${dateStr}T10:00:00Z`
                    }).then(() => fetchEvents());
                }
            });
        }
    };
    
    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6 shrink-0">
                <div className="flex items-center gap-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Calendar</h1>
                        <p className="text-slate-400 mt-1">Workspace Event Schedule</p>
                    </div>
                    <div className="flex gap-1 ml-4 bg-slate-800/50 p-1 rounded-lg border border-white/5">
                        <button className="p-1.5 rounded-md hover:bg-slate-700 text-slate-300 transition"><ChevronLeft size={20} /></button>
                        <button className="px-3 py-1.5 rounded-md text-sm font-medium hover:bg-slate-700 text-white transition">Today</button>
                        <button className="p-1.5 rounded-md hover:bg-slate-700 text-slate-300 transition"><ChevronRight size={20} /></button>
                    </div>
                </div>
                <button onClick={handleAddEvent} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20">
                    <Plus size={18} /> Add Event
                </button>
            </div>

            <div className="flex-1 bg-slate-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm flex flex-col shadow-2xl">
                <div className="grid grid-cols-7 border-b border-white/10 bg-slate-800/30 shrink-0">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                        <div key={day} className="p-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            {day}
                        </div>
                    ))}
                </div>
                
                <div className="flex-1 grid grid-cols-7 grid-rows-5 bg-white/5 gap-px">
                    {days.map((day, i) => {
                        const isCurrentMonth = day > 3 && day <= 34;
                        const date = isCurrentMonth ? day - 3 : (day <= 3 ? 27 + day : day - 34);
                        
                        // We filter real events by date. This is a very naive frontend calendar mapping 
                        // just for the current month approximation
                        // A robust app uses a library like fullcalendar
                        // Here we just map by matching the date day if it's current month
                        const dayEvents = isCurrentMonth ? events.filter(e => {
                            const d = new Date(e.start_time);
                            return d.getDate() === date;
                        }) : [];
                        
                        return (
                            <div 
                                key={i} 
                                className={`bg-slate-950 p-2 hover:bg-slate-900 transition-colors cursor-pointer flex flex-col gap-1 relative group ${!isCurrentMonth ? 'opacity-40 bg-slate-950/50' : ''}`}
                            >
                                <span className={`text-sm font-medium p-1 w-7 h-7 flex items-center justify-center rounded-full ${date === new Date().getDate() && isCurrentMonth ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'text-slate-400 group-hover:text-white transition-colors'}`}>
                                    {date}
                                </span>
                                
                                {dayEvents.map(evt => (
                                    <motion.div key={evt.id} initial={{opacity:0, scale:0.95}} animate={{opacity:1, scale:1}} className="text-[10px] p-1.5 rounded bg-emerald-500/10 text-emerald-400 font-medium truncate border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">
                                        {evt.title}
                                    </motion.div>
                                ))}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
