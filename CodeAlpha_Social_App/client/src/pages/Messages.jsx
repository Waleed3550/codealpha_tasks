import { useState, useEffect } from 'react';
import { Send, User as UserIcon } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export const Messages = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newMessage, setNewMessage] = useState('');
    const [receiverId, setReceiverId] = useState(''); // Very basic implementation

    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const res = await api.get('/messages/');
                setMessages(res.data.data || []);
            } catch (err) {
                console.error("Failed to load messages:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchMessages();
    }, []);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !receiverId) return;

        try {
            const res = await api.post('/messages/', {
                receiver_id: receiverId,
                content: newMessage
            });
            if (res.data.success) {
                setMessages([...messages, res.data.data]);
                setNewMessage('');
            }
        } catch (err) {
            alert('Failed to send message.');
        }
    };

    if (loading) return <p className="container">Loading messages...</p>;

    return (
        <div className="container" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)' }}>
            <h2 style={{ marginBottom: '20px' }}>Messages</h2>
            
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px', paddingRight: '10px' }}>
                {messages.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)' }}>No messages yet.</p>
                ) : (
                    messages.map(msg => {
                        const isMine = msg.sender.id === user.id;
                        return (
                            <div key={msg.id} style={{ alignSelf: isMine ? 'flex-end' : 'flex-start', maxWidth: '70%', background: isMine ? 'var(--primary-accent)' : 'var(--card-bg)', color: isMine ? 'white' : 'var(--text-color)', padding: '12px 16px', borderRadius: '12px', border: isMine ? 'none' : '1px solid var(--card-border)' }}>
                                {!isMine && <div style={{ fontSize: '0.8rem', opacity: 0.8, marginBottom: '4px' }}>{msg.sender.username}</div>}
                                <div style={{ fontSize: '0.95rem' }}>{msg.content}</div>
                            </div>
                        );
                    })
                )}
            </div>

            <form onSubmit={handleSend} style={{ display: 'flex', gap: '10px', marginTop: 'auto' }}>
                <input 
                    type="number" 
                    placeholder="User ID" 
                    value={receiverId} 
                    onChange={e => setReceiverId(e.target.value)}
                    style={{ width: '80px', padding: '12px', borderRadius: '8px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }}
                    required
                />
                <input 
                    type="text" 
                    placeholder="Write a message..." 
                    value={newMessage} 
                    onChange={e => setNewMessage(e.target.value)}
                    style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }}
                    required
                />
                <button type="submit" style={{ padding: '0 20px', borderRadius: '8px', border: 'none', background: 'var(--primary-accent)', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
};
