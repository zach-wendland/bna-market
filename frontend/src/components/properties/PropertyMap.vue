<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { useFormatters } from '@/composables/useFormatters';
import L from 'leaflet';
import 'leaflet.markercluster';

const store = useDashboardStore();
const { formatPrice, formatNumber } = useFormatters();

const mapContainer = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let markersLayer: L.MarkerClusterGroup | null = null;

// Price color coding
function getPriceColor(price: number | null): string {
  if (price === null) return '#9ca3af';
  if (store.filters.propertyType === 'rental') {
    if (price < 1500) return '#22c55e';
    if (price < 2500) return '#3b82f6';
    if (price < 3500) return '#f59e0b';
    return '#ef4444';
  } else {
    if (price < 300000) return '#22c55e';
    if (price < 500000) return '#3b82f6';
    if (price < 750000) return '#f59e0b';
    return '#ef4444';
  }
}

function initMap() {
  if (!mapContainer.value || map) return;

  // Create map centered on Nashville
  map = L.map(mapContainer.value).setView([36.1627, -86.7816], 11);

  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);

  // Create marker cluster group
  markersLayer = L.markerClusterGroup({
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    iconCreateFunction: (cluster) => {
      const count = cluster.getChildCount();
      let size = 'small';
      if (count > 10) size = 'medium';
      if (count > 50) size = 'large';

      return L.divIcon({
        html: `<div class="cluster-icon">${count}</div>`,
        className: `marker-cluster marker-cluster-${size}`,
        iconSize: L.point(40, 40)
      });
    }
  });

  map.addLayer(markersLayer);
  updateMarkers();
}

function updateMarkers() {
  if (!map || !markersLayer) return;

  markersLayer.clearLayers();

  const propertiesWithCoords = store.properties.filter(
    p => p.latitude !== null && p.longitude !== null
  );

  if (propertiesWithCoords.length === 0) return;

  propertiesWithCoords.forEach(property => {
    if (property.latitude === null || property.longitude === null) return;

    const color = getPriceColor(property.price);

    const marker = L.circleMarker([property.latitude, property.longitude], {
      radius: 8,
      fillColor: color,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8
    });

    const popupContent = `
      <div class="p-2 min-w-[200px]">
        <p class="text-lg font-bold" style="color: ${color}">
          ${formatPrice(property.price)}
        </p>
        <p class="text-sm text-gray-600 mt-1">
          ${property.address || 'Unknown address'}
        </p>
        <p class="text-sm text-gray-500 mt-2">
          ${property.bedrooms || '?'} bed &bull;
          ${property.bathrooms || '?'} bath &bull;
          ${formatNumber(property.livingArea)} sqft
        </p>
        ${property.pricePerSqft ? `<p class="text-sm text-gray-500">$${Math.round(property.pricePerSqft)}/sqft</p>` : ''}
        ${property.detailUrl ? `
          <a href="${property.detailUrl}" target="_blank" rel="noopener"
             class="inline-block mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium">
            View on Zillow →
          </a>
        ` : ''}
      </div>
    `;

    marker.bindPopup(popupContent);
    markersLayer!.addLayer(marker);
  });

  // Fit bounds to show all markers
  if (propertiesWithCoords.length > 0) {
    const bounds = markersLayer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }
}

// Watch for property changes
watch(() => store.properties, () => {
  updateMarkers();
}, { deep: true });

// Watch for view mode changes (fix Leaflet sizing issue)
watch(() => store.viewMode, (newMode) => {
  if (newMode === 'map' && map) {
    setTimeout(() => {
      map?.invalidateSize();
    }, 100);
  }
});

onMounted(() => {
  initMap();
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
    markersLayer = null;
  }
});
</script>

<template>
  <div class="card overflow-hidden">
    <!-- Empty State -->
    <div
      v-if="store.properties.length === 0"
      class="h-[500px] flex items-center justify-center text-gray-500"
    >
      <div class="text-center">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p class="font-medium">No properties to display</p>
        <p class="text-sm mt-1">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Map Container -->
    <div
      v-else
      ref="mapContainer"
      class="h-[500px] lg:h-[600px]"
    />

    <!-- Legend -->
    <div class="p-4 border-t border-gray-100 bg-gray-50">
      <div class="flex flex-wrap items-center gap-4 text-sm">
        <span class="text-gray-500 font-medium">Price Range:</span>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-green-500" />
          <span v-if="store.filters.propertyType === 'rental'">&lt;$1,500</span>
          <span v-else>&lt;$300K</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-blue-500" />
          <span v-if="store.filters.propertyType === 'rental'">$1,500-$2,500</span>
          <span v-else>$300K-$500K</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-amber-500" />
          <span v-if="store.filters.propertyType === 'rental'">$2,500-$3,500</span>
          <span v-else>$500K-$750K</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-red-500" />
          <span v-if="store.filters.propertyType === 'rental'">&gt;$3,500</span>
          <span v-else>&gt;$750K</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.marker-cluster {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.marker-cluster-small {
  background-color: rgba(102, 126, 234, 0.6);
}

.marker-cluster-medium {
  background-color: rgba(102, 126, 234, 0.7);
}

.marker-cluster-large {
  background-color: rgba(102, 126, 234, 0.8);
}

.cluster-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(102, 126, 234, 0.9);
  border-radius: 50%;
  color: white;
  font-weight: 600;
  font-size: 12px;
}
</style>
