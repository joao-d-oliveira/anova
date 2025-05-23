import React, { useEffect } from "react";

import '@mantine/notifications/styles.css'

import { Box } from "@mantine/core";
import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../mutations";
import { errorNotification, successNotification } from "../common/notifications";

export default function AuthLayout() {
    const location = useLocation();
    const message = new URLSearchParams(location.search).get('message');
    const messageType = new URLSearchParams(location.search).get('messageType');

    useEffect(() => {
        if (message && messageType) {
            if (messageType === 'success') {
                successNotification(message);
            } else if (messageType === 'error') {
                errorNotification(message);
            }
        }
    }, [message, messageType]);

    return (
        <QueryClientProvider client={queryClient}>
            <Box bg="gray.1" mih="100vh">
                <Suspense>
                    <Outlet />
                </Suspense>
            </Box>
        </QueryClientProvider>
    )
}