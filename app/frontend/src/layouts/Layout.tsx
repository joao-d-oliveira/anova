import React from "react";
import { MantineProvider } from "@mantine/core";
import { Suspense } from "react";
import { Outlet } from "react-router-dom";
import { Notifications } from "@mantine/notifications";

export default function Layout() {
    return (
        <MantineProvider>
            <Notifications />
            <Suspense>
                <Outlet />
            </Suspense>
        </MantineProvider>
    )
}