import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export const useProjects = (workspaceId?: string) => {
    return useQuery({
        queryKey: ['projects', workspaceId],
        queryFn: async () => {
            const params = workspaceId ? { workspace: workspaceId } : {};
            const { data } = await api.get('/projects/', { params });
            return data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};

export const useProject = (id: string) => {
    return useQuery({
        queryKey: ['project', id],
        queryFn: async () => {
            const { data } = await api.get(`/projects/${id}/`);
            return data;
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5,
    });
};

export const useCreateProject = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (newProject: any) => {
            const { data } = await api.post('/projects/', newProject);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        }
    });
};

export const useColumns = (boardId?: string) => {
    return useQuery({
        queryKey: ['columns', boardId],
        queryFn: async () => {
            const params = boardId ? { board: boardId } : {};
            // Using /columns/ as defined in the projects router
            const { data } = await api.get('/columns/', { params });
            return data;
        },
        staleTime: 1000 * 60 * 5,
    });
};
