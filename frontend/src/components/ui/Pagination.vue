<script setup lang="ts">
import { computed } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';

const store = useDashboardStore();

const pagination = computed(() => store.pagination);

const visiblePages = computed(() => {
  if (!pagination.value) return [];

  const current = pagination.value.page;
  const total = pagination.value.totalPages;
  const pages: (number | string)[] = [];

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    pages.push(1);

    if (current > 3) pages.push('...');

    const start = Math.max(2, current - 1);
    const end = Math.min(total - 1, current + 1);

    for (let i = start; i <= end; i++) pages.push(i);

    if (current < total - 2) pages.push('...');

    pages.push(total);
  }

  return pages;
});

async function goToPage(page: number) {
  if (!pagination.value) return;
  if (page < 1 || page > pagination.value.totalPages) return;

  store.setPage(page);
  await store.searchWithFilters();
}
</script>

<template>
  <nav v-if="pagination" class="flex items-center justify-between" aria-label="Pagination">
    <div class="hidden sm:flex sm:items-center sm:gap-2">
      <p class="text-sm text-gray-700">
        Showing
        <span class="font-medium">{{ (pagination.page - 1) * pagination.perPage + 1 }}</span>
        to
        <span class="font-medium">{{ Math.min(pagination.page * pagination.perPage, pagination.totalCount) }}</span>
        of
        <span class="font-medium">{{ pagination.totalCount.toLocaleString() }}</span>
        results
      </p>
    </div>

    <div class="flex items-center gap-1">
      <!-- Previous -->
      <button
        @click="goToPage(pagination.page - 1)"
        :disabled="!pagination.hasPrev"
        class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Previous page"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Page numbers -->
      <template v-for="page in visiblePages" :key="page">
        <span v-if="page === '...'" class="px-2 text-gray-400">...</span>
        <button
          v-else
          @click="goToPage(page as number)"
          :class="[
            'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
            pagination.page === page
              ? 'bg-primary-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
        >
          {{ page }}
        </button>
      </template>

      <!-- Next -->
      <button
        @click="goToPage(pagination.page + 1)"
        :disabled="!pagination.hasNext"
        class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Next page"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </nav>
</template>
