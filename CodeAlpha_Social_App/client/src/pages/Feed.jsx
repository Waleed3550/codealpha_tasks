import { useState, useEffect } from 'react';
import { Image as ImageIcon, Video, X, Plus } from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { PostCard } from '../components/PostCard';
import { StoryViewer } from '../components/StoryViewer';
export const Feed = ({ filter }) => {
    const { user } = useAuth();
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [content, setContent] = useState('');
    const [image, setImage] = useState(null);
    const [video, setVideo] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [videoPreview, setVideoPreview] = useState(null);
    const [fileKey, setFileKey] = useState(Date.now());
    
    // Stories state
    const [stories, setStories] = useState([]);
    const [activeStoryIndex, setActiveStoryIndex] = useState(null);

    useEffect(() => {
        fetchFeed();
    }, []);

    const fetchFeed = async () => {
        try {
            const res = await api.get('/posts/feed/');
            setPosts(res.data.data || []);
            
            const storyRes = await api.get('/stories/');
            setStories(storyRes.data.data || []);
        } catch (err) {
            setError('Failed to load feed.');
        } finally {
            setLoading(false);
        }
    };

    const handleStoryUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        if (file.type.startsWith('video/')) {
            formData.append('video', file);
        } else {
            formData.append('image', file);
        }

        try {
            const res = await api.post('/stories/', formData);
            if (res.data.success) {
                setStories([res.data.data, ...stories]);
            }
        } catch (err) {
            console.error(err);
            alert(`Failed to upload story: ${err.response?.data?.message || err.message}`);
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setImagePreview(URL.createObjectURL(file));
        }
    };

    const handleVideoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setVideo(file);
            setVideoPreview(URL.createObjectURL(file));
        }
    };

    const clearImage = () => {
        setImage(null);
        setImagePreview(null);
    };

    const clearVideo = () => {
        setVideo(null);
        setVideoPreview(null);
    };

    const handlePost = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('content', content);
        if (image) formData.append('image', image);
        if (video) formData.append('video', video);

        try {
            const res = await api.post('/posts/', formData);
            if (res.data.success) {
                setPosts([res.data.data, ...posts]);
                setContent('');
                clearImage();
                clearVideo();
                setFileKey(Date.now()); // Reset file inputs
            }
        } catch (err) {
            console.error(err);
            alert(`Failed to post: ${err.response?.data?.message || err.message}`);
        }
    };

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

    if (loading) return <p className="container">Loading feed...</p>;
    if (error) return <p className="container" style={{ color: 'var(--danger-color)' }}>{error}</p>;

    const displayedPosts = filter === 'videos' ? posts.filter(p => p.video) : posts;

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '225px minmax(0, 550px) 300px', gap: '24px', justifyContent: 'center' }}>
            {/* Left Column - Profile Summary */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="card" style={{ padding: 0, overflow: 'hidden', textAlign: 'center' }}>
                    <div style={{ height: '60px', backgroundColor: 'var(--primary-accent)', width: '100%' }}></div>
                    <div style={{ marginTop: '-30px', display: 'flex', justifyContent: 'center' }}>
                        {user && user.avatar ? (
                            <img src={user.avatar} alt="Avatar" style={{ width: 70, height: 70, borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--card-bg)' }} />
                        ) : (
                            <div style={{ width: 70, height: 70, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.5rem', border: '3px solid var(--card-bg)' }}>
                                {user ? user.username.charAt(0).toUpperCase() : '?'}
                            </div>
                        )}
                    </div>
                    <div style={{ padding: '16px' }}>
                        <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{user ? user.username : 'User'}</h3>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>Software Engineer</p>
                    </div>
                </div>
            </div>

            {/* Middle Column - Feed */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Story Tray */}
                <div className="card" style={{ padding: '16px', display: 'flex', gap: '12px', overflowX: 'auto', background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                    {/* Add Story Button */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', cursor: 'pointer', flexShrink: 0 }}>
                        <label style={{ position: 'relative', width: 60, height: 60, borderRadius: '50%', border: '2px solid var(--card-bg)', outline: '2px solid var(--primary-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', overflow: 'hidden' }}>
                            {user && user.avatar ? (
                                <img src={user.avatar} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                                <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem' }}>
                                    {user ? user.username.charAt(0).toUpperCase() : '?'}
                                </div>
                            )}
                            <div style={{ position: 'absolute', bottom: 0, right: 0, background: 'var(--primary-accent)', borderRadius: '50%', padding: '2px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Plus size={14} color="white" strokeWidth={3} />
                            </div>
                            <input type="file" accept="image/*,video/*" onChange={handleStoryUpload} style={{ display: 'none' }} />
                        </label>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>Create Story</span>
                    </div>

                    {/* Stories List */}
                    {stories.map((story, index) => (
                        <div key={story.id} onClick={() => setActiveStoryIndex(index)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', cursor: 'pointer', flexShrink: 0 }}>
                            <div style={{ width: 60, height: 60, borderRadius: '50%', border: '2px solid var(--card-bg)', outline: '2px solid var(--primary-accent)', overflow: 'hidden' }}>
                                {story.author.avatar ? (
                                    <img src={story.author.avatar} alt="Author" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                ) : (
                                    <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem' }}>
                                        {story.author.username.charAt(0).toUpperCase()}
                                    </div>
                                )}
                            </div>
                            <span style={{ fontSize: '0.75rem' }}>{story.author.username.substring(0, 10)}</span>
                        </div>
                    ))}
                </div>

                {filter !== 'videos' && (
                    <div className="card" style={{ padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                        <form onSubmit={handlePost}>
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                                {user && user.avatar ? (
                                    <img src={user.avatar} alt="Avatar" style={{ width: 48, height: 48, borderRadius: '50%', objectFit: 'cover', flexShrink: 0 }} />
                                ) : (
                                    <div style={{ width: 48, height: 48, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem', flexShrink: 0 }}>
                                        {user ? user.username.charAt(0).toUpperCase() : '?'}
                                    </div>
                                )}
                                <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Start a post" style={{ width: '100%', minHeight: '50px', border: '1px solid var(--card-border)', borderRadius: '24px', padding: '12px 16px', background: 'transparent', outline: 'none', resize: 'none', fontSize: '0.95rem', color: 'var(--text-color)', marginTop: '2px' }} />
                            </div>
                            
                            {(imagePreview || videoPreview) && (
                                <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginTop: '12px' }}>
                                    {imagePreview && (
                                        <div style={{ position: 'relative', display: 'inline-block', maxWidth: '200px' }}>
                                            <img src={imagePreview} alt="Preview" style={{ width: '100%', borderRadius: '6px', maxHeight: '150px', objectFit: 'cover' }} />
                                            <button type="button" onClick={clearImage} style={{ position: 'absolute', top: '5px', right: '5px', background: 'rgba(0,0,0,0.7)', color: 'white', border: 'none', borderRadius: '50%', padding: '4px', cursor: 'pointer', display: 'flex' }}><X size={14} /></button>
                                        </div>
                                    )}
                                    {videoPreview && (
                                        <div style={{ position: 'relative', display: 'inline-block', maxWidth: '200px' }}>
                                            <video src={videoPreview} style={{ width: '100%', borderRadius: '6px', maxHeight: '150px', objectFit: 'cover' }} controls />
                                            <button type="button" onClick={clearVideo} style={{ position: 'absolute', top: '5px', right: '5px', background: 'rgba(0,0,0,0.7)', color: 'white', border: 'none', borderRadius: '50%', padding: '4px', cursor: 'pointer', display: 'flex' }}><X size={14} /></button>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
                                <div style={{ display: 'flex', gap: '20px' }}>
                                    <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.9rem', padding: '8px', borderRadius: '4px', transition: 'background 0.2s' }}>
                                        <ImageIcon size={20} color="#70b5f9" /> Photo
                                        <input key={`img-${fileKey}`} type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
                                    </label>
                                    <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.9rem', padding: '8px', borderRadius: '4px', transition: 'background 0.2s' }}>
                                        <Video size={20} color="#7fc15e" /> Video
                                        <input key={`vid-${fileKey}`} type="file" accept="video/*" onChange={handleVideoChange} style={{ display: 'none' }} />
                                    </label>
                                </div>
                                <button type="submit" disabled={!content.trim() && !image && !video} style={{ borderRadius: '24px', padding: '6px 18px', fontWeight: '600', fontSize: '0.9rem', background: (!content.trim() && !image && !video) ? 'var(--card-border)' : 'var(--primary-accent)', color: (!content.trim() && !image && !video) ? 'var(--text-muted)' : 'white', border: 'none', cursor: (!content.trim() && !image && !video) ? 'default' : 'pointer' }}>Post</button>
                            </div>
                        </form>
                    </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {displayedPosts.length === 0 && <p style={{ textAlign: 'center', marginTop: '40px', color: 'var(--text-muted)' }}>{filter === 'videos' ? 'No video reels to show.' : 'No posts yet.'}</p>}
                    {displayedPosts.map(post => (
                        <PostCard key={post.id} post={post} onLike={handleLike} />
                    ))}
                </div>
            </div>

            {/* Right Column - News Widget */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="card" style={{ padding: '16px' }}>
                    <h3 style={{ margin: '0 0 16px 0', fontSize: '1rem', color: 'var(--text-color)' }}>CD-Social News</h3>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <li>
                            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-color)' }}>Tech hiring surges in 2026</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Top news • 10,234 readers</div>
                        </li>
                        <li>
                            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-color)' }}>New AI tools released</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>2d ago • 5,432 readers</div>
                        </li>
                        <li>
                            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-color)' }}>Remote work trends</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>3d ago • 1,234 readers</div>
                        </li>
                    </ul>
                </div>
            </div>

            {activeStoryIndex !== null && (
                <StoryViewer 
                    stories={stories} 
                    initialIndex={activeStoryIndex} 
                    onClose={() => setActiveStoryIndex(null)} 
                />
            )}
        </div>
    );
};


