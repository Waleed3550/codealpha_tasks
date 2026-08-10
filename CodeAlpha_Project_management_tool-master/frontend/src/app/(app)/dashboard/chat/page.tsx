'use client';
import React, { useState, useEffect, useRef } from 'react';
import { Send, Hash, MoreVertical, Phone, Video, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import api from '@/lib/api';
import { useAuthStore } from '@/store/useAuthStore';
import { useDialog } from '@/components/ui/DialogProvider';

interface ChatRoom {
    id: string;
    name: string;
    room_type: string;
}

interface ChatMessage {
    id: string;
    content: string;
    sender: string;
    sender_id: string;
    created_at: string;
}

export default function ChatPage() {
    const dialog = useDialog();
    const [rooms, setRooms] = useState<ChatRoom[]>([]);
    const [activeRoom, setActiveRoom] = useState<ChatRoom | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const token = useAuthStore((state) => state.accessToken);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    
    // Setup WebSocket
    const socketUrl = activeRoom && token 
        ? `${WS_URL}/ws/chat/${activeRoom.id}/?token=${token}` 
        : null;

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(socketUrl, {
        shouldReconnect: () => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
    });

    useEffect(() => {
        // Fetch rooms
        api.get('/chat/chatrooms/').then(res => {
            setRooms(res.data);
            if (res.data.length > 0) {
                setActiveRoom(res.data[0]);
            }
        }).catch(err => console.error("Failed to fetch chatrooms", err));
    }, []);

    useEffect(() => {
        // Fetch history when room changes
        if (activeRoom) {
            api.get(`/chat/messages/?room=${activeRoom.id}`).then(res => {
                setMessages(res.data);
                scrollToBottom();
            }).catch(err => console.error("Failed to fetch messages", err));
        }
    }, [activeRoom]);

    useEffect(() => {
        if (lastJsonMessage) {
            const data = lastJsonMessage as any;
            if (data.action === 'new_message') {
                setMessages(prev => [...prev, data.data]);
                scrollToBottom();
            }
        }
    }, [lastJsonMessage]);

    const scrollToBottom = () => {
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    };

    const handleSendMessage = () => {
        if (inputValue.trim() && readyState === ReadyState.OPEN) {
            sendJsonMessage({
                action: 'send_message',
                data: { content: inputValue.trim() }
            });
            setInputValue('');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="h-[calc(100vh-8rem)] flex bg-slate-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm shadow-2xl">
            {/* Channels Sidebar */}
            <div className="w-64 border-r border-white/5 bg-slate-950/30 flex flex-col shrink-0">
                <div className="p-4 border-b border-white/5">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input type="text" placeholder="Jump to..." className="w-full bg-slate-800/50 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors" />
                    </div>
                </div>
                <div className="flex-1 overflow-y-auto py-2">
                    <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">Channels</div>
                    <div className="space-y-0.5">
                        {rooms.map(room => (
                            <div 
                                key={room.id}
                                onClick={() => setActiveRoom(room)}
                                className={`mx-2 px-3 py-1.5 rounded-md flex items-center gap-2 cursor-pointer transition-colors ${activeRoom?.id === room.id ? 'bg-emerald-500/20 text-emerald-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
                            >
                                <Hash size={16} />
                                <span className="font-medium text-sm">{room.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Chat Header */}
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 shrink-0">
                    <div className="flex items-center gap-2">
                        <Hash className="text-slate-400" size={20} />
                        <h2 className="text-lg font-semibold text-white">{activeRoom ? activeRoom.name : 'Select a channel'}</h2>
                        {readyState === ReadyState.OPEN && <span className="w-2 h-2 rounded-full bg-green-500 ml-2" title="Connected"></span>}
                        {readyState !== ReadyState.OPEN && <span className="w-2 h-2 rounded-full bg-red-500 ml-2" title="Disconnected"></span>}
                    </div>
                    <div className="flex items-center gap-4 text-slate-400">
                        <Phone 
                            size={18} 
                            className="hover:text-white cursor-pointer transition-colors" 
                            onClick={() => {
                                if (activeRoom) {
                                    window.open(`https://meet.jit.si/NexusApp_Voice_${activeRoom.id}#config.startAudioOnly=true`, '_blank');
                                }
                            }}
                            title="Start Voice Call"
                        />
                        <Video 
                            size={18} 
                            className="hover:text-white cursor-pointer transition-colors" 
                            onClick={() => {
                                if (activeRoom) {
                                    window.open(`https://meet.jit.si/NexusApp_Video_${activeRoom.id}`, '_blank');
                                }
                            }}
                            title="Start Video Call"
                        />
                        <MoreVertical 
                            size={18} 
                            className="hover:text-white cursor-pointer transition-colors" 
                            onClick={async () => {
                                if (activeRoom) {
                                    if (await dialog.confirm("Are you sure you want to delete this channel?")) {
                                        api.delete(`/chat/chatrooms/${activeRoom.id}/`)
                                            .then(() => window.location.reload())
                                            .catch(() => dialog.alert("Failed to delete channel"));
                                    }
                                }
                            }}
                        />
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg, i) => (
                        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} key={msg.id} className="flex gap-4 group">
                            <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shrink-0 shadow-lg bg-emerald-500">
                                {msg.sender.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <div className="flex items-baseline gap-2 mb-1">
                                    <span className="font-semibold text-white">{msg.sender}</span>
                                    <span className="text-xs text-slate-500">
                                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                                <div className="text-slate-300 text-sm bg-white/5 p-3 rounded-xl rounded-tl-none border border-white/5 inline-block leading-relaxed">
                                    {msg.content}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/5 bg-slate-900/50">
                    <div className="bg-slate-800/80 border border-white/10 rounded-xl p-2 flex items-end gap-2 focus-within:border-emerald-500/50 focus-within:bg-slate-800 transition-all shadow-inner">
                        <textarea 
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={readyState !== ReadyState.OPEN || !activeRoom}
                            placeholder={activeRoom ? `Message #${activeRoom.name}...` : "Select a channel to message..."} 
                            className="flex-1 bg-transparent border-none focus:outline-none text-white text-sm resize-none min-h-[44px] max-h-32 p-2 scrollbar-thin scrollbar-thumb-white/10 disabled:opacity-50"
                            rows={1}
                        />
                        <button 
                            onClick={handleSendMessage}
                            disabled={!inputValue.trim() || readyState !== ReadyState.OPEN || !activeRoom}
                            className="p-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white transition-colors shrink-0 mb-0.5 shadow-lg shadow-emerald-500/20"
                        >
                            <Send size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
