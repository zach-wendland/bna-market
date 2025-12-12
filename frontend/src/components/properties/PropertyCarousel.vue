<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { useFormatters } from '@/composables/useFormatters';

const store = useDashboardStore();
const { formatPrice, formatNumber } = useFormatters();

// Current slide index
const currentIndex = ref(0);

// Track broken images by zpid
const brokenImages = ref<Set<string>>(new Set());

// All properties (including those without images, for display)
const allProperties = computed(() => store.properties);

// Current property being displayed
const currentProperty = computed(() => {
  if (allProperties.value.length === 0) return null;
  return allProperties.value[currentIndex.value];
});

// Navigation
function goToNext() {
  if (allProperties.value.length === 0) return;
  currentIndex.value = (currentIndex.value + 1) % allProperties.value.length;
}

function goToPrev() {
  if (allProperties.value.length === 0) return;
  currentIndex.value = currentIndex.value === 0
    ? allProperties.value.length - 1
    : currentIndex.value - 1;
}

function goToIndex(index: number) {
  if (index >= 0 && index < allProperties.value.length) {
    currentIndex.value = index;
  }
}

// Handle image load error
function handleImageError(zpid: string) {
  brokenImages.value.add(zpid);
  console.warn(`Image failed to load for property ${zpid}`);
}

// Check if current property has a valid image
const hasValidImage = computed(() => {
  if (!currentProperty.value) return false;
  return currentProperty.value.imgSrc && !brokenImages.value.has(currentProperty.value.zpid);
});

// Keyboard navigation
function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    goToNext();
    event.preventDefault();
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    goToPrev();
    event.preventDefault();
  }
}

// Auto-advance timer (optional - disabled by default)
const autoAdvance = ref(false);
const autoAdvanceInterval = ref<number | null>(null);

function toggleAutoAdvance() {
  autoAdvance.value = !autoAdvance.value;
  if (autoAdvance.value) {
    autoAdvanceInterval.value = window.setInterval(goToNext, 5000);
  } else if (autoAdvanceInterval.value) {
    clearInterval(autoAdvanceInterval.value);
    autoAdvanceInterval.value = null;
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
  if (autoAdvanceInterval.value) {
    clearInterval(autoAdvanceInterval.value);
  }
});
</script>

