import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await login(username, password);
            if (res.success) {
                navigate('/');
            } else {
                setError(res.message || 'Login failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Login failed');
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--bg-color)', color: 'var(--text-color)' }}>
            <nav style={{ padding: '20px 40px', display: 'flex', alignItems: 'center' }}>
                <span className="brand-text" style={{ fontSize: '2.2rem', color: 'var(--primary-accent)', fontWeight: 'bold' }}>CD-Social</span>
            </nav>

            <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
                <div style={{ width: '100%', maxWidth: '350px' }}>
                    <div className="card" style={{ padding: '30px', display: 'flex', flexDirection: 'column', borderRadius: '8px' }}>
                        <h1 style={{ margin: '0 0 4px 0', fontSize: '2rem', fontWeight: 600 }}>Sign in</h1>
                        <p style={{ margin: '0 0 24px 0', fontSize: '0.95rem', color: 'var(--text-muted)' }}>Stay updated on your professional world</p>
                        
                        {error && <p style={{ color: 'var(--danger-color)', fontSize: '0.9rem', marginBottom: '16px', fontWeight: 500 }}>{error}</p>}
                        
                        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
                            <input 
                                id="username"
                                name="username"
                                type="text" 
                                value={username} 
                                onChange={e => setUsername(e.target.value)} 
                                placeholder="Username or Email" 
                                autoComplete="username"
                                required 
                                style={{ width: '100%', fontSize: '1rem', background: 'transparent', border: '1px solid var(--text-muted)', color: 'var(--text-color)', borderRadius: '4px', padding: '14px', boxSizing: 'border-box' }}
                            />
                            <input 
                                id="password"
                                name="password"
                                type="password" 
                                value={password} 
                                onChange={e => setPassword(e.target.value)} 
                                placeholder="Password" 
                                autoComplete="current-password"
                                required 
                                style={{ width: '100%', fontSize: '1rem', background: 'transparent', border: '1px solid var(--text-muted)', color: 'var(--text-color)', borderRadius: '4px', padding: '14px', boxSizing: 'border-box' }}
                            />
                            
                            <a href="#" onClick={(e) => e.preventDefault()} style={{ fontSize: '0.95rem', color: 'var(--primary-accent)', textDecoration: 'none', fontWeight: 600, alignSelf: 'flex-start', marginTop: '-4px' }}>
                                Forgot password?
                            </a>

                            <button 
                                type="submit" 
                                style={{ width: '100%', padding: '14px', marginTop: '10px', fontSize: '1rem', borderRadius: '24px', fontWeight: '600', background: 'var(--primary-accent)', color: 'white', border: 'none', cursor: 'pointer' }}
                            >
                                Sign in
                            </button>
                        </form>

                        <div style={{ display: 'flex', alignItems: 'center', width: '100%', margin: '20px 0' }}>
                            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--card-border)' }}></div>
                            <span style={{ margin: '0 12px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>or</span>
                            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--card-border)' }}></div>
                        </div>

                        <p style={{ textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-color)', margin: 0 }}>
                            By clicking Sign in, you agree to our Terms, Privacy Policy, and Cookie Policy.
                        </p>
                    </div>

                    <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '1rem' }}>
                        <span style={{ color: 'var(--text-color)' }}>New to CD-Social? </span>
                        <Link to="/register" style={{ color: 'var(--primary-accent)', fontWeight: '600', textDecoration: 'none' }}>
                            Join now
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

