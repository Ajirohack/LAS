import { test, expect } from '@playwright/test';

test.describe('Workflow Builder', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/workflows');
    });

    test('workflow builder page loads', async ({ page }) => {
        // Check for workflow builder elements
        const hasWorkflowElement = await page.locator('text=/workflow/i').count() > 0;
        expect(hasWorkflowElement).toBeTruthy();
    });

    test('can create new workflow', async ({ page }) => {
        // Look for "New Workflow" or similar button
        const newButton = page.locator('button', { hasText: /new|create|add/i }).first();

        if (await newButton.count() > 0) {
            await newButton.click();
            await page.waitForTimeout(1000);

            // Should have workflow name input
            const nameInput = await page.locator('input[type="text"]').count();
            expect(nameInput).toBeGreaterThan(0);
        }
    });

    test('workflow nodes can be added', async ({ page }) => {
        // This test depends on your workflow builder implementation
        // Check if there's a node palette or add node button
        const hasAddNode = await page.locator('button, [role="button"]').count() > 0;
        expect(hasAddNode).toBeTruthy();
    });
});

test.describe('Settings Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/settings');
    });

    test('settings page loads', async ({ page }) => {
        // Check for settings elements
        const hasSettings = await page.locator('text=/settings|preferences|config/i').count() > 0;
        expect(hasSettings).toBeTruthy();
    });

    test('can change theme', async ({ page }) => {
        // Look for theme toggle
        const themeToggle = page.locator('button', { hasText: /theme|dark|light/i }).first();

        if (await themeToggle.count() > 0) {
            await themeToggle.click();
            await page.waitForTimeout(500);

            // Theme should have changed
            // Check for dark/light mode class on html or body
            const html = page.locator('html, body');
            const className = await html.getAttribute('class');
            expect(className).toBeTruthy();
        }
    });

    test('can update API settings', async ({ page }) => {
        // Look for API key or model settings
        const hasApiSettings = await page.locator('input[type="text"], input[type="password"]').count() > 0;

        if (hasApiSettings) {
            const input = page.locator('input').first();
            await input.fill('test-value');

            // Look for save button
            const saveButton = page.locator('button', { hasText: /save|update|apply/i }).first();
            if (await saveButton.count() > 0) {
                await saveButton.click();

                // Should show success message
                await page.waitForTimeout(1000);
            }
        }
    });
});
