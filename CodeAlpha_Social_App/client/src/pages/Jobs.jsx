import { useState, useEffect } from 'react';
import { Briefcase, Search, MapPin } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export const Jobs = () => {
    const { user } = useAuth();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await api.get('/jobs/');
                setJobs(res.data.data || []);
            } catch (err) {
                console.error("Failed to load jobs:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchJobs();
    }, []);

    if (loading) return <p className="container">Loading jobs...</p>;

    return (
        <div className="container">
            <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Briefcase size={28} /> Jobs Board
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {jobs.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)' }}>No jobs posted yet.</p>
                ) : (
                    jobs.map(job => (
                        <div key={job.id} className="card" style={{ padding: '20px' }}>
                            <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem' }}>{job.title}</h3>
                            <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '16px' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <Briefcase size={16} /> {job.company}
                                </span>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <MapPin size={16} /> {job.location}
                                </span>
                            </div>
                            <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>
                                {job.description}
                            </p>
                            <button style={{ marginTop: '16px', padding: '8px 16px', background: 'var(--primary-accent)', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
                                Apply Now
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
