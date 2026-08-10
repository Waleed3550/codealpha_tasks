import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// Reusable hook for fetching tasks via React Query
export const useTasks = (projectId?: string) => {
    return useQuery({
        queryKey: ['tasks', projectId],
        queryFn: async () => {
            const { data } = await api.get('/tasks/', {
                params: { project: projectId }
            });
            return data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};

// Reusable mutation hook for creating tasks
export const useCreateTask = () => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: async (newTask: any) => {
            const { data } = await api.post('/tasks/', newTask);
            return data;
        },
        onSuccess: () => {
            // Invalidate and refetch
            queryClient.invalidateQueries({ queryKey: ['tasks'] });
        }
    });
};

// Example Hook for AI Task Generator Integration
export const useAITaskGenerator = () => {
    return useMutation({
        mutationFn: async (prompt: string) => {
            const { data } = await api.post('/tasks/generate-ai/', { prompt });
            return data;
        }
    });
};

export const useUpdateTask = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, status }: { id: string | number, status: string }) => {
            const { data } = await api.patch(`/tasks/${id}/update_status/`, { status });
            return data;
        },
        onMutate: async (newInfo) => {
            await queryClient.cancelQueries({ queryKey: ['tasks'] });
            const previousTasks = queryClient.getQueryData(['tasks']);
            queryClient.setQueryData(['tasks'], (old: any) => {
                if (!old) return old;
                if (Array.isArray(old)) {
                    return old.map((t: any) => t.id === newInfo.id ? { ...t, status: newInfo.status } : t);
                } else if (old.results) {
                    return { ...old, results: old.results.map((t: any) => t.id === newInfo.id ? { ...t, status: newInfo.status } : t) };
                }
                return old;
            });
            return { previousTasks };
        },
        onError: (err, newInfo, context) => {
            if (context?.previousTasks) {
                queryClient.setQueryData(['tasks'], context.previousTasks);
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks'] });
        }
    });
};
