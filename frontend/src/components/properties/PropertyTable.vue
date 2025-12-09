<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import { useFormatters } from '@/composables/useFormatters';

const store = useDashboardStore();
const { formatPrice, formatNumber } = useFormatters();

interface Column {
  key: string;
  label: string;
  sortable: boolean;
  class?: string;
}

const columns: Column[] = [
  { key: 'address', label: 'Address', sortable: true, class: 'min-w-[200px]' },
  { key: 'price', label: 'Price', sortable: true },
  { key: 'pricePerSqft', label: '$/Sqft', sortable: true },
  { key: 'bedrooms', label: 'Beds', sortable: true },
  { key: 'bathrooms', label: 'Baths', sortable: true },
  { key: 'livingArea', label: 'Sq Ft', sortable: true },
  { key: 'propertyType', label: 'Type', sortable: false },
  { key: 'daysOnZillow', label: 'Days', sortable: true },
  { key: 'actions', label: 'View', sortable: false }
];

async function handleSort(column: string) {
  store.setSort(column);
  await store.searchWithFilters();
}

function getSortIcon(column: string): string {
  if (store.sortConfig.column !== column) return '';
  return store.sortConfig.order === 'asc' ? '↑' : '↓';
}
</script>

<template>
  <div class="card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="data-table">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="col.class"
            >
              <button
                v-if="col.sortable"
                @click="handleSort(col.key)"
                class="flex items-center gap-1 hover:opacity-80 transition-opacity w-full text-left"
              >
                <span>{{ col.label }}</span>
                <span
                  v-if="store.sortConfig.column === col.key"
                  class="text-yellow-300"
                >
                  {{ getSortIcon(col.key) }}
                </span>
              </button>
              <span v-else>{{ col.label }}</span>
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-if="store.properties.length === 0">
            <td :colspan="columns.length" class="text-center py-12 text-gray-500">
              <div class="flex flex-col items-center">
                <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <p class="font-medium">No properties found</p>
                <p class="text-sm mt-1">Try adjusting your filters</p>
              </div>
            </td>
          </tr>

          <tr
            v-for="property in store.properties"
            :key="property.zpid"
            class="group"
          >
            <!-- Address -->
            <td class="font-medium text-gray-900 max-w-[250px] truncate" :title="property.address || ''">
              {{ property.address || 'Unknown' }}
            </td>

            <!-- Price -->
            <td class="font-semibold text-primary-600">
              {{ formatPrice(property.price) }}
            </td>

            <!-- Price per Sqft -->
            <td class="text-gray-500">
              <span v-if="property.pricePerSqft">
                ${{ Math.round(property.pricePerSqft) }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </td>

            <!-- Beds -->
            <td>{{ property.bedrooms ?? 'N/A' }}</td>

            <!-- Baths -->
            <td>{{ property.bathrooms != null ? (Number.isInteger(property.bathrooms) ? property.bathrooms : property.bathrooms.toFixed(1)) : 'N/A' }}</td>

            <!-- Sqft -->
            <td>{{ formatNumber(property.livingArea) }}</td>

            <!-- Type -->
            <td>
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                {{ property.propertyType || 'Unknown' }}
              </span>
            </td>

            <!-- Days on Zillow -->
            <td>
              <span
                v-if="property.daysOnZillow !== null"
                :class="[
                  'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                  property.daysOnZillow <= 7 ? 'bg-green-100 text-green-700' :
                  property.daysOnZillow <= 30 ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                ]"
              >
                {{ property.daysOnZillow }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </td>

            <!-- Actions -->
            <td>
              <a
                v-if="property.detailUrl"
                :href="property.detailUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                <span>View</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
              <span v-else class="text-gray-400">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
