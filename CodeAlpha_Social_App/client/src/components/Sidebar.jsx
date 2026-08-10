import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Compass, Film, User, Settings, Sun, Moon, LogOut, Briefcase, MessageCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Sidebar = () => {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };
    if (!user) return null;
    
    const navItems = [
        { label: 'Home', path: '/', icon: Home },
        { label: 'Reels', path: '/videos', icon: Film },
        { label: 'Jobs', path: '/jobs', icon: Briefcase },
        { label: 'Messages', path: '/messages', icon: MessageCircle },
        { label: 'Profile', path: `/profile/${user.id}`, icon: User, isProfile: true },
        { label: 'Settings', path: '/edit-profile', icon: Settings },
    ];

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '12px 16px 0 16px', borderRight: '1px solid var(--card-border)', height: '100%', backgroundColor: 'var(--sidebar-bg)' }}>
            <div style={{ padding: '12px 12px 24px 12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="brand-text" style={{ fontSize: '2.2rem', cursor: 'pointer' }}>CD-Social</span>
            </div>

            {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                    <Link 
                        key={item.label}
                        to={item.path} 
                        className="sidebar-link"
                        style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: '16px', 
                            padding: '12px', 
                            color: isActive ? 'var(--text-color)' : 'var(--text-muted)', 
                            textDecoration: 'none', 
                            fontSize: '1rem', 
                            fontWeight: isActive ? 700 : 500, 
                            borderRadius: '8px',
                        }}
                    >
                        {item.isProfile ? (
                            <div className="avatar-ring" style={{ padding: '1.5px' }}>
                                <div className="avatar-ring-inner">
                                    {user.avatar ? (
                                        <img src={user.avatar} style={{ width: 24, height: 24, borderRadius: '50%', objectFit: 'cover' }} alt="Profile" />
                                    ) : (
                                        <div style={{ width: 24, height: 24, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600 }}>
                                            {user.username.charAt(0).toUpperCase()}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <Icon size={24} color={isActive ? "var(--primary-accent)" : "var(--text-muted)"} strokeWidth={isActive ? 2.5 : 1.8} />
                        )}
                        <span>{item.label}</span>
                    </Link>
                );
            })}

            {/* Theme Toggle Button */}
            <button 
                onClick={toggleTheme}
                className="sidebar-link"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '12px',
                    marginTop: 'auto',
                    background: 'transparent',
                    color: 'var(--text-color)',
                    border: 'none',
                    textAlign: 'left',
                    width: '100%',
                    fontSize: '1rem',
                    fontWeight: 500,
                    cursor: 'pointer',
                    borderRadius: '8px'
                }}
            >
                {theme === 'dark' ? (
                    <>
                        <Sun size={24} color="#f59e0b" strokeWidth={2} />
                        <span>Light Mode</span>
                    </>
                ) : (
                    <>
                        <Moon size={24} color="#10b981" strokeWidth={2} />
                        <span>Dark Mode</span>
                    </>
                )}
            </button>

            {/* Logout Button */}
            <button 
                onClick={handleLogout}
                className="sidebar-link"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '12px',
                    marginBottom: '20px',
                    background: 'transparent',
                    color: '#ef4444',
                    border: 'none',
                    textAlign: 'left',
                    width: '100%',
                    fontSize: '1rem',
                    fontWeight: 500,
                    cursor: 'pointer',
                    borderRadius: '8px'
                }}
            >
                <LogOut size={24} color="#ef4444" strokeWidth={2} />
                <span>Logout</span>
            </button>
        </div>
    );
};


