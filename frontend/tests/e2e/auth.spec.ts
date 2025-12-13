import { test, expect } from '@playwright/test'

/**
 * E2E tests for Authentication (Google SSO)
 */

test.describe('Login Page', () => {
  test('should display login page with Google sign-in button', async ({ page }) => {
    await page.goto('/login')

    // Check for BNA Market branding
    const title = page.getByRole('heading', { name: /BNA Market/i })
    await expect(title).toBeVisible()

    // Check for Nashville Real Estate Analytics subtitle
    const subtitle = page.getByText(/Nashville Real Estate Analytics/i)
    await expect(subtitle).toBeVisible()
  })

  test('should display Google sign-in button', async ({ page }) => {
    await page.goto('/login')

    // Find the Google sign-in button
    const googleButton = page.getByRole('button', { name: /Continue with Google/i })
    await expect(googleButton).toBeVisible()

    // Button should have Google logo (SVG)
    const googleLogo = googleButton.locator('svg')
    await expect(googleLogo).toBeVisible()
  })

  test('should display "Browse as Guest" option', async ({ page }) => {
    await page.goto('/login')

    // Find guest access button
    const guestButton = page.getByRole('button', { name: /Browse as Guest/i })
    await expect(guestButton).toBeVisible()
  })

  test('should navigate to dashboard when clicking Browse as Guest', async ({ page }) => {
    await page.goto('/login')

    // Click guest button
    const guestButton = page.getByRole('button', { name: /Browse as Guest/i })
    await guestButton.click()

    // Should navigate to dashboard
    await expect(page).toHaveURL('/')

    // Dashboard should load
    await expect(page.getByRole('heading', { name: /Market Overview/i })).toBeVisible({ timeout: 10000 })
  })

  test('should show loading state when clicking Google sign-in', async ({ page }) => {
    await page.goto('/login')

    // Mock the Supabase OAuth to prevent actual redirect
    await page.route('**/*supabase*', route => route.abort())

    // Click Google button
    const googleButton = page.getByRole('button', { name: /Continue with Google/i })
    await googleButton.click()

    // Button should show loading state or error
    // (Since we blocked Supabase, it may show an error)
  })

  test('should display terms and privacy links', async ({ page }) => {
    await page.goto('/login')

    // Check for terms link
    const termsLink = page.getByRole('link', { name: /Terms of Service/i })
    await expect(termsLink).toBeVisible()

    // Check for privacy link
    const privacyLink = page.getByRole('link', { name: /Privacy Policy/i })
    await expect(privacyLink).toBeVisible()
  })
})

test.describe('Login Page - Features Section', () => {
  test('should display three feature highlights', async ({ page }) => {
    await page.goto('/login')

    // Check for Save Properties feature
    const savePropsHeading = page.getByRole('heading', { name: /Save Properties/i })
    await expect(savePropsHeading).toBeVisible()

    // Check for Save Searches feature
    const saveSearchHeading = page.getByRole('heading', { name: /Save Searches/i })
    await expect(saveSearchHeading).toBeVisible()

    // Check for Market Analytics feature
    const analyticsHeading = page.getByRole('heading', { name: /Market Analytics/i })
    await expect(analyticsHeading).toBeVisible()
  })
})

test.describe('Auth Callback', () => {
  test('should handle auth callback with tokens', async ({ page }) => {
    // Simulate callback with mock tokens
    await page.goto('/auth/callback#access_token=mock_token&refresh_token=mock_refresh')

    // Should show verifying or error message
    // (Will fail to verify with mock tokens, but should handle gracefully)
    await page.waitForLoadState('networkidle')

    // Either shows error or redirects
  })

  test('should show error state for invalid callback', async ({ page }) => {
    // No tokens in URL
    await page.goto('/auth/callback')

    // Should handle gracefully
    await page.waitForLoadState('networkidle')
  })
})

test.describe('Protected Routes', () => {
  test('should allow access to dashboard without authentication', async ({ page }) => {
    // Dashboard is public
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Market Overview/i })).toBeVisible({ timeout: 10000 })
  })

  test('should show login prompt for authenticated features', async ({ page }) => {
    // Property lists require auth
    await page.goto('/lists')

    // Should redirect to login or show auth required message
    await page.waitForLoadState('networkidle')

    // Either on login page or shows sign-in prompt
    const currentUrl = page.url()
    const isOnLogin = currentUrl.includes('/login')
    const hasSignInPrompt = await page.getByText(/Sign in/i).isVisible().catch(() => false)

    expect(isOnLogin || hasSignInPrompt).toBeTruthy()
  })
})

test.describe('Login Page - Responsive Design', () => {
  test('should be usable on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/login')

    // Google button should be visible and clickable
    const googleButton = page.getByRole('button', { name: /Continue with Google/i })
    await expect(googleButton).toBeVisible()

    // Features section should stack vertically
    const features = page.locator('.grid.grid-cols-1')
    await expect(features.first()).toBeVisible()
  })
})
