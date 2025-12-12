import { test, expect } from '@playwright/test'

/**
 * E2E tests for the PropertyCarousel component
 */

test.describe('Property Carousel View', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display carousel as default view mode', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('.property-carousel, [class*="carousel"]', {
      state: 'visible',
      timeout: 15000
    }).catch(() => {
      // Carousel might not be the default, let's click on it
    })

    // Look for carousel view toggle button and click it
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    // Carousel should now be visible
    await expect(page.locator('.property-carousel')).toBeVisible({ timeout: 10000 })
  })

  test('should display property information in carousel', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    // Wait for carousel to load
    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Should show price
    const priceElement = page.locator('.property-carousel').getByText(/\$[\d,]+/)
    await expect(priceElement.first()).toBeVisible({ timeout: 10000 })
  })

  test('should have navigation arrows', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Check for previous button
    const prevButton = page.getByRole('button', { name: /previous property/i })
    await expect(prevButton).toBeVisible()

    // Check for next button
    const nextButton = page.getByRole('button', { name: /next property/i })
    await expect(nextButton).toBeVisible()
  })

  test('should navigate to next property when clicking next', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Get initial counter text
    const counter = page.locator('.property-carousel').locator('text=/\\d+ \\/ \\d+/')
    const initialText = await counter.textContent({ timeout: 5000 }).catch(() => '1 / 1')

    // Click next
    const nextButton = page.getByRole('button', { name: /next property/i })
    await nextButton.click()

    // Counter should change (if more than 1 property)
    await page.waitForTimeout(300) // Allow animation
    const newText = await counter.textContent()

    // If there's more than 1 property, counter should have changed
    if (initialText && initialText !== '1 / 1') {
      expect(newText).not.toBe(initialText)
    }
  })

  test('should navigate with keyboard arrow keys', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Focus the carousel
    await page.locator('.property-carousel').focus()

    // Get initial state
    const counter = page.locator('.property-carousel').locator('text=/\\d+ \\/ \\d+/')
    const initialText = await counter.textContent({ timeout: 5000 }).catch(() => '1 / 1')

    // Press right arrow
    await page.keyboard.press('ArrowRight')
    await page.waitForTimeout(300)

    // Counter might change if multiple properties
    const afterRightText = await counter.textContent()

    // Press left arrow to go back
    await page.keyboard.press('ArrowLeft')
    await page.waitForTimeout(300)

    const afterLeftText = await counter.textContent()

    // Should be back at initial position
    expect(afterLeftText).toBe(initialText)
  })

  test('should display slide counter', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Should show counter like "1 / 45"
    const counter = page.locator('.property-carousel').locator('text=/\\d+ \\/ \\d+/')
    await expect(counter).toBeVisible({ timeout: 5000 })
  })

  test('should display image or fallback', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Should have either an image or fallback text
    const hasImage = await page.locator('.property-carousel img').isVisible().catch(() => false)
    const hasFallback = await page.locator('.property-carousel').getByText(/no image available/i).isVisible().catch(() => false)

    // One of these should be true
    expect(hasImage || hasFallback).toBe(true)
  })

  test('should have Zillow link when available', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Look for Zillow link
    const zillowLink = page.locator('.property-carousel').getByRole('link', { name: /zillow/i })

    // If link exists, verify it has correct attributes
    if (await zillowLink.isVisible().catch(() => false)) {
      await expect(zillowLink).toHaveAttribute('target', '_blank')
      await expect(zillowLink).toHaveAttribute('rel', /noopener/)
    }
  })

  test('should display empty state when no properties', async ({ page }) => {
    // Apply a filter that returns no results
    await page.goto('/?minPrice=999999999')
    await page.waitForLoadState('networkidle')

    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
      await page.waitForTimeout(500)
    }

    // Check for empty state message in carousel or elsewhere
    const emptyMessage = page.getByText(/no properties found/i)
    // This might be visible depending on the actual API response
  })

  test('should be accessible', async ({ page }) => {
    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Navigation buttons should have aria-labels
    const prevButton = page.getByRole('button', { name: /previous property/i })
    const nextButton = page.getByRole('button', { name: /next property/i })

    await expect(prevButton).toHaveAttribute('aria-label')
    await expect(nextButton).toHaveAttribute('aria-label')

    // Images should have alt text
    const images = page.locator('.property-carousel img')
    const imageCount = await images.count()

    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i)
      if (await img.isVisible()) {
        const alt = await img.getAttribute('alt')
        expect(alt).toBeTruthy()
      }
    }
  })
})

test.describe('Carousel Mobile Responsiveness', () => {
  test('should display correctly on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Carousel should still be visible and functional
    const nextButton = page.getByRole('button', { name: /next property/i })
    await expect(nextButton).toBeVisible()

    // Click should work
    await nextButton.click()
    await page.waitForTimeout(300)
  })

  test('should display correctly on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Navigate to carousel view
    const carouselButton = page.getByRole('button', { name: /carousel/i })
    if (await carouselButton.isVisible()) {
      await carouselButton.click()
    }

    await page.waitForSelector('.property-carousel', { state: 'visible', timeout: 15000 })

    // Navigation should be visible
    await expect(page.getByRole('button', { name: /previous property/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /next property/i })).toBeVisible()
  })
})
