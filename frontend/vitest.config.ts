import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig } from 'vite'
import { configDefaults, defineConfig as defineVitestConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default mergeConfig(
  defineConfig({
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }),
  defineVitestConfig({
    test: {
      environment: 'happy-dom',
      globals: true,
      include: ['tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
      exclude: [...configDefaults.exclude, 'tests/e2e/**/*'],
      setupFiles: ['./tests/unit/setup.ts'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        include: ['src/**/*.{vue,ts}'],
        exclude: [
          'src/**/*.d.ts',
          'src/main.ts',
          'src/router/index.ts',
        ],
        thresholds: {
          lines: 70,
          functions: 70,
          branches: 70,
          statements: 70,
        },
      },
      reporters: ['verbose'],
      testTimeout: 10000,
    },
  })
)
