/**
 * Vitest global test setup
 * This file runs before each test file
 */
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, vi } from 'vitest'

// Create a fresh Pinia instance before each test
beforeEach(() => {
  setActivePinia(createPinia())
})

// Global test configuration for Vue Test Utils
config.global.stubs = {
  // Stub router-link by default
  RouterLink: true,
  RouterView: true,
  // Stub teleport for modals
  Teleport: true,
}

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver for lazy loading tests
const mockIntersectionObserver = vi.fn()
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
})
window.IntersectionObserver = mockIntersectionObserver

// Mock ResizeObserver for chart tests
const mockResizeObserver = vi.fn()
mockResizeObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
})
window.ResizeObserver = mockResizeObserver

// Suppress console errors in tests (optional, enable for cleaner output)
// vi.spyOn(console, 'error').mockImplementation(() => {})
// vi.spyOn(console, 'warn').mockImplementation(() => {})

// Export useful test utilities
export { vi } from 'vitest'
export { mount, shallowMount, flushPromises } from '@vue/test-utils'
