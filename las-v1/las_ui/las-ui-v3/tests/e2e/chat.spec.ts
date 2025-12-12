import { test, expect } from '@playwright/test';

test.describe('LAS Chat Interface', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should display the main chat layout', async ({ page }) => {
        // Verify title or main header
        await expect(page).toHaveTitle(/Local Agent System/);

        // Use accessible locator strategies
        const inputArea = page.getByPlaceholder(/Send a message/i);
        await expect(inputArea).toBeVisible();
    });

    test('should allow user to type and send a message', async ({ page }) => {
        const input = page.getByPlaceholder(/Send a message/i);

        // Type a test message
        await input.fill('Hello AI');
        await page.keyboard.press('Enter');

        // Expect the message to appear in the chat stream
        // Note: Depends on backend being mockable or available. 
        // In a real E2E, we might see the user message immediately.
        await expect(page.getByText('Hello AI')).toBeVisible();
    });
});
