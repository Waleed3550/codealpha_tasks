import { Link } from 'react-router-dom';
import { Heart, MessageCircle, Send, Bookmark, Trash2, MoreHorizontal } from 'lucide-react';
import { timeAgo } from '../utils/timeAgo';

export const PostCard = ({ post, onLike, onDelete, isAuthor, hideCommentLink }) => {
    const getInitial = (name) => name ? name.charAt(0).toUpperCase() : '?';

    const handleShare = () => {
        const postUrl = `${window.location.origin}/post/${post.id}`;
        navigator.clipboard.writeText(postUrl).then(() => {
            alert('Link copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy link.');
        });
    };

    return (
        <div className="card">
            {/* Header */}
            <div className="card-header" style={{ justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="avatar-ring">
                        <div className="avatar-ring-inner">
                            {post.author.avatar ? (
                                <img src={post.author.avatar} alt="Avatar" style={{ width: 32, height: 32, borderRadius: '50%', objectFit: 'cover', display: 'block' }} />
                            ) : (
                                <div style={{ width: 32, height: 32, borderRadius: '50%', backgroundColor: 'var(--input-bg)', color: 'var(--text-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.9rem' }}>
                                    {getInitial(post.author.username)}
                                </div>
                            )}
                        </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <Link to={`/profile/${post.author.id}`} className="username" style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-color)', textDecoration: 'none' }}>
                            {post.author.username}
                        </Link>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            {timeAgo(post.created_at)}
                        </span>
                    </div>
                </div>

                {isAuthor && onDelete ? (
                    <button onClick={() => onDelete(post.id)} className="danger" style={{ display: 'flex', alignItems: 'center', padding: '5px 8px', borderRadius: '4px', fontSize: '0.8rem' }}>
                        <Trash2 size={15} />
                    </button>
                ) : (
                    <MoreHorizontal size={20} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
                )}
            </div>
            
            {/* Media */}
            {(post.image || post.video) && (
                <div className="card-media">
                    {post.image && <img src={post.image} alt="Post" />}
                    {post.video && <video src={post.video} controls />}
                </div>
            )}
            
            {/* Actions */}
            <div className="card-actions" style={{ justifyContent: 'space-between', padding: '10px 14px 4px' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <button onClick={() => onLike && onLike(post.id)} className={`like-btn ${post.is_liked_by_me ? 'liked' : ''}`}>
                        <Heart size={24} strokeWidth={post.is_liked_by_me ? 0 : 2} fill={post.is_liked_by_me ? "#ff3040" : "none"} color={post.is_liked_by_me ? "#ff3040" : "var(--text-color)"} />
                    </button>
                    
                    {!hideCommentLink ? (
                        <Link to={`/post/${post.id}`} style={{ display: 'flex', alignItems: 'center', color: 'var(--text-color)', cursor: 'pointer', textDecoration: 'none' }}>
                            <MessageCircle size={24} strokeWidth={2} color="var(--text-color)" />
                        </Link>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-color)' }}>
                            <MessageCircle size={24} strokeWidth={2} color="var(--text-color)" />
                        </div>
                    )}
                    
                    <Send size={22} strokeWidth={2} color="var(--text-color)" style={{ cursor: 'pointer' }} onClick={handleShare} />
                </div>

                <Bookmark size={24} strokeWidth={2} color="var(--text-color)" style={{ cursor: 'pointer' }} />
            </div>

            {/* Likes count & caption */}
            <div className="card-content">
                <div style={{ fontWeight: 600, fontSize: '0.88rem', margin: '4px 0 6px 0', color: 'var(--text-color)' }}>
                    {post.like_count} {post.like_count === 1 ? 'like' : 'likes'}
                </div>

                <p className="post-content" style={{ margin: 0 }}>
                    <Link to={`/profile/${post.author.id}`} style={{ fontWeight: 600, color: 'var(--text-color)', marginRight: '6px', textDecoration: 'none' }}>
                        {post.author.username}
                    </Link>
                    <span style={{ color: 'var(--text-color)' }}>{post.content}</span>
                </p>

                {!hideCommentLink && post.comment_count > 0 && (
                    <Link to={`/post/${post.id}`} style={{ display: 'block', marginTop: '6px', fontSize: '0.82rem', color: 'var(--text-muted)', textDecoration: 'none' }}>
                        View all {post.comment_count} {post.comment_count === 1 ? 'comment' : 'comments'}
                    </Link>
                )}
            </div>
        </div>
    );
};


