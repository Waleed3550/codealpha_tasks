import { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

export const StoryViewer = ({ stories, initialIndex, onClose }) => {
    const [currentIndex, setCurrentIndex] = useState(initialIndex);

    const handlePrev = (e) => {
        e.stopPropagation();
        if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
    };

    const handleNext = (e) => {
        e.stopPropagation();
        if (currentIndex < stories.length - 1) setCurrentIndex(currentIndex + 1);
        else onClose(); // Close on last story next
    };

    const currentStory = stories[currentIndex];

    if (!currentStory) return null;

    return (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.9)', zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={onClose}>
            <button onClick={onClose} style={{ position: 'absolute', top: '20px', right: '20px', background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>
                <X size={32} />
            </button>
            
            <button onClick={handlePrev} style={{ position: 'absolute', left: '20px', background: 'rgba(255,255,255,0.2)', border: 'none', color: 'white', borderRadius: '50%', padding: '12px', cursor: 'pointer', visibility: currentIndex > 0 ? 'visible' : 'hidden' }}>
                <ChevronLeft size={32} />
            </button>
            
            <div style={{ position: 'relative', width: '100%', maxWidth: '400px', height: '80vh', backgroundColor: '#111', borderRadius: '12px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }} onClick={e => e.stopPropagation()}>
                {/* Progress bar mock */}
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', display: 'flex', gap: '4px', padding: '10px', zIndex: 10 }}>
                    {stories.map((s, idx) => (
                        <div key={s.id} style={{ flex: 1, backgroundColor: idx <= currentIndex ? 'white' : 'rgba(255,255,255,0.3)', borderRadius: '2px', height: '2px' }} />
                    ))}
                </div>
                
                {/* Author Info */}
                <div style={{ position: 'absolute', top: '20px', left: '16px', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 10 }}>
                    {currentStory.author.avatar ? (
                        <img src={currentStory.author.avatar} alt="Avatar" style={{ width: 32, height: 32, borderRadius: '50%', objectFit: 'cover' }} />
                    ) : (
                        <div style={{ width: 32, height: 32, borderRadius: '50%', backgroundColor: 'var(--primary-accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.9rem' }}>
                            {currentStory.author.username.charAt(0).toUpperCase()}
                        </div>
                    )}
                    <span style={{ color: 'white', fontWeight: 600, fontSize: '0.9rem', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>{currentStory.author.username}</span>
                </div>

                {/* Content */}
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#000' }}>
                    {currentStory.video ? (
                        <video src={currentStory.video} autoPlay style={{ width: '100%', maxHeight: '100%', objectFit: 'contain' }} onEnded={handleNext} />
                    ) : (
                        <img src={currentStory.image} alt="Story" style={{ width: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                    )}
                </div>
            </div>

            <button onClick={handleNext} style={{ position: 'absolute', right: '20px', background: 'rgba(255,255,255,0.2)', border: 'none', color: 'white', borderRadius: '50%', padding: '12px', cursor: 'pointer', visibility: currentIndex < stories.length - 1 ? 'visible' : 'hidden' }}>
                <ChevronRight size={32} />
            </button>
        </div>
    );
};