<template>
  <div class="property-carousel" tabindex="0" @keydown="handleKeyDown">
    <!-- Empty State -->
    <div v-if="allProperties.length === 0" class="card p-12 text-center">
      <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="font-medium text-gray-900 text-lg">No properties found</p>
      <p class="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
    </div>

    <!-- Carousel Content -->
    <div v-else class="relative">
      <!-- Main Image Container -->
      <div class="relative bg-gray-900 rounded-xl overflow-hidden aspect-[16/9] max-h-[600px]">
        <!-- Image or Fallback -->
        <div v-if="currentProperty" class="absolute inset-0">
          <img
            v-if="hasValidImage"
            :src="currentProperty.imgSrc!"
            :alt="`Property at ${currentProperty.address}`"
            class="w-full h-full object-cover"
            @error="handleImageError(currentProperty.zpid)"
          />
          <!-- Fallback for missing/broken images -->
          <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gray-800 text-gray-400">
            <svg class="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <p class="text-lg">No image available</p>
          </div>
        </div>

        <!-- Property Details Overlay -->
        <div v-if="currentProperty" class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent p-6">
          <!-- Price -->
          <div class="flex items-baseline gap-3 mb-2">
            <span class="text-3xl font-bold text-white">
              {{ formatPrice(currentProperty.price) }}
            </span>
            <span v-if="currentProperty.pricePerSqft" class="text-lg text-gray-300">
              ${{ Math.round(currentProperty.pricePerSqft) }}/sqft
            </span>
          </div>

          <!-- Address -->
          <p class="text-lg text-gray-200 mb-3">
            {{ currentProperty.address || 'Address unavailable' }}
          </p>

          <!-- Details Row -->
          <div class="flex flex-wrap items-center gap-4 text-gray-300">
            <span v-if="currentProperty.bedrooms !== null" class="flex items-center gap-1.5">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span class="font-medium">{{ currentProperty.bedrooms }} beds</span>
            </span>
            <span v-if="currentProperty.bathrooms !== null" class="flex items-center gap-1.5">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
              <span class="font-medium">
                {{ Number.isInteger(currentProperty.bathrooms) ? currentProperty.bathrooms : currentProperty.bathrooms.toFixed(1) }} baths
              </span>
            </span>
            <span v-if="currentProperty.livingArea !== null" class="flex items-center gap-1.5">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <span class="font-medium">{{ formatNumber(currentProperty.livingArea) }} sqft</span>
            </span>
            <span v-if="currentProperty.daysOnZillow !== null"
              :class="[
                'px-2 py-0.5 rounded text-sm font-medium',
                currentProperty.daysOnZillow <= 7 ? 'bg-green-500 text-white' :
                currentProperty.daysOnZillow <= 30 ? 'bg-yellow-500 text-white' :
                'bg-red-500 text-white'
              ]"
            >
              {{ currentProperty.daysOnZillow }} days on market
            </span>
          </div>

          <!-- View on Zillow Link -->
          <a
            v-if="currentProperty.detailUrl"
            :href="currentProperty.detailUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-4 inline-flex items-center gap-2 text-primary-300 hover:text-primary-200 transition-colors"
          >
            View on Zillow
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <!-- Navigation Arrows -->
        <button
          @click="goToPrev"
          class="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors focus:outline-none focus:ring-2 focus:ring-white/50"
          aria-label="Previous property"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button
          @click="goToNext"
          class="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors focus:outline-none focus:ring-2 focus:ring-white/50"
          aria-label="Next property"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- Slide Counter -->
        <div class="absolute top-4 right-4 bg-black/60 px-3 py-1.5 rounded-full text-white text-sm font-medium">
          {{ currentIndex + 1 }} / {{ allProperties.length }}
        </div>

        <!-- Auto-advance toggle -->
        <button
          @click="toggleAutoAdvance"
          :class="[
            'absolute top-4 left-4 p-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-white/50',
            autoAdvance ? 'bg-primary-500 text-white' : 'bg-black/50 text-white hover:bg-black/70'
          ]"
          :aria-label="autoAdvance ? 'Stop auto-advance' : 'Start auto-advance'"
          :title="autoAdvance ? 'Stop auto-advance' : 'Auto-advance (5s)'"
        >
          <svg v-if="autoAdvance" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>

      <!-- Thumbnail Strip (optional - shows nearby slides) -->
      <div class="mt-4 flex items-center justify-center gap-2 overflow-x-auto py-2">
        <!-- Show up to 7 thumbnail dots centered around current -->
        <button
          v-for="(_, index) in Math.min(allProperties.length, 9)"
          :key="index"
          @click="goToIndex(Math.max(0, currentIndex - 4) + index)"
          :class="[
            'w-2.5 h-2.5 rounded-full transition-all duration-200',
            (Math.max(0, currentIndex - 4) + index) === currentIndex
              ? 'bg-primary-500 w-4'
              : 'bg-gray-300 hover:bg-gray-400'
          ]"
          :aria-label="`Go to property ${Math.max(0, currentIndex - 4) + index + 1}`"
          v-show="Math.max(0, currentIndex - 4) + index < allProperties.length"
        />
        <span v-if="allProperties.length > 9" class="text-gray-400 text-sm ml-2">
          ...
        </span>
      </div>

      <!-- Keyboard hint -->
      <p class="text-center text-sm text-gray-500 mt-2">
        Use <kbd class="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">←</kbd>
        <kbd class="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">→</kbd>
        arrow keys to navigate
      </p>
    </div>
  </div>
</template>

<style scoped>
.property-carousel:focus {
  outline: none;
}

.property-carousel:focus-visible {
  @apply ring-2 ring-primary-500 ring-offset-2 rounded-xl;
}

/* Smooth transitions for image */
.property-carousel img {
  transition: opacity 0.3s ease-in-out;
}
</style>
