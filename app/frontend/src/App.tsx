import './css/App.css'; // Make sure the file path is correct

import React, { Component } from "react";

import { RouteRecord } from "vite-react-ssg";
const Layout = React.lazy(() => import("./layouts/Layout"));
const AuthLayout = React.lazy(() => import("./layouts/AuthLayout"));
const DashboardLayout = React.lazy(() => import("./layouts/DashboardLayout"));
const Landing = React.lazy(() => import("./pages/Landing"));
const Error404 = React.lazy(() => import("./pages/Error404"));
const Signup = React.lazy(() => import("./pages/auth/Signup"));
const Login = React.lazy(() => import("./pages/auth/Login"));
const ForgotPassword = React.lazy(() => import("./pages/auth/ForgotPassword"));
const Tos = React.lazy(() => import("./pages/Tos"));
const Dashboard = React.lazy(() => import("./pages/dashboard/Dashboard"));
const Analysis = React.lazy(() => import("./pages/dashboard/Task"));
const GameReport = React.lazy(() => import("./pages/dashboard/GameReport"));

const staticPaths: RouteRecord[] = [
  {
    path: "",
    Component: Layout,
    children: [
      {
        path: "auth",
        Component: AuthLayout,
        children: [
          {
            path: "signup", Component: Signup,
          },
          {
            path: "login", Component: Login,
          },
          {
            path: "forgot-password", Component: ForgotPassword,
          },
        ]
      },
      {
        path: "dashboard", Component: DashboardLayout,
        children: [
          {
            path: "", Component: Dashboard,
          },
          {
            path: "analysis", Component: Analysis,
          },
          {
            path: "game-report", Component: GameReport,
          }
        ]
      },
      {
        path: "terms", Component: Tos,
      },
      {
        path: "", Component: Landing,
      },
      { path: "404", Component: Error404 },
      { path: "*", Component: Error404 }
    ]
  },

]

// Simplify your route configuration
let routes: RouteRecord[] = staticPaths.map(
  route => ["/"].map(
    (language) => (
      {
        path: language.concat(route.path!),
        Component: route.Component,
        element: route.element,
        // ErrorBoundary: ErrorBoundary,
        children: route.children,
      }
    )
  )
).flat()

export default routes;