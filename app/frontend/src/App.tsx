// import {
//   BrowserRouter as Router,
//   Routes,
//   Route,
// } from "react-router-dom";

import './App.css'; // Make sure the file path is correct
// import { ENV } from "./utils/const";

// import ErrorBoundary from "./components/ErrorBoundary";
// import { initReactI18next } from "react-i18next";
// import i18nextBrowserLanguageDetector from "i18next-browser-languagedetector"
// import i18next from "i18next";
// import LocalesImportPlugin from "./components/LocalesLazyImport";

// import { SUPPORTED_LANGUAGES } from "./utils/common";
import React, { Component } from "react";

// import PageNotFound from "./pages/page404";
import { RouteRecord } from "vite-react-ssg";
// import LocalesImportPlugin from './components/LocalesLazyImport';
const Layout = React.lazy(() => import("./layouts/Layout"));
const AuthLayout = React.lazy(() => import("./layouts/AuthLayout"));
const DashboardLayout = React.lazy(() => import("./layouts/DashboardLayout"));

const Error404 = React.lazy(() => import("./pages/Error404"));
const Signup = React.lazy(() => import("./pages/auth/Signup"));
const Login = React.lazy(() => import("./pages/auth/Login"));
const ForgotPassword = React.lazy(() => import("./pages/auth/ForgotPassword"));
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