import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { PostCard } from '../components/PostCard';

export const Profile = () => {
    const { id } = useParams();
    const { user: currentUser } = useAuth();
    const [profile, setProfile] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get(`/users/${id}/`);
                setProfile(res.data.data);
                const postsRes = await api.get(`/posts/`);
                setPosts(postsRes.data.data.filter(p => p.author.id === parseInt(id)));
            } catch (err) {
                setError('Failed to load profile.');
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [id]);

    const handleLike = async (postId) => {
        try {
            const res = await api.post(`/posts/${postId}/like/`);
            const liked = res.data.data.liked;
            setPosts(posts.map(p => {
                if (p.id === postId) {
                    return {
                        ...p,
                        is_liked_by_me: liked,
                        like_count: liked ? p.like_count + 1 : Math.max(0, p.like_count - 1)
                    };
                }
                return p;
            }));
        } catch (err) {
            alert('Failed to like post.');
        }
    };

    const handleFollow = async () => {
        try {
            await api.post(`/users/${id}/follow/`);
            setProfile(p => ({ ...p, follower_count: p.follower_count + 1 }));
        } catch (err) {
            alert('Failed to follow.');
        }
    };

    const handleUnfollow = async () => {
        try {
            await api.post(`/users/${id}/unfollow/`);
            setProfile(p => ({ ...p, follower_count: Math.max(0, p.follower_count - 1) }));
        } catch (err) {
            alert('Failed to unfollow.');
        }
    };

    if (loading) return <p className="container">Loading profile...</p>;
    if (error) return <p className="container" style={{ color: 'var(--danger-color)' }}>{error}</p>;
    if (!profile) return <p className="container">Profile not found.</p>;

    const isMe = currentUser && currentUser.id === parseInt(id);

    const getInitial = (name) => name ? name.charAt(0).toUpperCase() : '?';

    return (
        <div className="container">
            <div className="card" style={{ padding: '30px', display: 'flex', alignItems: 'flex-start', gap: '30px' }}>
                {profile.avatar ? (
                    <img src={profile.avatar} alt="Avatar" style={{ width: '100px', height: '100px', borderRadius: '50%', objectFit: 'cover', flexShrink: 0 }} />
                ) : (
                    <div style={{ width: '100px', height: '100px', borderRadius: '50%', backgroundColor: 'var(--primary-accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px', fontWeight: 'bold', flexShrink: 0 }}>
                        {getInitial(profile.username)}
                    </div>
                )}
                <div style={{ flex: 1 }}>
                    <h2 className="serif username" style={{ margin: '0 0 5px 0', fontSize: '1.5rem' }}>{profile.username}</h2>
                    {profile.headline && <p style={{ margin: '0 0 10px 0', fontSize: '1.1rem', color: 'var(--text-color)', fontWeight: 500 }}>{profile.headline}</p>}
                    <div style={{ display: 'flex', gap: '20px', margin: '0 0 10px 0', color: 'var(--text-color)' }}>
                        <span><strong style={{ fontSize: '1.1rem' }}>{profile.follower_count}</strong> connections</span>
                    </div>
                    <p style={{ margin: '0 0 15px 0', fontSize: '0.95rem' }}>{profile.bio || 'No bio yet.'}</p>
                    
                    {profile.experience && (
                        <div style={{ marginBottom: '15px' }}>
                            <h4 style={{ margin: '0 0 5px 0' }}>Experience</h4>
                            <p style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{profile.experience}</p>
                        </div>
                    )}
                    {profile.education && (
                        <div style={{ marginBottom: '15px' }}>
                            <h4 style={{ margin: '0 0 5px 0' }}>Education</h4>
                            <p style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{profile.education}</p>
                        </div>
                    )}
                    {profile.skills && (
                        <div style={{ marginBottom: '15px' }}>
                            <h4 style={{ margin: '0 0 5px 0' }}>Skills</h4>
                            <p style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{profile.skills}</p>
                        </div>
                    )}
                    
                    {!isMe && (
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button onClick={handleFollow} style={{ borderRadius: '20px', padding: '6px 24px', fontWeight: 'bold' }}>Follow</button>
                            <button onClick={handleUnfollow} className="secondary" style={{ borderRadius: '20px', padding: '6px 24px', fontWeight: 'bold' }}>Unfollow</button>
                        </div>
                    )}
                </div>
            </div>

            <h3 className="serif" style={{ margin: '30px 0 15px 0' }}>Posts</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0px' }}>
                {posts.length === 0 && <p style={{ color: '#888', textAlign: 'center', marginTop: '20px' }}>No posts yet.</p>}
                {posts.map(post => (
                    <PostCard key={post.id} post={post} onLike={handleLike} />
                ))}
            </div>
        </div>
    );
};
