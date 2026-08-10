'use client';
import React, { useState, useEffect } from 'react';
import { Building, Plus, Settings, Trash2, Users, MoreHorizontal, Edit2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

export default function OrganizationsPage() {
    const dialog = useDialog();
    const [organizations, setOrganizations] = useState<any[]>([]);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [currentOrg, setCurrentOrg] = useState<any>(null);
    const [orgName, setOrgName] = useState('');
    const [orgDomain, setOrgDomain] = useState('');
    const [stats, setStats] = useState<Record<string, any>>({});

    const fetchOrgs = () => {
        api.get('/organizations/').then(res => {
            const orgs = res.data.results || res.data || [];
            setOrganizations(orgs);
            // Fetch stats for each
            orgs.forEach((o: any) => {
                api.get(`/organizations/${o.id}/statistics/`).then(sRes => {
                    setStats(prev => ({ ...prev, [o.id]: sRes.data }));
                });
            });
        }).catch(console.error);
    };

    useEffect(() => {
        fetchOrgs();
    }, []);

    const handleCreate = (e: React.FormEvent) => {
        e.preventDefault();
        api.post('/organizations/', { name: orgName, domain: orgDomain })
            .then(() => {
                setIsAddModalOpen(false);
                setOrgName(''); setOrgDomain('');
                fetchOrgs();
            }).catch(err => dialog.alert("Failed to create. Check permissions or missing fields."));
    };

    const handleUpdate = (e: React.FormEvent) => {
        e.preventDefault();
        api.patch(`/organizations/${currentOrg.id}/`, { name: orgName, domain: orgDomain })
            .then(() => {
                setIsEditModalOpen(false);
                setCurrentOrg(null);
                setOrgName(''); setOrgDomain('');
                fetchOrgs();
            }).catch(err => dialog.alert("Failed to update."));
    };

    const handleDelete = async (id: string) => {
        if (await dialog.confirm("Are you sure you want to permanently delete this organization? All workspaces and data will be lost!")) {
            api.delete(`/organizations/${id}/`)
                .then(() => fetchOrgs())
                .catch(err => dialog.alert("You don't have permission to delete this organization."));
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6 pb-12 relative">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Organization Management</h1>
                    <p className="text-slate-400 mt-1">Manage tenants, workspaces, and domains across the platform.</p>
                </div>
                <button onClick={() => setIsAddModalOpen(true)} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20">
                    <Plus size={18} /> New Organization
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {organizations.map((org, i) => (
                    <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        key={org.id} 
                        className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm shadow-xl group hover:border-emerald-500/30 transition-colors flex flex-col"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400">
                                    <Building size={24} />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-lg text-white group-hover:text-emerald-300 transition-colors">{org.name}</h3>
                                    <p className="text-xs text-slate-400">{org.domain || "No domain set"}</p>
                                </div>
                            </div>
                            
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    onClick={() => {
                                        setCurrentOrg(org);
                                        setOrgName(org.name);
                                        setOrgDomain(org.domain || '');
                                        setIsEditModalOpen(true);
                                    }}
                                    className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-md transition-colors"
                                >
                                    <Edit2 size={16} />
                                </button>
                                <button 
                                    onClick={() => handleDelete(org.id)}
                                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/20 rounded-md transition-colors"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 py-4 border-t border-b border-white/5 my-auto">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-white">{stats[org.id]?.workspaces_count || 0}</div>
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">Workspaces</div>
                            </div>
                            <div className="text-center border-l border-r border-white/5">
                                <div className="text-2xl font-bold text-white">{stats[org.id]?.teams_count || 0}</div>
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">Teams</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-white">{stats[org.id]?.roles_count || 0}</div>
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">Roles</div>
                            </div>
                        </div>
                        
                        <div className="pt-4 flex justify-between items-center">
                            <span className="text-xs text-slate-500">ID: {org.id.split('-')[0]}</span>
                            <button className="text-xs font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors">
                                <Settings size={14} /> Org Settings
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Modal */}
            <AnimatePresence>
                {(isAddModalOpen || isEditModalOpen) && (
                    <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="bg-slate-900/90 border border-white/10 rounded-3xl p-8 w-full max-w-md shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-xl relative overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-80" />
                            <h2 className="text-2xl font-bold text-white mb-8 tracking-tight">
                                {isEditModalOpen ? "Edit Organization" : "Create Organization"}
                            </h2>
                            <form onSubmit={isEditModalOpen ? handleUpdate : handleCreate} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">Organization Name</label>
                                    <input type="text" required value={orgName} onChange={e => setOrgName(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">Domain (Optional)</label>
                                    <input type="text" placeholder="e.g. example.com" value={orgDomain} onChange={e => setOrgDomain(e.target.value)} className="w-full bg-slate-950/50 border border-white/5 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all shadow-inner" />
                                </div>
                                <div className="pt-6 flex justify-end gap-3">
                                    <button type="button" onClick={() => { setIsAddModalOpen(false); setIsEditModalOpen(false); setCurrentOrg(null); }} className="px-5 py-2.5 text-sm font-medium text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-xl transition-colors">
                                        Cancel
                                    </button>
                                    <button type="submit" className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-emerald-500/25">
                                        {isEditModalOpen ? "Save Changes" : "Create Organization"}
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
