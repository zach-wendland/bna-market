<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg';
}>();
</script>

<template>
  <div class="flex items-center justify-center">
    <div
      :class="[
        'animate-spin rounded-full border-2 border-current border-t-transparent text-primary-600',
        {
          'w-4 h-4': size === 'sm',
          'w-6 h-6': size === 'md' || !size,
          'w-10 h-10': size === 'lg'
        }
      ]"
    />
  </div>
</template>
