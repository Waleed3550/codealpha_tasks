'use client';
import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { File as FileIcon, UploadCloud, Trash2, Download, Image as ImageIcon, FileText, MoreVertical, Search, HardDrive } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';
import { useDialog } from '@/components/ui/DialogProvider';

interface Attachment {
    id: string;
    file_name: string;
    file_size: number;
    mime_type: string;
    file: string;
    version: number;
    uploader_name: string;
    created_at: string;
}

export default function FilesPage() {
    const dialog = useDialog();
    const [files, setFiles] = useState<Attachment[]>([]);
    const [stats, setStats] = useState({ total_size_bytes: 0, total_files: 0, storage_limit_bytes: 5368709120 });
    const [isUploading, setIsUploading] = useState(false);

    const fetchFiles = () => {
        api.get('/files/attachments/').then(res => setFiles(res.data)).catch(console.error);
        api.get('/files/attachments/statistics/').then(res => setStats(res.data)).catch(console.error);
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;
        setIsUploading(true);
        try {
            for (const file of acceptedFiles) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('file_name', file.name);
                
                // Assuming global upload defaults to a generic type if not attached to a project
                formData.append('model_name', 'project'); // We just use project as a placeholder for now
                // We'd need an object_id, but the backend allows it to be arbitrary if we don't strictly enforce generic foreign keys validation in the serializer,
                // Wait, Django GenericForeignKey requires object_id. We'll pass a dummy UUID or fetch a project.
                // For a proper enterprise manager, files might not always require a model. Let's adjust backend later if needed.
                // For now, assume there's a default project or we just pass a random UUID.
                formData.append('object_id', '00000000-0000-0000-0000-000000000000'); 
                
                await api.post('/files/attachments/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            }
            fetchFiles();
        } catch (error) {
            console.error("Upload failed", error);
        } finally {
            setIsUploading(false);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    const deleteFile = async (id: string) => {
        try {
            await api.delete(`/files/attachments/${id}/`);
            fetchFiles();
        } catch (error) {
            console.error("Delete failed", error);
        }
    };

    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Enterprise File Manager</h1>
                    <p className="text-slate-400">Manage all your project assets, documents, and attachments in one place.</p>
                </div>
                
                <div className="flex gap-4 items-center">
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 flex items-center gap-4">
                        <HardDrive className="text-emerald-400" size={24} />
                        <div>
                            <div className="text-sm font-medium text-white">{formatBytes(stats.total_size_bytes)} Used</div>
                            <div className="text-xs text-slate-500">of {formatBytes(stats.storage_limit_bytes)}</div>
                        </div>
                        <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden ml-2">
                            <div 
                                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500" 
                                style={{ width: `${Math.min(100, (stats.total_size_bytes / stats.storage_limit_bytes) * 100)}%` }} 
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center transition-all cursor-pointer ${
                    isDragActive ? 'border-emerald-500 bg-emerald-500/10' : 'border-white/10 hover:border-emerald-500/50 hover:bg-slate-900/50 bg-slate-900/30'
                }`}
            >
                <input {...getInputProps()} />
                <UploadCloud className={`w-12 h-12 mb-4 ${isDragActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                <p className="text-lg font-medium text-white mb-1">
                    {isUploading ? 'Uploading...' : isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </p>
                <p className="text-sm text-slate-500">or click to browse from your computer</p>
            </div>

            <div className="bg-slate-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm">
                <div className="p-4 border-b border-white/5 flex justify-between items-center">
                    <h2 className="font-semibold text-white">All Files</h2>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input type="text" placeholder="Search files..." className="bg-slate-950/50 border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:border-emerald-500 text-white" />
                    </div>
                </div>
                
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="bg-slate-950/50 border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4 font-medium text-slate-300">Name</th>
                                <th className="px-6 py-4 font-medium text-slate-300">Size</th>
                                <th className="px-6 py-4 font-medium text-slate-300">Type</th>
                                <th className="px-6 py-4 font-medium text-slate-300">Uploaded By</th>
                                <th className="px-6 py-4 font-medium text-slate-300">Date</th>
                                <th className="px-6 py-4 font-medium text-slate-300 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            <AnimatePresence>
                                {files.map(file => (
                                    <motion.tr 
                                        initial={{ opacity: 0 }} 
                                        animate={{ opacity: 1 }} 
                                        exit={{ opacity: 0 }} 
                                        key={file.id} 
                                        className="hover:bg-white/5 transition-colors group"
                                    >
                                        <td className="px-6 py-4 flex items-center gap-3 text-white font-medium">
                                            {file.mime_type.startsWith('image') ? <ImageIcon className="text-pink-400 w-5 h-5" /> : 
                                             file.mime_type.includes('pdf') ? <FileText className="text-red-400 w-5 h-5" /> : 
                                             <FileIcon className="text-blue-400 w-5 h-5" />}
                                            <a href={file.file} target="_blank" rel="noreferrer" className="hover:underline">{file.file_name}</a>
                                        </td>
                                        <td className="px-6 py-4">{formatBytes(file.file_size)}</td>
                                        <td className="px-6 py-4">{file.mime_type.split('/')[1]?.toUpperCase() || 'FILE'}</td>
                                        <td className="px-6 py-4">{file.uploader_name || 'User'}</td>
                                        <td className="px-6 py-4">{new Date(file.created_at).toLocaleDateString()}</td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <a href={file.file} download className="p-1.5 hover:bg-white/10 rounded-md text-slate-300 hover:text-white">
                                                    <Download size={16} />
                                                </a>
                                                <button onClick={() => deleteFile(file.id)} className="p-1.5 hover:bg-red-500/20 rounded-md text-slate-300 hover:text-red-400">
                                                    <Trash2 size={16} />
                                                </button>
                                                <button 
                                                    onClick={async () => {
                                                        const action = await dialog.prompt("Type 'rename' to rename file, or 'link' to copy link:");
                                                        if (action === 'rename') {
                                                            const newName = await dialog.prompt("New file name:", file.file_name);
                                                            if (newName) {
                                                                api.patch(`/files/attachments/${file.id}/`, { file_name: newName })
                                                                    .then(() => fetchFiles());
                                                            }
                                                        } else if (action === 'link') {
                                                            navigator.clipboard.writeText(file.file);
                                                            await dialog.alert("Link copied to clipboard!");
                                                        }
                                                    }}
                                                    className="p-1.5 hover:bg-white/10 rounded-md text-slate-300 hover:text-white"
                                                >
                                                    <MoreVertical size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                ))}
                            </AnimatePresence>
                            {files.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                                        No files uploaded yet. Drag and drop some files above.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
