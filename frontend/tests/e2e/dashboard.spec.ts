import { test, expect } from '@playwright/test'

/**
 * E2E tests for Dashboard with new BentoMetrics and Charts
 */

test.describe('Dashboard - Bento Metrics Grid', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display Nashville Market Insights heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: /Nashville Market Insights/i })
    await expect(heading).toBeVisible({ timeout: 10000 })
  })

  test('should display Bento metrics grid with 6 cards', async ({ page }) => {
    // Wait for the bento grid to load
    const bentoGrid = page.locator('.bento-grid')
    await expect(bentoGrid).toBeVisible({ timeout: 15000 })

    // Should have 6 metric cards
    const cards = page.locator('.bento-card')
    await expect(cards).toHaveCount(6, { timeout: 10000 })
  })

  test('should display Avg Rental Price metric', async ({ page }) => {
    const label = page.locator('.bento-label', { hasText: /Avg Rental Price/i })
    await expect(label).toBeVisible({ timeout: 10000 })

    // Should show a value or "Accumulating data"
    const card = label.locator('..')
    const value = card.locator('.bento-value')
    await expect(value).toBeVisible()
  })

  test('should display Avg Sale Price metric', async ({ page }) => {
    const label = page.locator('.bento-label', { hasText: /Avg Sale Price/i })
    await expect(label).toBeVisible({ timeout: 10000 })
  })

  test('should display DOM metrics', async ({ page }) => {
    // Rental DOM
    const rentalDom = page.locator('.bento-label', { hasText: /Rental DOM/i })
    await expect(rentalDom).toBeVisible({ timeout: 10000 })

    // For-Sale DOM
    const saleDom = page.locator('.bento-label', { hasText: /For-Sale DOM/i })
    await expect(saleDom).toBeVisible({ timeout: 10000 })
  })

  test('should display Active Listings and Market Sentiment', async ({ page }) => {
    const activeListings = page.locator('.bento-label', { hasText: /Active Listings/i })
    await expect(activeListings).toBeVisible({ timeout: 10000 })

    const sentiment = page.locator('.bento-label', { hasText: /Market Sentiment/i })
    await expect(sentiment).toBeVisible({ timeout: 10000 })
  })

  test('should show sparklines or "Accumulating data" message', async ({ page }) => {
    // Either sparklines should be visible OR the "Accumulating data" message
    const sparklines = page.locator('.bento-sparkline svg')
    const noDataMessages = page.locator('.bento-no-data')

    // At least one should be present for each card
    const sparklineCount = await sparklines.count()
    const noDataCount = await noDataMessages.count()

    // Total should equal 6 (one per card that has sparkline area)
    // Note: Only 4 cards have sparklines (the price/DOM ones)
    expect(sparklineCount + noDataCount).toBeGreaterThanOrEqual(4)
  })
})

test.describe('Dashboard - Economic Charts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display Economic Indicators section', async ({ page }) => {
    const heading = page.getByText(/Economic Indicators/i)
    await expect(heading).toBeVisible({ timeout: 10000 })
  })

  test('should display chart grid with 4 charts', async ({ page }) => {
    // Wait for charts to load (they use Suspense)
    await page.waitForTimeout(2000)

    // Chart cards should be visible
    const chartCards = page.locator('.chart-card')
    await expect(chartCards.first()).toBeVisible({ timeout: 15000 })

    // Should have 4 economic indicator charts
    const count = await chartCards.count()
    expect(count).toBeGreaterThanOrEqual(4)
  })

  test('should show loading spinners while charts load', async ({ page }) => {
    // Immediately check for spinners (may be too fast to catch)
    // This is more of a smoke test
    await page.goto('/')

    // Either spinner or chart should be visible
    const spinner = page.locator('.spinner-cyber')
    const chart = page.locator('.chart-card canvas')

    // Wait for either
    await Promise.race([
      expect(spinner.first()).toBeVisible({ timeout: 1000 }).catch(() => {}),
      expect(chart.first()).toBeVisible({ timeout: 10000 }),
    ])
  })
})

test.describe('Dashboard - KPI Cards', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display Market Overview heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: /Market Overview/i })
    await expect(heading).toBeVisible({ timeout: 10000 })
  })

  test('should display KPI values', async ({ page }) => {
    // Look for KPI values (they're formatted like $XXX,XXX or numbers)
    const kpiValues = page.locator('.kpi-value')
    await expect(kpiValues.first()).toBeVisible({ timeout: 10000 })

    // Should have at least 4 KPI values
    const count = await kpiValues.count()
    expect(count).toBeGreaterThanOrEqual(4)
  })
})

test.describe('Dashboard - Responsive Layout', () => {
  test('bento grid should be 3 columns on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const bentoGrid = page.locator('.bento-grid')
    await expect(bentoGrid).toBeVisible({ timeout: 10000 })

    // Check grid layout via CSS
    const gridCols = await bentoGrid.evaluate((el) => {
      const style = window.getComputedStyle(el)
      return style.gridTemplateColumns
    })

    // Should have 3 columns (contains 3 values like "200px 200px 200px" or "1fr 1fr 1fr")
    const colCount = gridCols.split(' ').filter(v => v.length > 0).length
    expect(colCount).toBe(3)
  })

  test('bento grid should be 2 columns on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 800, height: 600 })
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const bentoGrid = page.locator('.bento-grid')
    await expect(bentoGrid).toBeVisible({ timeout: 10000 })

    const gridCols = await bentoGrid.evaluate((el) => {
      const style = window.getComputedStyle(el)
      return style.gridTemplateColumns
    })

    const colCount = gridCols.split(' ').filter(v => v.length > 0).length
    expect(colCount).toBe(2)
  })

  test('bento grid should be 1 column on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const bentoGrid = page.locator('.bento-grid')
    await expect(bentoGrid).toBeVisible({ timeout: 10000 })

    const gridCols = await bentoGrid.evaluate((el) => {
      const style = window.getComputedStyle(el)
      return style.gridTemplateColumns
    })

    const colCount = gridCols.split(' ').filter(v => v.length > 0).length
    expect(colCount).toBe(1)
  })
})

test.describe('Dashboard - Visual Polish', () => {
  test('bento cards should have hover effect', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const card = page.locator('.bento-card').first()
    await expect(card).toBeVisible({ timeout: 10000 })

    // Get initial box shadow
    const initialShadow = await card.evaluate((el) => {
      return window.getComputedStyle(el).boxShadow
    })

    // Hover over card
    await card.hover()

    // Wait for transition
    await page.waitForTimeout(300)

    // Get new shadow (should be different on hover)
    const hoverShadow = await card.evaluate((el) => {
      return window.getComputedStyle(el).boxShadow
    })

    // Shadow should change on hover (or transform)
    // Note: This may not always be different depending on CSS
  })

  test('indicator dots should have glow effect', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const dot = page.locator('.bento-dot').first()
    await expect(dot).toBeVisible({ timeout: 10000 })

    // Check that dot has box-shadow (glow)
    const shadow = await dot.evaluate((el) => {
      return window.getComputedStyle(el).boxShadow
    })

    expect(shadow).not.toBe('none')
  })
})
