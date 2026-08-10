import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { register, login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await register(username, email, password);
            if (res.success) {
                await login(username, password);
                navigate('/');
            } else {
                setError(res.message || 'Registration failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Registration failed');
        }
    };

    return (
        <div className="auth-container">
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                <div className="auth-card">
                    <h1 className="brand-text" style={{ fontSize: '3.2rem', margin: '10px 0 10px 0' }}>Instagram</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', fontWeight: '600', textAlign: 'center', marginBottom: '20px', lineHeight: '1.3' }}>
                        Sign up to see photos and videos from your friends.
                    </p>
                    
                    {error && <p style={{ color: 'var(--danger-color)', fontSize: '0.85rem', marginBottom: '14px', textAlign: 'center' }}>{error}</p>}
                    
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                        <input 
                            type="email" 
                            value={email} 
                            onChange={e => setEmail(e.target.value)} 
                            placeholder="Mobile Number or Email" 
                            required 
                            style={{ width: '100%', fontSize: '0.85rem', background: 'var(--input-bg)', border: '1px solid var(--card-border)', color: 'var(--text-color)', borderRadius: '6px', padding: '10px' }}
                        />
                        <input 
                            type="text" 
                            value={username} 
                            onChange={e => setUsername(e.target.value)} 
                            placeholder="Username" 
                            required 
                            style={{ width: '100%', fontSize: '0.85rem', background: 'var(--input-bg)', border: '1px solid var(--card-border)', color: 'var(--text-color)', borderRadius: '6px', padding: '10px' }}
                        />
                        <input 
                            type="password" 
                            value={password} 
                            onChange={e => setPassword(e.target.value)} 
                            placeholder="Password (min 6 chars)" 
                            required 
                            style={{ width: '100%', fontSize: '0.85rem', background: 'var(--input-bg)', border: '1px solid var(--card-border)', color: 'var(--text-color)', borderRadius: '6px', padding: '10px' }}
                        />
                        <button 
                            type="submit" 
                            style={{ width: '100%', padding: '8px', marginTop: '10px', fontSize: '0.9rem', borderRadius: '8px', fontWeight: '600' }}
                        >
                            Sign up
                        </button>
                    </form>
                </div>

                <div className="auth-card-sub">
                    <span style={{ color: 'var(--text-color)', fontSize: '0.85rem' }}>Have an account? </span>
                    <Link to="/login" style={{ color: 'var(--primary-accent)', fontWeight: '600', fontSize: '0.85rem', textDecoration: 'none' }}>
                        Log in
                    </Link>
                </div>

            </div>
        </div>
    );
};

