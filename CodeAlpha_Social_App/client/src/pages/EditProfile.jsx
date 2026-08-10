import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export const EditProfile = () => {
    const { user, updateUser } = useAuth();
    const navigate = useNavigate();
    const [bio, setBio] = useState('');
    const [headline, setHeadline] = useState('');
    const [experience, setExperience] = useState('');
    const [education, setEducation] = useState('');
    const [skills, setSkills] = useState('');
    const [avatar, setAvatar] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get(`/users/${user.id}/`);
                if (res.data.success) {
                    setBio(res.data.data.bio || '');
                    setHeadline(res.data.data.headline || '');
                    setExperience(res.data.data.experience || '');
                    setEducation(res.data.data.education || '');
                    setSkills(res.data.data.skills || '');
                    setAvatarPreview(res.data.data.avatar || '');
                }
            } catch (err) {
                setError('Failed to load profile.');
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [user.id]);

    const handleAvatarChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setAvatar(file);
            setAvatarPreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('bio', bio);
        formData.append('headline', headline);
        formData.append('experience', experience);
        formData.append('education', education);
        formData.append('skills', skills);
        if (avatar) formData.append('avatar', avatar);

        try {
            const res = await api.put(`/users/${user.id}/update/`, formData);
            if (res.data.success) {
                updateUser({ avatar: res.data.data.avatar });
            }
            navigate(`/profile/${user.id}`);
        } catch (err) {
            alert('Failed to update profile.');
        }
    };

    if (loading) return <p className="container">Loading...</p>;
    if (error) return <p className="container" style={{ color: 'var(--danger-color)' }}>{error}</p>;

    return (
        <div className="container card" style={{ marginTop: '20px', maxWidth: '400px' }}>
            <h2 className="serif">Edit Profile</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                    <div style={{ position: 'relative', width: '120px', height: '120px', borderRadius: '50%', overflow: 'hidden', backgroundColor: 'var(--bg-color)', border: '2px solid var(--card-border)' }}>
                        {avatarPreview ? (
                            <img src={avatarPreview} alt="Avatar Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>No Avatar</div>
                        )}
                        <label style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(0,0,0,0.6)', color: 'white', display: 'flex', justifyContent: 'center', padding: '6px', cursor: 'pointer' }}>
                            <Camera size={18} />
                            <input type="file" accept="image/*" onChange={handleAvatarChange} style={{ display: 'none' }} />
                        </label>
                    </div>
                    <span style={{ fontSize: '0.9em', color: '#666' }}>Change Avatar</span>
                </div>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    Headline:
                    <input type="text" value={headline} onChange={e => setHeadline(e.target.value)} style={{ padding: '10px', borderRadius: '4px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }} />
                </label>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    Bio:
                    <textarea value={bio} onChange={e => setBio(e.target.value)} style={{ minHeight: '100px', padding: '10px', borderRadius: '4px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }} />
                </label>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    Experience:
                    <textarea value={experience} onChange={e => setExperience(e.target.value)} style={{ minHeight: '80px', padding: '10px', borderRadius: '4px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }} />
                </label>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    Education:
                    <textarea value={education} onChange={e => setEducation(e.target.value)} style={{ minHeight: '80px', padding: '10px', borderRadius: '4px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }} />
                </label>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    Skills:
                    <input type="text" value={skills} onChange={e => setSkills(e.target.value)} placeholder="e.g. React, Python, Node.js" style={{ padding: '10px', borderRadius: '4px', border: '1px solid var(--card-border)', background: 'var(--input-bg)', color: 'var(--text-color)' }} />
                </label>
                <button type="submit" style={{ padding: '12px' }}>Save Changes</button>
            </form>
        </div>
    );
};
