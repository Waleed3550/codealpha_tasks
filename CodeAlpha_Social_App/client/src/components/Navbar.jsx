import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Home, Compass, Film, User, Settings, Sun, Moon, LogOut, Briefcase, MessageCircle, Bell, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Navbar = () => {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null;

    const navItems = [
        { label: 'Home', path: '/', icon: Home },
        { label: 'Network', path: '/network', icon: Users },
        { label: 'Jobs', path: '/jobs', icon: Briefcase },
        { label: 'Messages', path: '/messages', icon: MessageCircle },
        { label: 'Profile', path: `/profile/${user.id}`, icon: User, isProfile: true },
    ];

    return (
        <nav className="navbar" style={{ position: 'fixed', width: '100%', top: 0, zIndex: 1000, height: '60px', boxSizing: 'border-box', backgroundColor: 'var(--card-bg)', borderBottom: '1px solid var(--card-border)', display: 'flex', alignItems: 'center', padding: '0 20px' }}>
            <div style={{ display: 'flex', width: '100%', maxWidth: '1128px', margin: '0 auto', alignItems: 'center', justifyContent: 'space-between' }}>
                <Link to="/" className="brand-text" style={{ fontSize: '1.8rem', textDecoration: 'none', lineHeight: 1 }}>CD-Social</Link>
                
                <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                    {navItems.map(item => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link key={item.label} to={item.path} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', textDecoration: 'none', color: isActive ? 'var(--text-color)' : 'var(--text-muted)' }}>
                                {item.isProfile ? (
                                    user.avatar ? <img src={user.avatar} style={{ width: 24, height: 24, borderRadius: '50%', objectFit: 'cover' }} /> : <div style={{ width: 24, height: 24, borderRadius: '50%', backgroundColor: 'var(--input-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600 }}>{user.username.charAt(0).toUpperCase()}</div>
                                ) : (
                                    <Icon size={24} strokeWidth={isActive ? 2.5 : 1.8} />
                                )}
                                <span style={{ fontSize: '0.75rem', fontWeight: isActive ? 600 : 400 }}>{item.label}</span>
                            </Link>
                        );
                    })}
                </div>

                <div style={{ display: 'flex', gap: '16px', alignItems: 'center', borderLeft: '1px solid var(--card-border)', paddingLeft: '16px' }}>
                    <button onClick={toggleTheme} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                    <Link to="/edit-profile" style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
                        <Settings size={20} />
                    </Link>
                    <button onClick={handleLogout} title="Logout" style={{ background: 'transparent', color: 'var(--text-muted)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                        <LogOut size={20} />
                    </button>
                </div>
            </div>
        </nav>
    );
};

