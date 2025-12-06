<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import { useFormatters } from '@/composables/useFormatters';

const store = useDashboardStore();
const { formatPrice, formatNumber } = useFormatters();
</script>

<template>
  <div>
    <!-- Empty State -->
    <div v-if="store.properties.length === 0" class="card p-12 text-center">
      <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <p class="font-medium text-gray-900">No properties found</p>
      <p class="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
    </div>

    <!-- Cards Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <article
        v-for="property in store.properties"
        :key="property.zpid"
        class="card card-hover overflow-hidden group"
      >
        <!-- Image -->
        <div class="aspect-video bg-gray-100 relative overflow-hidden">
          <img
            v-if="property.imgSrc"
            :src="property.imgSrc"
            :alt="`Property at ${property.address}`"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>

          <!-- Days Badge -->
          <div
            v-if="property.daysOnZillow !== null"
            :class="[
              'absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium',
              property.daysOnZillow <= 7 ? 'bg-green-500 text-white' :
              property.daysOnZillow <= 30 ? 'bg-yellow-500 text-white' :
              'bg-red-500 text-white'
            ]"
          >
            {{ property.daysOnZillow }} days
          </div>
        </div>

        <!-- Content -->
        <div class="p-4">
          <!-- Price -->
          <div class="flex items-baseline gap-2 mb-2">
            <span class="text-xl font-bold text-gray-900">
              {{ formatPrice(property.price) }}
            </span>
            <span v-if="property.pricePerSqft" class="text-sm text-gray-500">
              ${{ Math.round(property.pricePerSqft) }}/sqft
            </span>
          </div>

          <!-- Address -->
          <p class="text-sm text-gray-600 truncate mb-3" :title="property.address || ''">
            {{ property.address || 'Address unavailable' }}
          </p>

          <!-- Details -->
          <div class="flex items-center gap-4 text-sm text-gray-500">
            <span v-if="property.bedrooms !== null" class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              {{ property.bedrooms }} bd
            </span>
            <span v-if="property.bathrooms !== null" class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
              {{ property.bathrooms }} ba
            </span>
            <span v-if="property.livingArea !== null" class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              {{ formatNumber(property.livingArea) }} sqft
            </span>
          </div>

          <!-- View Link -->
          <a
            v-if="property.detailUrl"
            :href="property.detailUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-4 btn btn-outline w-full text-center"
          >
            View on Zillow
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </article>
    </div>
  </div>
</template>
