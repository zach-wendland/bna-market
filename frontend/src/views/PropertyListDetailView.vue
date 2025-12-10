<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();
const listId = route.params.id;
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">List Detail</h1>

    <div class="bg-white shadow sm:rounded-lg p-8 text-center">
      <p class="text-gray-600 mb-4">List ID: {{ listId }}</p>
      <p class="text-sm text-gray-500">Full list detail view coming soon!</p>
    </div>
  </main>
</template>
