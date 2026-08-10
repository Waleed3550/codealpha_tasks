import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { PostCard } from '../components/PostCard';
import { timeAgo } from '../utils/timeAgo';

export const PostDetail = () => {
    const { id } = useParams();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [post, setPost] = useState(null);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [postRes, commentsRes] = await Promise.all([
                    api.get(`/posts/${id}/`),
                    api.get(`/posts/${id}/comments/`)
                ]);
                setPost(postRes.data.data);
                setComments(commentsRes.data.data || []);
            } catch (err) {
                setError('Failed to load post.');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const handleLike = async () => {
        try {
            const res = await api.post(`/posts/${id}/like/`);
            const liked = res.data.data.liked;
            setPost(p => ({
                ...p,
                is_liked_by_me: liked,
                like_count: liked ? p.like_count + 1 : Math.max(0, p.like_count - 1)
            }));
        } catch (err) {
            alert('Failed to like post.');
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to remove this pinned note?')) return;
        try {
            await api.delete(`/posts/${id}/`);
            navigate('/');
        } catch (err) {
            alert('Failed to delete post.');
        }
    };

    const handleComment = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post(`/posts/${id}/comments/`, { content: newComment });
            setComments([...comments, res.data.data]);
            setNewComment('');
            setPost(p => ({ ...p, comment_count: p.comment_count + 1 }));
        } catch (err) {
            alert('Failed to post comment.');
        }
    };

    if (loading) return <p className="container">Loading post...</p>;
    if (error) return <p className="container" style={{ color: 'var(--danger-color)' }}>{error}</p>;
    if (!post) return <p className="container">Post not found.</p>;

    const isAuthor = user && user.id === post.author.id;

    return (
        <div className="container">
            <PostCard 
                post={post} 
                onLike={handleLike} 
                onDelete={handleDelete}
                isAuthor={isAuthor}
                hideCommentLink={true}
            />

            <div className="card" style={{ marginTop: '20px', padding: '20px' }}>
                <form onSubmit={handleComment} style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
                    <div style={{ width: 32, height: 32, borderRadius: '50%', backgroundColor: 'var(--primary-accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.9rem', flexShrink: 0 }}>
                        {user ? user.username.charAt(0).toUpperCase() : '?'}
                    </div>
                    <input value={newComment} onChange={e => setNewComment(e.target.value)} placeholder="Add a comment..." style={{ flex: 1, padding: '8px 12px', border: 'none', borderBottom: '1px solid var(--card-border)', borderRadius: 0, backgroundColor: 'transparent', outline: 'none' }} required />
                    <button type="submit" style={{ borderRadius: '20px', padding: '6px 16px' }}>Post</button>
                </form>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {comments.length === 0 && <p style={{ color: '#888', textAlign: 'center' }}>No comments yet.</p>}
                    {comments.map(c => (
                        <div key={c.id} style={{ display: 'flex', gap: '10px' }}>
                            <div style={{ width: 28, height: 28, borderRadius: '50%', backgroundColor: 'var(--primary-accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.8rem', flexShrink: 0 }}>
                                {c.author.username.charAt(0).toUpperCase()}
                            </div>
                            <div style={{ flex: 1 }}>
                                <p className="post-content" style={{ margin: '0', fontSize: '0.95rem' }}>
                                    <Link to={`/profile/${c.author.id}`} style={{ fontWeight: 600, color: 'var(--text-color)', marginRight: '6px', textDecoration: 'none' }}>{c.author.username}</Link>
                                    {c.content}
                                </p>
                                <span style={{ fontSize: '0.75rem', color: '#888' }}>{timeAgo(c.created_at)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
