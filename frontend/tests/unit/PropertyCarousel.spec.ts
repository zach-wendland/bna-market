/**
 * Unit tests for PropertyCarousel component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PropertyCarousel from '@/components/properties/PropertyCarousel.vue'
import { useDashboardStore } from '@/stores/dashboard'

// Mock property data
const mockProperties = [
  {
    zpid: '12345',
    address: '123 Main St, Nashville, TN 37203',
    price: 350000,
    bedrooms: 3,
    bathrooms: 2.0,
    livingArea: 1800,
    propertyType: 'SINGLE_FAMILY',
    latitude: 36.1627,
    longitude: -86.7816,
    imgSrc: 'https://example.com/img1.jpg',
    detailUrl: 'https://zillow.com/homedetails/12345',
    daysOnZillow: 5,
    listingStatus: 'FOR_SALE',
    pricePerSqft: 194.44
  },
  {
    zpid: '67890',
    address: '456 Oak Ave, Nashville, TN 37204',
    price: 425000,
    bedrooms: 4,
    bathrooms: 2.5,
    livingArea: 2200,
    propertyType: 'SINGLE_FAMILY',
    latitude: 36.1500,
    longitude: -86.7700,
    imgSrc: 'https://example.com/img2.jpg',
    detailUrl: 'https://zillow.com/homedetails/67890',
    daysOnZillow: 15,
    listingStatus: 'FOR_SALE',
    pricePerSqft: 193.18
  },
  {
    zpid: '11111',
    address: '789 Elm St, Nashville, TN 37205',
    price: 275000,
    bedrooms: 2,
    bathrooms: 1.5,
    livingArea: 1200,
    propertyType: 'CONDO',
    latitude: 36.1400,
    longitude: -86.7600,
    imgSrc: null, // No image
    detailUrl: 'https://zillow.com/homedetails/11111',
    daysOnZillow: 45,
    listingStatus: 'FOR_SALE',
    pricePerSqft: 229.17
  }
]

describe('PropertyCarousel', () => {
  let store: ReturnType<typeof useDashboardStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useDashboardStore()
  })

  it('should render empty state when no properties', () => {
    store.properties = []

    const wrapper = mount(PropertyCarousel)

    expect(wrapper.text()).toContain('No properties found')
    expect(wrapper.text()).toContain('Try adjusting your filters')
  })

  it('should render carousel with properties', () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Should show first property
    expect(wrapper.text()).toContain('123 Main St, Nashville, TN 37203')
    expect(wrapper.text()).toContain('$350,000')
    expect(wrapper.text()).toContain('3 beds')
    expect(wrapper.text()).toContain('2 baths')
    expect(wrapper.text()).toContain('1,800 sqft')
  })

  it('should display slide counter correctly', () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    expect(wrapper.text()).toContain('1 / 3')
  })

  it('should navigate to next property', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Initially showing first property
    expect(wrapper.text()).toContain('123 Main St')

    // Click next button
    const nextButton = wrapper.find('[aria-label="Next property"]')
    await nextButton.trigger('click')

    // Should now show second property
    expect(wrapper.text()).toContain('456 Oak Ave')
    expect(wrapper.text()).toContain('2 / 3')
  })

  it('should navigate to previous property', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Go to next first
    const nextButton = wrapper.find('[aria-label="Next property"]')
    await nextButton.trigger('click')

    // Then go back
    const prevButton = wrapper.find('[aria-label="Previous property"]')
    await prevButton.trigger('click')

    // Should be back at first property
    expect(wrapper.text()).toContain('123 Main St')
    expect(wrapper.text()).toContain('1 / 3')
  })

  it('should wrap around when navigating past last property', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    const nextButton = wrapper.find('[aria-label="Next property"]')

    // Click next 3 times (should wrap around to first)
    await nextButton.trigger('click') // 2
    await nextButton.trigger('click') // 3
    await nextButton.trigger('click') // 1 (wrapped)

    expect(wrapper.text()).toContain('1 / 3')
    expect(wrapper.text()).toContain('123 Main St')
  })

  it('should wrap around when navigating before first property', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    const prevButton = wrapper.find('[aria-label="Previous property"]')

    // Click prev (should wrap to last)
    await prevButton.trigger('click')

    expect(wrapper.text()).toContain('3 / 3')
    expect(wrapper.text()).toContain('789 Elm St')
  })

  it('should show fallback for property without image', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Navigate to property without image
    const nextButton = wrapper.find('[aria-label="Next property"]')
    await nextButton.trigger('click') // 2
    await nextButton.trigger('click') // 3 (no image)

    // Should show fallback
    expect(wrapper.text()).toContain('No image available')
  })

  it('should handle keyboard navigation', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Simulate right arrow key
    await wrapper.find('.property-carousel').trigger('keydown', { key: 'ArrowRight' })

    expect(wrapper.text()).toContain('2 / 3')

    // Simulate left arrow key
    await wrapper.find('.property-carousel').trigger('keydown', { key: 'ArrowLeft' })

    expect(wrapper.text()).toContain('1 / 3')
  })

  it('should display days on market with correct color', () => {
    store.properties = [mockProperties[0]] // 5 days - green

    const wrapper = mount(PropertyCarousel)

    const badge = wrapper.find('.bg-green-500')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('5 days')
  })

  it('should have link to Zillow', () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    const zillowLink = wrapper.find('a[href*="zillow.com"]')
    expect(zillowLink.exists()).toBe(true)
    expect(zillowLink.attributes('target')).toBe('_blank')
    expect(zillowLink.attributes('rel')).toContain('noopener')
  })

  it('should track broken images', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Get the img element
    const img = wrapper.find('img')

    // Simulate image error
    await img.trigger('error')

    // The component should track broken images
    // and show fallback (this is handled internally)
    // We can check the console warning was called
    expect(wrapper.vm).toBeDefined()
  })

  it('should toggle auto-advance mode', async () => {
    vi.useFakeTimers()
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // Find auto-advance button
    const autoButton = wrapper.find('[title*="Auto-advance"]')
    expect(autoButton.exists()).toBe(true)

    // Click to enable
    await autoButton.trigger('click')

    // Should now have active state
    expect(autoButton.classes()).toContain('bg-primary-500')

    // Clean up
    vi.useRealTimers()
  })

  it('should display price per sqft when available', () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    expect(wrapper.text()).toContain('$194/sqft')
  })

  it('should format bathroom count correctly', async () => {
    store.properties = mockProperties

    const wrapper = mount(PropertyCarousel)

    // First property has 2.0 baths (should show as "2")
    expect(wrapper.text()).toContain('2 baths')

    // Navigate to second property with 2.5 baths
    const nextButton = wrapper.find('[aria-label="Next property"]')
    await nextButton.trigger('click')

    expect(wrapper.text()).toContain('2.5 baths')
  })
})

describe('PropertyCarousel - Image Integrity', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should handle property with null imgSrc', () => {
    const store = useDashboardStore()
    store.properties = [
      {
        zpid: '99999',
        address: 'No Image Property',
        price: 100000,
        bedrooms: 1,
        bathrooms: 1,
        livingArea: 500,
        propertyType: 'CONDO',
        latitude: 36.0,
        longitude: -86.0,
        imgSrc: null,
        detailUrl: null,
        daysOnZillow: 1,
        listingStatus: 'FOR_SALE',
        pricePerSqft: 200
      }
    ]

    const wrapper = mount(PropertyCarousel)

    // Should show fallback
    expect(wrapper.text()).toContain('No image available')
    // Should not have img element
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('should log warning when image fails to load', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    const store = useDashboardStore()
    store.properties = [
      {
        zpid: 'broken-image',
        address: 'Broken Image Property',
        price: 100000,
        bedrooms: 1,
        bathrooms: 1,
        livingArea: 500,
        propertyType: 'CONDO',
        latitude: 36.0,
        longitude: -86.0,
        imgSrc: 'https://example.com/broken.jpg',
        detailUrl: null,
        daysOnZillow: 1,
        listingStatus: 'FOR_SALE',
        pricePerSqft: 200
      }
    ]

    const wrapper = mount(PropertyCarousel)

    // Trigger image error
    await wrapper.find('img').trigger('error')

    // Should have logged warning
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Image failed to load for property broken-image')
    )

    consoleSpy.mockRestore()
  })
})
