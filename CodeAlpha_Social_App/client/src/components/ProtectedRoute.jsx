import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) return <div style={{ padding: '20px' }}>Loading auth...</div>;
    
    if (!user) return <Navigate to="/login" />;
    
    return children;
};
