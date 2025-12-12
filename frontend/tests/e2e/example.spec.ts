import { test, expect } from '@playwright/test'

/**
 * Example E2E tests to verify Playwright is working correctly
 */

test.describe('BNA Market - Basic Navigation', () => {
  test('should load the dashboard page', async ({ page }) => {
    await page.goto('/')

    // Wait for the page to load
    await expect(page).toHaveTitle(/BNA Market/i)

    // Check that main content is visible
    const main = page.locator('main')
    await expect(main).toBeVisible()
  })

  test('should display market overview section', async ({ page }) => {
    await page.goto('/')

    // Wait for loading to complete
    await page.waitForLoadState('networkidle')

    // Look for the Market Overview heading
    const heading = page.getByRole('heading', { name: /market overview/i })
    await expect(heading).toBeVisible({ timeout: 10000 })
  })

  test('should display property listings section', async ({ page }) => {
    await page.goto('/')

    // Wait for loading to complete
    await page.waitForLoadState('networkidle')

    // Look for Property Listings heading
    const heading = page.getByRole('heading', { name: /property listings/i })
    await expect(heading).toBeVisible({ timeout: 10000 })
  })

  test('should have view toggle buttons', async ({ page }) => {
    await page.goto('/')

    // Wait for loading to complete
    await page.waitForLoadState('networkidle')

    // Find view toggle area
    const viewToggle = page.locator('[class*="view-toggle"]').or(
      page.getByRole('button', { name: /table|cards|map/i }).first()
    )

    // Should have some view toggle UI (table, cards, map buttons)
    await expect(viewToggle.first()).toBeVisible({ timeout: 10000 })
  })
})

test.describe('BNA Market - Responsive Design', () => {
  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Main content should still be visible
    const main = page.locator('main')
    await expect(main).toBeVisible()
  })

  test('should be responsive on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Main content should still be visible
    const main = page.locator('main')
    await expect(main).toBeVisible()
  })
})

test.describe('BNA Market - Accessibility', () => {
  test('should have no automatically detectable a11y violations on dashboard', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Basic accessibility checks
    // Check that images have alt text (if any)
    const images = page.locator('img')
    const imageCount = await images.count()

    for (let i = 0; i < Math.min(imageCount, 5); i++) {
      const img = images.nth(i)
      const alt = await img.getAttribute('alt')
      // Images should have some alt attribute (can be empty for decorative)
      expect(alt).not.toBeNull()
    }

    // Check that buttons are accessible
    const buttons = page.getByRole('button')
    const buttonCount = await buttons.count()

    for (let i = 0; i < Math.min(buttonCount, 5); i++) {
      const button = buttons.nth(i)
      // Button should have accessible name
      const name = await button.getAttribute('aria-label') ||
                   await button.textContent()
      expect(name).toBeTruthy()
    }
  })
})
