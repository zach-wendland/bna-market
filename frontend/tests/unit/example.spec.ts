/**
 * Example unit test to verify Vitest is working correctly
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, h } from 'vue'

// Simple test component
const TestComponent = defineComponent({
  props: {
    msg: { type: String, default: 'Hello' }
  },
  setup(props) {
    return () => h('div', { class: 'test-component' }, props.msg)
  }
})

describe('Vitest Setup', () => {
  it('should run basic assertions', () => {
    expect(1 + 1).toBe(2)
    expect('hello').toContain('ell')
    expect([1, 2, 3]).toHaveLength(3)
  })

  it('should mount Vue components', () => {
    const wrapper = mount(TestComponent, {
      props: { msg: 'Testing!' }
    })

    expect(wrapper.text()).toBe('Testing!')
    expect(wrapper.classes()).toContain('test-component')
  })

  it('should have Pinia available', () => {
    // Pinia is auto-initialized in setup.ts
    const pinia = createPinia()
    setActivePinia(pinia)
    expect(pinia).toBeDefined()
  })

  it('should mock functions correctly', () => {
    const mockFn = vi.fn()
    mockFn('test')

    expect(mockFn).toHaveBeenCalled()
    expect(mockFn).toHaveBeenCalledWith('test')
  })

  it('should handle async operations', async () => {
    const promise = Promise.resolve('success')
    await expect(promise).resolves.toBe('success')
  })
})

describe('Environment', () => {
  it('should have window defined (happy-dom)', () => {
    expect(window).toBeDefined()
    expect(document).toBeDefined()
  })

  it('should have matchMedia mocked', () => {
    const mediaQuery = window.matchMedia('(min-width: 768px)')
    expect(mediaQuery).toBeDefined()
    expect(mediaQuery.matches).toBe(false)
  })

  it('should have IntersectionObserver mocked', () => {
    const observer = new IntersectionObserver(() => {})
    expect(observer).toBeDefined()
    expect(observer.observe).toBeDefined()
  })

  it('should have ResizeObserver mocked', () => {
    const observer = new ResizeObserver(() => {})
    expect(observer).toBeDefined()
    expect(observer.observe).toBeDefined()
  })
})
