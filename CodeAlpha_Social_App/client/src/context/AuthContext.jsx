import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api/axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = sessionStorage.getItem('accessToken');
        const storedUser = sessionStorage.getItem('user');
        
        if (token && storedUser) {
            setAccessToken(token);
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        const response = await api.post('/auth/login/', { username, password });
        if (response.data.success) {
            const { access, id, username: uname, email, avatar } = response.data.data;
            const userData = { id, username: uname, email, avatar };
            
            setAccessToken(access);
            setUser(userData);
            
            sessionStorage.setItem('accessToken', access);
            sessionStorage.setItem('user', JSON.stringify(userData));
        }
        return response.data;
    };

    const register = async (username, email, password) => {
        const response = await api.post('/auth/register/', { username, email, password });
        return response.data;
    };

    const logout = () => {
        setAccessToken(null);
        setUser(null);
        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('user');
    };

    const updateUser = (newData) => {
        const updatedUser = { ...user, ...newData };
        setUser(updatedUser);
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
    };

    return (
        <AuthContext.Provider value={{ user, accessToken, loading, login, register, logout, updateUser }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
