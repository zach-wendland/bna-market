import { ref, watch, onUnmounted, type Ref } from 'vue';

export function useDebounce<T>(value: Ref<T>, delay: number = 500): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>;
  let timeout: ReturnType<typeof setTimeout>;

  watch(value, (newValue) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);
  });

  // Cleanup on component unmount to prevent memory leaks
  onUnmounted(() => {
    clearTimeout(timeout);
  });

  return debouncedValue;
}

export interface DebouncedFn<T extends (...args: unknown[]) => unknown> {
  (...args: Parameters<T>): void;
  cancel: () => void;
}

export function useDebounceFn<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number = 500
): DebouncedFn<T> {
  let timeout: ReturnType<typeof setTimeout> | undefined;

  const debouncedFn = ((...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      fn(...args);
    }, delay);
  }) as DebouncedFn<T>;

  // Add cancel method to stop pending debounced calls
  debouncedFn.cancel = () => {
    clearTimeout(timeout);
    timeout = undefined;
  };

  // Cleanup on component unmount to prevent memory leaks
  onUnmounted(() => {
    clearTimeout(timeout);
  });

  return debouncedFn;
}
