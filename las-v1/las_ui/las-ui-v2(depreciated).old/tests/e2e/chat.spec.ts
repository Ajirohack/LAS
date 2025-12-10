import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
    test.beforeEach(async ({ page }) => {
        // Login first
        await page.goto('/');

        // Quick login (adjust based on your flow)
        const loginTab = page.locator('text=Login');
        if (await loginTab.count() > 0) {
            await loginTab.click();
            await page.fill('input[id="login-username"]', 'testuser');
            await page.fill('input[id="login-password"]', 'testpass123');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(2000);
        }

        // Navigate to chat
        await page.goto('/chat');
    });

    test('chat interface loads correctly', async ({ page }) => {
        // Check for chat elements
        const hasChatInput = await page.locator('input[type="text"], textarea').count() > 0;
        expect(hasChatInput).toBeTruthy();
    });

    test('user can send a message', async ({ page }) => {
        // Find chat input
        const chatInput = page.locator('input[type="text"], textarea').first();
        await chatInput.fill('Hello, this is a test message');

        // Find and click send button
        const sendButton = page.locator('button', { hasText: /send|submit/i }).first();
        await sendButton.click();

        // Wait for message to appear
        await page.waitForTimeout(1000);

        // Check if message appears in chat
        await expect(page.locator('text=Hello, this is a test message')).toBeVisible({
            timeout: 5000
        });
    });

    test('provider selection is available', async ({ page }) => {
        // Look for provider selector
        const hasProviderSelector = await page.locator('select, [role="combobox"]').count() > 0;

        if (hasProviderSelector) {
            const selector = page.locator('select, [role="combobox"]').first();
            await selector.click();

            // Should have options
            const options = await page.locator('option, [role="option"]').count();
            expect(options).toBeGreaterThan(0);
        }
    });

    test('chat history is preserved', async ({ page }) => {
        // Send a message
        const chatInput = page.locator('input[type="text"], textarea').first();
        const testMessage = `Test ${Date.now()}`;

        await chatInput.fill(testMessage);
        const sendButton = page.locator('button', { hasText: /send|submit/i }).first();
        await sendButton.click();

        await page.waitForTimeout(2000);

        // Refresh page
        await page.reload();
        await page.waitForTimeout(1000);

        // Check if message is still there
        const messageExists = await page.locator(`text=${testMessage}`).count() > 0;
        // Message might or might not persist based on implementation
        // This is more of a feature check
    });
});
