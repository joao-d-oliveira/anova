import { QueryClient, useMutation, useQuery } from '@tanstack/react-query';
import { BodyUploadFilesApiTaskUploadPost, LatestTeamAnalysis, OverallReport, ProcessingTaskResponse, ReportSummary, ResetPasswordRequest, UploadProcessResponse, UserBase, UserConfirm, UserCreate, UserLogin } from './generated/client';
import { errorNotification } from './common/notifications';
import { useState } from 'react';

export const queryClient = new QueryClient();

async function processedFetch<T>(
    url: string,
    options: RequestInit = {},
    json: boolean = true,
    handleError: boolean = true
): Promise<T> {
    let response: Response;
    response = await fetch(`/api${url}`, {
        ...options,
    });


    if (!response.ok && !response.redirected) {
        if (response.headers.get('content-type')?.includes('application/json')) {
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

    const confirmAccount = useMutation({
        mutationFn: async (data: UserConfirm) => {
            await processedFetch<void>("/auth/confirm-email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            }, false);
        },
        onError: (error) => {
            errorNotification(error.message);
        },
    });

    return { register, confirmAccount };
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
            }, false);
        },
        onError: (error) => {
            errorNotification(error.message);
        },
        onSuccess: (data) => {
            window.location.href = "/dashboard";
        },
    });
    return { login };
};

export const useUser = () => {
    const user = useQuery({
        queryKey: ["user"],
        queryFn: async () => await processedFetch<UserBase>("/auth/me"),
        staleTime: 1000 * 60 * 5, // Refetch every 5 minutes
        retry: false,
    });
    return {user};
};

export const useLogout = () => {
    const logout = useMutation({
        mutationFn: async () => await processedFetch<void>("/auth/logout", {}, false),
        onSuccess: () => {
            console.log("Logging out");
            window.location.href = "/auth/login";
        },
    });
    return {logout};
};

export const useUpload = () => {
    const upload = useMutation({
        mutationFn: async (data: BodyUploadFilesApiTaskUploadPost) => {
            const formData = new FormData();
            formData.append('team_files', data.team_files);
            formData.append('opponent_files', data.opponent_files);
            if (data.team_name) formData.append('team_name', data.team_name);
            if (data.opponent_name) formData.append('opponent_name', data.opponent_name);
            if (data.use_local_simulation !== undefined) {
                formData.append('use_local_simulation', data.use_local_simulation.toString());
            }

            return await processedFetch<UploadProcessResponse>("/task/upload", {
                method: "POST",
                body: formData,
            });
        },
    });
    return { upload };
};

export const useAnalysis = ({ task_id }: { task_id: string }) => {
    const [analysis, setAnalysis] = useState<ProcessingTaskResponse | null>(null);
    const status = useQuery({
        queryKey: ["analysis", task_id],
        queryFn: async () => {
            const response = await processedFetch<ProcessingTaskResponse>("/task/status/" + task_id);
            setAnalysis(response);
            return response;
        },
        enabled: !!task_id,
        refetchInterval: (data) => {
            if(data.state?.error?.cause === 404) {
                return false
            }
            return analysis == null || analysis.status == "processing" ? 2000 : false;
        },
        retryDelay: 2000
    });
    return { status };
};

export const useReport = ({ game_uuid }: { game_uuid: string }) => {
    const overallReport = useQuery({
        queryKey: ["report", game_uuid],
        queryFn: async () => await processedFetch<OverallReport>("/report/" + game_uuid),
    });

    return { overallReport };
};

export const useDownloadReport = () => {
    const downloadReport = useMutation({
        mutationFn: async ({game_uuid}: {game_uuid: string}) => {
            const response = await fetch("/api/report/" + game_uuid + "/download");
            if (!response.ok) {
                errorNotification("Failed to download report");
                throw new Error("Failed to download report");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `game-report-${game_uuid}.docx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        },
    });
    return { downloadReport };
};

export const useReportSummaries = () => {
    const reportSummaries = useQuery({
        queryKey: ["report-summaries"],
        queryFn: async () => await processedFetch<ReportSummary[]>("/report/summaries"),
    });
    return { reportSummaries };
};

export const useForgotPassword = () => {
    const forgotPassword = useMutation({
        mutationFn: async (email: string) => {
            await processedFetch<void>("/auth/forgot-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });
        },
        onError: (error) => {
            errorNotification(error.message);
        },
    });
    return { forgotPassword };
};

export const useResetPassword = () => {
    const resetPassword = useMutation({
        mutationFn: async (data: ResetPasswordRequest) => {
            await processedFetch<void>("/auth/reset-password", {
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
    return { resetPassword };
};

export const useLatestTeamAnalysis = () => {
    const latestHomeTeamAnalysis = useQuery({
        queryKey: ["latest-home-team-analysis"],
        queryFn: async () => await processedFetch<LatestTeamAnalysis>("/team/latest-home-team-analysis"),
        staleTime: 1000 * 60 * 5, // Refetch every 5 minutes
    });
    return { latestHomeTeamAnalysis };
};