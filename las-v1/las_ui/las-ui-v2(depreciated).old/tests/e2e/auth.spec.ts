import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should show login/register form on landing page', async ({ page }) => {
        // Check for auth form elements
        await expect(page.getByRole('tab', { name: /login/i })).toBeVisible();
        await expect(page.getByRole('tab', { name: /register/i })).toBeVisible();
    });

    test('user can register a new account', async ({ page }) => {
        // Click register tab
        await page.click('text=Register');

        // Fill registration form
        const timestamp = Date.now();
        await page.fill('input[id="register-username"]', `testuser${timestamp}`);
        await page.fill('input[id="register-email"]', `test${timestamp}@example.com`);
        await page.fill('input[id="register-password"]', 'testpass123');
        await page.fill('input[id="register-confirm"]', 'testpass123');

        // Submit form
        await page.click('button[type="submit"]');

        // Wait for redirect or success message
        await page.waitForTimeout(2000);

        // Should either redirect to dashboard or show success
        const url = page.url();
        const hasRedirected = url.includes('dashboard') || url.includes('chat');
        const hasSuccessMessage = await page.locator('text=/success|welcome/i').count() > 0;

        expect(hasRedirected || hasSuccessMessage).toBeTruthy();
    });

    test('user can login with valid credentials', async ({ page }) => {
        // First register a user
        await page.click('text=Register');
        const timestamp = Date.now();
        const username = `loginuser${timestamp}`;
        const password = 'testpass123';

        await page.fill('input[id="register-username"]', username);
        await page.fill('input[id="register-email"]', `${username}@example.com`);
        await page.fill('input[id="register-password"]', password);
        await page.fill('input[id="register-confirm"]', password);
        await page.click('button[type="submit"]');

        await page.waitForTimeout(2000);

        // Now logout (if button exists)
        const logoutButton = page.locator('button', { hasText: /logout|sign out/i });
        if (await logoutButton.count() > 0) {
            await logoutButton.first().click();
            await page.waitForTimeout(1000);
        } else {
            // Navigate back to login
            await page.goto('/');
        }

        // Login
        await page.click('text=Login');
        await page.fill('input[id="login-username"]', username);
        await page.fill('input[id="login-password"]', password);
        await page.click('button[type="submit"]');

        await page.waitForTimeout(2000);

        // Should be logged in
        const url = page.url();
        expect(url).not.toContain('/login');
    });

    test('login fails with incorrect password', async ({ page }) => {
        await page.click('text=Login');

        await page.fill('input[id="login-username"]', 'nonexistent');
        await page.fill('input[id="login-password"]', 'wrongpassword');
        await page.click('button[type="submit"]');

        // Should show error message
        await expect(page.locator('text=/invalid|incorrect|failed/i')).toBeVisible({
            timeout: 5000
        });
    });

    test('registration validates password length', async ({ page }) => {
        await page.click('text=Register');

        await page.fill('input[id="register-username"]', 'testuser');
        await page.fill('input[id="register-email"]', 'test@example.com');
        await page.fill('input[id="register-password"]', '123');  // Too short
        await page.fill('input[id="register-confirm"]', '123');
        await page.click('button[type="submit"]');

        // Should show validation error
        await expect(page.locator('text=/at least 8/i')).toBeVisible({
            timeout: 3000
        });
    });

    test('protected routes redirect to login', async ({ page }) => {
        // Try to access dashboard without auth
        await page.goto('/dashboard');

        // Should redirect to login
        await page.waitForURL('**/login**', { timeout: 3000 }).catch(() => { });

        // Or should show login form
        const hasLoginForm = await page.locator('input[id="login-username"]').count() > 0;
        expect(hasLoginForm).toBeTruthy();
    });
});
