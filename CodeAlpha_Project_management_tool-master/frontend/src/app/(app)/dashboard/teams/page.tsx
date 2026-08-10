'use client';
import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Mail, Shield, MoreHorizontal, CheckCircle2, XCircle, Trash2, Power } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

export default function TeamsPage() {
    const dialog = useDialog();
    const [members, setMembers] = useState<any[]>([]);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newEmail, setNewEmail] = useState('');
    const [newFirstName, setNewFirstName] = useState('');
    const [newLastName, setNewLastName] = useState('');
    const [newPassword, setNewPassword] = useState('');

    const fetchUsers = () => {
        api.get('/users/').then(res => setMembers(res.data.results || res.data || [])).catch(console.error);
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleAddUser = (e: React.FormEvent) => {
        e.preventDefault();
        // Uses the AuthViewSet register endpoint to add a user
        api.post('/auth/register/', { 
            email: newEmail, 
            password: newPassword, 
            first_name: newFirstName,
            last_name: newLastName
        }).then(() => {
            setIsAddModalOpen(false);
            setNewEmail(''); setNewPassword(''); setNewFirstName(''); setNewLastName('');
            fetchUsers();
            dialog.alert("User created successfully!");
        }).catch(err => {
            dialog.alert(JSON.stringify(err.response?.data || "Failed to create user."));
        });
    };

    const toggleStatus = async (id: string, currentStatus: boolean) => {
        if (await dialog.confirm(`Are you sure you want to ${currentStatus ? 'suspend' : 'activate'} this user?`)) {
            api.post(`/users/${id}/${currentStatus ? 'deactivate' : 'activate'}/`)
                .then(() => fetchUsers())
                .catch(err => dialog.alert("You don't have permission to do this."));
        }
    };

    const handleDelete = async (id: string) => {
        if (await dialog.confirm("Are you sure you want to permanently delete this user?")) {
            api.delete(`/users/${id}/`)
                .then(() => fetchUsers())
                .catch(err => dialog.alert("You don't have permission to delete this user."));
        }
    };

    const handleRoleChange = async (id: string, newRole: string) => {
        if (await dialog.confirm(`Are you sure you want to change this user's role?`)) {
            api.post(`/users/${id}/change_role/`, { role: newRole })
                .then(() => fetchUsers())
                .catch(err => dialog.alert("Failed to change role or you do not have permission."));
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6 pb-12 relative">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">User & Team Management</h1>
                    <p className="text-slate-400 mt-1">Manage workspace members, roles, and system access.</p>
                </div>
                <button onClick={() => setIsAddModalOpen(true)} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20">
                    <UserPlus size={18} /> Add New User
                </button>
            </div>

            <div className="bg-slate-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm shadow-2xl">
                <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-slate-800/30 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <div className="col-span-4">Member</div>
                    <div className="col-span-3">System Role</div>
                    <div className="col-span-2">Status</div>
                    <div className="col-span-3 text-right">Actions</div>
                </div>
                
                <div className="divide-y divide-white/5">
                    {members.map((member, i) => (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.05 }}
                            key={member.id} 
                            className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-slate-800/40 transition-colors group"
                        >
                            <div className="col-span-4 flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shadow-lg ${member.is_active ? 'bg-emerald-500' : 'bg-slate-600'}`}>
                                    {(member.first_name || member.email || 'U').charAt(0).toUpperCase()}
                                </div>
                                <div className="truncate pr-2">
                                    <div className={`font-semibold transition-colors ${member.is_active ? 'text-white group-hover:text-emerald-300' : 'text-slate-500'}`}>
                                        {member.first_name} {member.last_name}
                                    </div>
                                    <div className="text-xs text-slate-400 flex items-center gap-1 mt-0.5 truncate">
                                        <Mail size={12} /> {member.email}
                                    </div>
                                </div>
                            </div>
                            <div className="col-span-3">
                                <div className="flex items-center gap-2 bg-slate-800/50 w-fit px-2 py-1 rounded-lg border border-white/5 focus-within:border-emerald-500/50 transition-colors">
                                    <Shield size={14} className={member.is_superuser ? 'text-pink-400' : 'text-slate-500'} />
                                    <select 
                                        className="bg-transparent text-sm text-slate-300 focus:outline-none cursor-pointer appearance-none pr-4"
                                        value={member.is_superuser ? 'superadmin' : (member.is_staff ? 'admin' : 'employee')}
                                        onChange={(e) => handleRoleChange(member.id, e.target.value)}
                                    >
                                        <option value="superadmin" className="bg-slate-800">Super Admin</option>
                                        <option value="admin" className="bg-slate-800">Admin</option>
                                        <option value="employee" className="bg-slate-800">Employee</option>
                                    </select>
                                </div>
                            </div>
                            <div className="col-span-2">
                                <span className={`px-2.5 py-1 rounded-full border text-xs font-medium flex items-center w-fit gap-1 ${
                                    member.is_active ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                                }`}>
                                    {member.is_active ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                                    {member.is_active ? 'Active' : 'Suspended'}
                                </span>
                            </div>
                            <div className="col-span-3 flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    title={member.is_active ? "Suspend User" : "Activate User"}
                                    onClick={() => toggleStatus(member.id, member.is_active)}
                                    className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-md transition-colors"
                                >
                                    <Power size={16} className={member.is_active ? "text-yellow-400" : "text-emerald-400"} />
                                </button>
                                <button 
                                    title="Edit User"
                                    onClick={async () => {
                                        const newName = await dialog.prompt("Enter new First Name:", member.first_name);
                                        if (newName) {
                                            api.patch(`/users/${member.id}/`, { first_name: newName }).then(fetchUsers);
                                        }
                                    }}
                                    className="p-1.5 text-slate-400 hover:text-emerald-300 hover:bg-white/10 rounded-md transition-colors"
                                >
                                    <MoreHorizontal size={16} />
                                </button>
                                <button 
                                    title="Delete User"
                                    onClick={() => handleDelete(member.id)}
                                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/20 rounded-md transition-colors"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Add User Modal */}
            <AnimatePresence>
                {isAddModalOpen && (
                    <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="bg-slate-900/90 border border-white/10 rounded-3xl p-8 w-full max-w-md shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-xl relative overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-80" />
                            <h2 className="text-2xl font-bold text-white mb-8 tracking-tight">Add New User</h2>
                            <form onSubmit={handleAddUser} className="space-y-4">
                                <div className="flex gap-4">
                                    <div className="flex-1">
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">First Name</label>
                                        <input type="text" required value={newFirstName} onChange={e => setNewFirstName(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                    </div>
                                    <div className="flex-1">
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">Last Name</label>
                                        <input type="text" required value={newLastName} onChange={e => setNewLastName(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">Email Address</label>
                                    <input type="email" required value={newEmail} onChange={e => setNewEmail(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">Temporary Password</label>
                                    <input type="password" required value={newPassword} onChange={e => setNewPassword(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                </div>
                                <div className="pt-6 flex justify-end gap-3">
                                    <button type="button" onClick={() => setIsAddModalOpen(false)} className="px-5 py-2.5 text-sm font-medium text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-xl transition-colors">
                                        Cancel
                                    </button>
                                    <button type="submit" className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-emerald-500/25">
                                        Create User
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
