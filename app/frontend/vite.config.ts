import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

const isLocal = process.env.NODE_ENV !== '  ';
const server = isLocal ? {
    proxy: {
        '/api': {
            // target: 'https://vgreen.webcustodia.com',
            target: 'http://localhost:8000',
            changeOrigin: true,
            secure: true,
            cookieDomainRewrite: 'localhost',
            // If your API doesn't have /api in the path, you can rewrite it:
            // rewrite: (path) => path.replace(/^\/api/, '')
        }
    }
} : {};

// https://vitejs.dev/config/
export default defineConfig({
    base: process.env.BASE_URL ?? "/",
    server: server,
    plugins: [
        react(),
    ],
    resolve: {
        alias: {
            // /esm/icons/index.mjs only exports the icons statically, so no separate chunks are created
            '@tabler/icons-react': '@tabler/icons-react/dist/esm/icons/index.mjs',
        },
    },
    build: {
        commonjsOptions: {
            include: [/node_modules/, /@mantine\/.*/],
            transformMixedEsModules: true,
            sourceMap: true
        },
        rollupOptions: {
            output: {
                manualChunks: undefined
            }
        }
    },
    optimizeDeps: {
        include: ['@mantine/core', '@mantine/hooks']
    },
    ssgOptions: {
        beastiesOptions: {
            external: false,
        },
        dirStyle: 'nested',
        script: 'async',
        format: 'esm',
    }
})