import { useState, useEffect } from 'react';
import { UserCheck, UserPlus, X } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export const Network = () => {
    const { user } = useAuth();
    const [requests, setRequests] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchNetworkData();
    }, []);

    const fetchNetworkData = async () => {
        try {
            const [reqRes, suggRes, connRes] = await Promise.all([
                api.get('/connections/requests/'),
                api.get('/connections/suggestions/'),
                api.get('/connections/')
            ]);
            setRequests(reqRes.data.data || []);
            setSuggestions(suggRes.data.data || []);
            setConnections(connRes.data.data || []);
        } catch (err) {
            console.error('Failed to load network data');
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async (id) => {
        try {
            await api.post(`/connections/requests/${id}/accept/`);
            fetchNetworkData(); // Refresh to update lists
        } catch (err) {
            alert('Failed to accept request');
        }
    };

    const handleReject = async (id) => {
        try {
            await api.post(`/connections/requests/${id}/reject/`);
            setRequests(requests.filter(req => req.id !== id));
        } catch (err) {
            alert('Failed to reject request');
        }
    };

    const handleConnect = async (userId) => {
        try {
            await api.post(`/connections/requests/send/${userId}/`);
            // Optimistically remove from suggestions
            setSuggestions(suggestions.filter(sugg => sugg.user_id !== userId));
            alert('Connection request sent!');
        } catch (err) {
            alert('Failed to send request');
        }
    };

    if (loading) return <p style={{ padding: '20px', textAlign: 'center' }}>Loading your network...</p>;

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 750px) 300px', gap: '24px', justifyContent: 'center' }}>
            
            {/* Left Column - Network Content */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* Pending Requests */}
                {requests.length > 0 && (
                    <div className="card" style={{ padding: '20px', background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                        <h2 style={{ margin: '0 0 16px 0', fontSize: '1.2rem', fontWeight: 600 }}>Invitations ({requests.length})</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {requests.map(req => (
                                <div key={req.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--card-border)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <Link to={`/profile/${req.sender.id}`} style={{ textDecoration: 'none' }}>
                                            {req.sender.avatar ? (
                                                <img src={req.sender.avatar} alt="Avatar" style={{ width: 64, height: 64, borderRadius: '50%', objectFit: 'cover' }} />
                                            ) : (
                                                <div style={{ width: 64, height: 64, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.5rem' }}>
                                                    {req.sender.username.charAt(0).toUpperCase()}
                                                </div>
                                            )}
                                        </Link>
                                        <div>
                                            <Link to={`/profile/${req.sender.id}`} style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
                                                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{req.sender.username}</h3>
                                            </Link>
                                            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>Sent you a connection request</p>
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: '12px' }}>
                                        <button onClick={() => handleReject(req.id)} style={{ background: 'transparent', border: '1px solid var(--text-muted)', color: 'var(--text-muted)', borderRadius: '24px', padding: '6px 16px', fontWeight: 600, cursor: 'pointer' }}>Ignore</button>
                                        <button onClick={() => handleAccept(req.id)} style={{ background: 'transparent', border: '1px solid var(--primary-accent)', color: 'var(--primary-accent)', borderRadius: '24px', padding: '6px 16px', fontWeight: 600, cursor: 'pointer' }}>Accept</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Suggestions */}
                <div className="card" style={{ padding: '20px', background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                    <h2 style={{ margin: '0 0 16px 0', fontSize: '1.2rem', fontWeight: 600 }}>Suggested for you</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
                        {suggestions.map(sugg => (
                            <div key={sugg.id} className="card" style={{ padding: 0, overflow: 'hidden', textAlign: 'center', display: 'flex', flexDirection: 'column', height: '100%', border: '1px solid var(--card-border)' }}>
                                <div style={{ height: '60px', backgroundColor: 'var(--primary-accent)', width: '100%' }}></div>
                                <div style={{ marginTop: '-40px', display: 'flex', justifyContent: 'center' }}>
                                    <Link to={`/profile/${sugg.user_id}`}>
                                        {sugg.avatar ? (
                                            <img src={sugg.avatar} alt="Avatar" style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--card-bg)' }} />
                                        ) : (
                                            <div style={{ width: 80, height: 80, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '2rem', border: '3px solid var(--card-bg)' }}>
                                                {sugg.username.charAt(0).toUpperCase()}
                                            </div>
                                        )}
                                    </Link>
                                </div>
                                <div style={{ padding: '12px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                    <Link to={`/profile/${sugg.user_id}`} style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
                                        <h3 style={{ margin: '0 0 4px 0', fontSize: '1rem', fontWeight: 600 }}>{sugg.username}</h3>
                                    </Link>
                                    <p style={{ margin: '0 0 16px 0', fontSize: '0.8rem', color: 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                                        {sugg.bio || 'Software Professional'}
                                    </p>
                                    <button onClick={() => handleConnect(sugg.user_id)} style={{ width: '100%', background: 'transparent', border: '1px solid var(--primary-accent)', color: 'var(--primary-accent)', borderRadius: '24px', padding: '6px 0', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', cursor: 'pointer', transition: 'background 0.2s' }}>
                                        <UserPlus size={16} /> Connect
                                    </button>
                                </div>
                            </div>
                        ))}
                        {suggestions.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No new suggestions.</p>}
                    </div>
                </div>

            </div>

            {/* Right Column - Manage Network */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="card" style={{ padding: '20px', background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                    <h3 style={{ margin: '0 0 16px 0', fontSize: '1rem', fontWeight: 600 }}>Manage my network</h3>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', cursor: 'pointer', color: 'var(--text-color)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontWeight: 500 }}>
                            <UserCheck size={20} color="var(--text-muted)" />
                            Connections
                        </div>
                        <span style={{ fontWeight: 600 }}>{connections.length}</span>
                    </div>
                </div>
            </div>

        </div>
    );
};
