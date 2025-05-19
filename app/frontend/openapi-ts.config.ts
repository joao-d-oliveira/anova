import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './specs/openapi.json',
  output: './src/generated/client',
  plugins: [
    {
      name: '@hey-api/typescript',
      enums: 'typescript',
    },
  ],
});