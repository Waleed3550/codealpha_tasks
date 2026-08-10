import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import { useQueryClient } from '@tanstack/react-query';

export const useWebsocket = (projectId?: string) => {
    const [messages, setMessages] = useState<any[]>([]);
    const ws = useRef<WebSocket | null>(null);
    const accessToken = useAuthStore(state => state.accessToken);
    const queryClient = useQueryClient();

    useEffect(() => {
        if (!projectId || !accessToken) return;

        // Establish secure WebSocket connection with JWT token parameter
        const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'}/projects/${projectId}/?token=${accessToken}`;
        
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log(`[Realtime] Connected to WebSocket for Project ${projectId}`);
        };

        ws.current.onmessage = (event) => {
            const payload = JSON.parse(event.data);
            setMessages(prev => [...prev, payload]);
            
            // Enterprise App: Auto-update React Query Cache on Live WebSocket Events
            if (payload.action === 'TASK_MOVED') {
                queryClient.setQueryData(['tasks', projectId], (old: any) => {
                    if (!old) return old;
                    if (Array.isArray(old)) {
                        return old.map((t: any) => t.id === payload.data.task_id ? { ...t, status: payload.data.new_status } : t);
                    }
                    return old;
                });
            } else if (payload.action === 'NEW_COMMENT' || payload.action === 'TASK_CREATED') {
                queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
            }
        };

        ws.current.onerror = (error) => {
            console.error('[Realtime] WebSocket Error: ', error);
        };

        ws.current.onclose = () => {
            console.log('[Realtime] WebSocket Connection Closed');
        };

        return () => {
            if (ws.current?.readyState === WebSocket.OPEN) {
                ws.current.close();
            }
        };
    }, [projectId, accessToken]);

    const sendMessage = (action: string, data: any) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ action, data }));
        } else {
            console.warn('[Realtime] Attempted to send message but socket is not open.');
        }
    };

    return { messages, sendMessage };
};
