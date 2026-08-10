import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
    accessToken: string | null;
    user: any | null;
    isAuthenticated: boolean;
    setAccessToken: (access: string) => void;
    setUser: (user: any) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            accessToken: null,
            user: null,
            isAuthenticated: false,
            
            setAccessToken: (access) => set({ 
                accessToken: access, 
                isAuthenticated: true
            }),
            
            setUser: (user) => set({ user }),
            
            logout: () => set({ 
                accessToken: null, 
                user: null,
                isAuthenticated: false 
            }),
        }),
        {
            name: 'nexus-auth-storage', // Persist auth state to localStorage securely
        }
    )
);
