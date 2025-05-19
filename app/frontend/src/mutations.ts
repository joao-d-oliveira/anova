import { QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { UserCreate, UserLogin } from './generated/client';
import { errorNotification } from './common/notifications';

export const queryClient = new QueryClient();

async function processedFetch<T>(
    url: string,
    options: RequestInit = {},
    json: boolean = true,
    handleError: boolean = true
): Promise<T> {
    let response: Response;
    response = await fetch(`/api/${url}`, {
        ...options,
    });


    if (!response.ok && !response.redirected) {
        if (response.status < 500) {
            const data = await response.json();
            throw new Error(data.detail || 'API request failed');
        }
        throw new Error('Internal server error');
    }
    if (json) {
        const json_response = await response.json();
        return json_response;
    }
    return response as T;
}

export const useRegister = () => {
    const register = useMutation({
        mutationFn: async (data: UserCreate) => {
            await processedFetch<void>("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
        },
        onError: (error) => {
            console.log(error);
            errorNotification(error.message);
        },
    });
    return { register };
};

export const useLogin = () => {
    const login = useMutation({
        mutationFn: async (data: UserLogin) => {
            await processedFetch<void>("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
        },
        onError: (error) => {
            errorNotification(error.message);
        },
    });
    return { login };
};