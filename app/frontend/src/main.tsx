import React from 'react';
import { ViteReactSSG } from 'vite-react-ssg'
import routes from './App'

// Patch useLayoutEffect for SSR
if (typeof window === 'undefined') {
  // @ts-ignore - Intentionally overriding React's useLayoutEffect during SSR
  React.useLayoutEffect = React.useEffect;
}

export const createRoot = ViteReactSSG(
  { 
    routes,
    basename: import.meta.env.BASE_URL
  }
)