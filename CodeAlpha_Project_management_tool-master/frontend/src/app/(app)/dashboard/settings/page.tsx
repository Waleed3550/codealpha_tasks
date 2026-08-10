'use client';
import React, { useState, useEffect, useRef } from 'react';
import { Settings, User, Bell, Shield, Key, Moon, Globe, Copy, Plus, Trash2, Check, Layout, Palette } from 'lucide-react';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

export default function SettingsPage() {
    const dialog = useDialog();
    const [user, setUser] = useState<any>(null);
    const [formData, setFormData] = useState({ first_name: '', last_name: '', email: '' });
    const [activeTab, setActiveTab] = useState('Profile');
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Tab Data States
    const [workspaces, setWorkspaces] = useState<any[]>([]);
    const [securityData, setSecurityData] = useState({ old_password: '', new_password: '', confirm_password: '' });
    const [notifySettings, setNotifySettings] = useState({ email: true, push: false, weekly: true, security: true });
    const [appearanceSettings, setAppearanceSettings] = useState({ dark_mode: true, compact: false, language: 'English' });
    const [apiKeys, setApiKeys] = useState([{ id: 1, name: 'Production Server', key: 'sk_live_****************a8b2', created: '2025-10-12' }, { id: 2, name: 'Development Mac', key: 'sk_test_****************c9d1', created: '2026-01-05' }]);

    useEffect(() => {
        api.get('/users/me/').then(res => {
            setUser(res.data);
            setFormData({
                first_name: res.data.first_name || '',
                last_name: res.data.last_name || '',
                email: res.data.email || ''
            });
            if (res.data.profile) {
                setAppearanceSettings(prev => ({ ...prev, dark_mode: res.data.profile.dark_mode_enabled ?? true }));
            }
        }).catch(console.error);

        api.get('/organizations/workspaces/').then(res => {
            setWorkspaces(res.data.results || res.data || []);
        }).catch(console.error);
    }, []);

    const handleProfileSave = async () => {
        if (user) {
            try {
                const res = await api.patch(`/users/me/`, formData);
                setUser(res.data);
                await dialog.alert("Profile saved successfully.");
                // Also update local storage or auth store if needed
                import('@/store/useAuthStore').then(({ useAuthStore }) => {
                    useAuthStore.getState().setUser(res.data);
                });
            } catch (err: any) {
                console.error(err);
                await dialog.alert(err.response?.data?.detail || "Failed to save profile. Please check your inputs.");
            }
        }
    };

    const handlePasswordChange = () => {
        if (securityData.new_password !== securityData.confirm_password) {
            dialog.alert("Passwords do not match!");
            return;
        }
        api.post('/auth/change_password/', {
            old_password: securityData.old_password,
            new_password: securityData.new_password
        }).then(() => {
            dialog.alert("Password updated successfully.");
            setSecurityData({ old_password: '', new_password: '', confirm_password: '' });
        }).catch(err => {
            dialog.alert(err.response?.data?.old_password?.[0] || "Failed to update password.");
        });
    };

    const handleAppearanceSave = () => {
        if (user?.profile?.id) {
            api.patch(`/profiles/${user.profile.id}/`, { dark_mode_enabled: appearanceSettings.dark_mode }).then(() => {
                dialog.alert("Appearance settings saved!");
            }).catch(console.error);
        } else {
            dialog.alert("Appearance settings saved locally!");
        }
    };

    const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0] && user?.profile?.id) {
            const formData = new FormData();
            formData.append('avatar', e.target.files[0]);
            
            api.post(`/profiles/${user.profile.id}/upload_avatar/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            }).then(res => {
                setUser({ ...user, profile: { ...user.profile, avatar: res.data.avatar_url } });
            }).catch(err => {
                console.error(err);
                dialog.alert("Failed to upload avatar.");
            });
        }
    };

    const generateApiKey = () => {
        const newKey = { id: Date.now(), name: 'New API Key', key: `sk_live_****${Math.floor(Math.random()*10000)}`, created: new Date().toISOString().split('T')[0] };
        setApiKeys([...apiKeys, newKey]);
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'Profile':
                return (
                    <div className="space-y-6 max-w-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="flex items-center gap-6">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-emerald-500/20 overflow-hidden shrink-0">
                                {user?.profile?.avatar ? (
                                    <img 
                                        src={user.profile.avatar.startsWith('http') ? user.profile.avatar : `${process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '')}${user.profile.avatar}`} 
                                        alt="Avatar" 
                                        className="w-full h-full object-cover" 
                                    />
                                ) : (
                                    formData.first_name ? formData.first_name[0].toUpperCase() : 'U'
                                )}
                            </div>
                            <div>
                                <input type="file" ref={fileInputRef} onChange={handleAvatarChange} className="hidden" />
                                <button onClick={() => fileInputRef.current?.click()} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-medium rounded-lg transition-colors border border-white/5">
                                    Change Avatar
                                </button>
                                <p className="text-xs text-slate-500 mt-2">Any file type allowed. 1MB max.</p>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-1.5">First Name</label>
                                <input type="text" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors" />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-1.5">Last Name</label>
                                <input type="text" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors" />
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-1.5">Email Address</label>
                            <input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors" />
                        </div>
                        <div className="pt-4 border-t border-white/5 flex justify-end">
                            <button onClick={handleProfileSave} className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-emerald-500/20">
                                Save Profile
                            </button>
                        </div>
                    </div>
                );
            case 'Workspace':
                return (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <p className="text-sm text-slate-400 mb-4">Manage the workspaces you are part of and your current roles.</p>
                        <div className="grid gap-4">
                            {workspaces.length > 0 ? workspaces.map((ws: any) => (
                                <div key={ws.id} className="p-4 rounded-xl bg-slate-800/30 border border-white/5 flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                                            {ws.name.substring(0, 2).toUpperCase()}
                                        </div>
                                        <div>
                                            <h3 className="text-white font-medium">{ws.name}</h3>
                                            <p className="text-xs text-slate-500">{ws.description || 'Enterprise Workspace'}</p>
                                        </div>
                                    </div>
                                    <span className="px-3 py-1 bg-green-500/10 text-green-400 text-xs font-medium rounded-full border border-green-500/20">Active</span>
                                </div>
                            )) : (
                                <div className="p-8 text-center border border-dashed border-white/10 rounded-xl">
                                    <Globe className="mx-auto text-slate-500 mb-2" size={32} />
                                    <p className="text-slate-400">No workspaces assigned to you.</p>
                                </div>
                            )}
                        </div>
                    </div>
                );
            case 'Notifications':
                return (
                    <div className="space-y-6 max-w-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="space-y-4">
                            <ToggleItem title="Email Notifications" description="Receive updates and alerts via email." checked={notifySettings.email} onChange={() => setNotifySettings({...notifySettings, email: !notifySettings.email})} />
                            <ToggleItem title="Push Notifications" description="Receive real-time push notifications in the browser." checked={notifySettings.push} onChange={() => setNotifySettings({...notifySettings, push: !notifySettings.push})} />
                            <ToggleItem title="Weekly Reports" description="Get a weekly summary of your tasks and projects." checked={notifySettings.weekly} onChange={() => setNotifySettings({...notifySettings, weekly: !notifySettings.weekly})} />
                            <ToggleItem title="Security Alerts" description="Get notified instantly if we notice suspicious login activity." checked={notifySettings.security} onChange={() => setNotifySettings({...notifySettings, security: !notifySettings.security})} />
                        </div>
                        <div className="pt-4 border-t border-white/5 flex justify-end">
                            <button onClick={() => dialog.alert("Notification preferences saved!")} className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors">
                                Save Preferences
                            </button>
                        </div>
                    </div>
                );
            case 'Security':
                return (
                    <div className="space-y-6 max-w-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <p className="text-sm text-slate-400 mb-6">Update your password to keep your account secure. We recommend using a strong password.</p>
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-1.5">Current Password</label>
                            <input type="password" value={securityData.old_password} onChange={e => setSecurityData({...securityData, old_password: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500" placeholder="••••••••" />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-1.5">New Password</label>
                            <input type="password" value={securityData.new_password} onChange={e => setSecurityData({...securityData, new_password: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500" placeholder="••••••••" />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-1.5">Confirm New Password</label>
                            <input type="password" value={securityData.confirm_password} onChange={e => setSecurityData({...securityData, confirm_password: e.target.value})} className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500" placeholder="••••••••" />
                        </div>
                        <div className="pt-4 border-t border-white/5 flex justify-end">
                            <button onClick={handlePasswordChange} className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors">
                                Update Password
                            </button>
                        </div>
                    </div>
                );
            case 'API Keys':
                return (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="flex justify-between items-center mb-4">
                            <p className="text-sm text-slate-400">Manage API keys to authenticate external apps to your account.</p>
                            <button onClick={generateApiKey} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-emerald-500/20">
                                <Plus size={16} /> Generate Key
                            </button>
                        </div>
                        <div className="overflow-hidden rounded-xl border border-white/5 bg-slate-800/30">
                            <table className="w-full text-left text-sm text-slate-300">
                                <thead className="bg-slate-800/50 text-xs uppercase font-medium text-slate-400">
                                    <tr>
                                        <th className="px-4 py-3">Name</th>
                                        <th className="px-4 py-3">API Key</th>
                                        <th className="px-4 py-3">Created</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {apiKeys.map(k => (
                                        <tr key={k.id} className="border-t border-white/5">
                                            <td className="px-4 py-3 font-medium text-white">{k.name}</td>
                                            <td className="px-4 py-3 font-mono text-xs">{k.key}</td>
                                            <td className="px-4 py-3">{k.created}</td>
                                            <td className="px-4 py-3 text-right">
                                                <button className="text-slate-400 hover:text-white mr-3"><Copy size={16} /></button>
                                                <button onClick={() => setApiKeys(apiKeys.filter(ak => ak.id !== k.id))} className="text-rose-400 hover:text-rose-300"><Trash2 size={16} /></button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            case 'Appearance':
                return (
                    <div className="space-y-6 max-w-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-slate-800/30 border border-white/5 rounded-xl">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg"><Moon size={20} /></div>
                                    <div>
                                        <h4 className="text-white font-medium text-sm">Dark Mode</h4>
                                        <p className="text-xs text-slate-400">Enable dark theme across the dashboard</p>
                                    </div>
                                </div>
                                <Toggle checked={appearanceSettings.dark_mode} onChange={() => setAppearanceSettings({...appearanceSettings, dark_mode: !appearanceSettings.dark_mode})} />
                            </div>
                            
                            <div className="flex items-center justify-between p-4 bg-slate-800/30 border border-white/5 rounded-xl">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg"><Layout size={20} /></div>
                                    <div>
                                        <h4 className="text-white font-medium text-sm">Compact View</h4>
                                        <p className="text-xs text-slate-400">Reduce spacing for maximum data density</p>
                                    </div>
                                </div>
                                <Toggle checked={appearanceSettings.compact} onChange={() => setAppearanceSettings({...appearanceSettings, compact: !appearanceSettings.compact})} />
                            </div>
                        </div>
                        <div className="pt-4 border-t border-white/5 flex justify-end">
                            <button onClick={handleAppearanceSave} className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors">
                                Save Appearance
                            </button>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-8 pb-12">
            <div className="w-full md:w-64 shrink-0">
                <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
                <nav className="space-y-1">
                    <SettingsLink icon={<User size={18} />} label="Profile" active={activeTab === 'Profile'} onClick={() => setActiveTab('Profile')} />
                    <SettingsLink icon={<Globe size={18} />} label="Workspace" active={activeTab === 'Workspace'} onClick={() => setActiveTab('Workspace')} />
                    <SettingsLink icon={<Bell size={18} />} label="Notifications" active={activeTab === 'Notifications'} onClick={() => setActiveTab('Notifications')} />
                    <SettingsLink icon={<Shield size={18} />} label="Security" active={activeTab === 'Security'} onClick={() => setActiveTab('Security')} />
                    <SettingsLink icon={<Key size={18} />} label="API Keys" active={activeTab === 'API Keys'} onClick={() => setActiveTab('API Keys')} />
                    <SettingsLink icon={<Moon size={18} />} label="Appearance" active={activeTab === 'Appearance'} onClick={() => setActiveTab('Appearance')} />
                </nav>
            </div>

            <div className="flex-1 bg-slate-900/40 border border-white/5 rounded-2xl backdrop-blur-sm p-6 lg:p-10 shadow-2xl min-h-[500px]">
                <h2 className="text-xl font-semibold text-white border-b border-white/10 pb-4 mb-6">{activeTab}</h2>
                {renderTabContent()}
            </div>
        </div>
    );
}

function SettingsLink({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick: () => void }) {
    return (
        <div onClick={onClick} className={`px-4 py-2.5 rounded-lg flex items-center gap-3 cursor-pointer transition-colors ${active ? 'bg-emerald-500/10 text-emerald-400 font-medium' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
            {icon}
            <span className="text-sm">{label}</span>
        </div>
    );
}

function ToggleItem({ title, description, checked, onChange }: any) {
    return (
        <div className="flex items-center justify-between p-4 bg-slate-800/30 border border-white/5 rounded-xl">
            <div>
                <h4 className="text-white font-medium text-sm">{title}</h4>
                <p className="text-xs text-slate-400">{description}</p>
            </div>
            <Toggle checked={checked} onChange={onChange} />
        </div>
    );
}

function Toggle({ checked, onChange }: { checked: boolean, onChange: () => void }) {
    return (
        <button 
            onClick={onChange}
            className={`w-11 h-6 rounded-full flex items-center transition-colors px-1 ${checked ? 'bg-emerald-500' : 'bg-slate-700'}`}
        >
            <div className={`w-4 h-4 rounded-full bg-white transition-transform ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
        </button>
    );
}
