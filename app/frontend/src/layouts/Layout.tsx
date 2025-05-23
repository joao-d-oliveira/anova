import React from "react";
import { Button, CardSection, MantineProvider, Title, createTheme } from "@mantine/core";
import { Suspense } from "react";
import { Outlet } from "react-router-dom";
import { Notifications } from "@mantine/notifications";


const theme = createTheme({
    fontFamily: "Inter, sans-serif",
    defaultRadius: "md",
    colors: {
        brand: [
            '#e2ffef',
            '#ccffe1',
            '#9affc3',
            '#65fea2',
            '#3afe87',
            '#20fe75',
            '#01fb65',
            '#00e25a',
            '#00c94e',
            '#000f11'
          ],
    },
    components: {
        CardSection: {
            defaultProps: {
                px: "md",
                pt: "6",
                pb: "2",
                mb: "xs",
                bg: "brand.9",
                c: "brand.6",
                fw: 700,
                fz: "md",
            },
        },
        Anchor: {
            defaultProps: {
                c: "brand.9",
            },
        },
    },
});

export default function Layout() {
    return (
        <MantineProvider theme={theme}>
            <Notifications />
            <Suspense>
                <Outlet />
            </Suspense>
        </MantineProvider>
    )
}