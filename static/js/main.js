/*
 * D&D Tracker Application JavaScript
 *
 * This JavaScript file contains client-side functionality for the D&D Tracker application.
 * It provides enhanced user experience features such as auto-focusing on form inputs
 * and other interactive elements.
 *
 * Key Features:
 * - Auto-focus on 2FA code input fields
 * - Enhanced form interaction
 * - User experience improvements
 */

/**
 * Auto-focus functionality for 2FA code input fields
 *
 * This function automatically focuses on 2FA code input fields when the page loads,
 * improving user experience by eliminating the need to manually click on the input.
 * It tries multiple selectors to find the appropriate input field.
 */
document.addEventListener("DOMContentLoaded", function () {
  // Try to find code input by ID 'code' first (most specific)
  let codeInput = document.getElementById("code");

  // If not found by ID, try to find by pattern attribute for 6-digit codes
  if (!codeInput) {
    codeInput = document.querySelector('input[pattern="[0-9]{6}"]');
  }

  // If still not found, try to find by maxlength attribute for 6-digit codes
  if (!codeInput) {
    codeInput = document.querySelector('input[maxlength="6"]');
  }

  // Focus on the input field if found
  if (codeInput) {
    codeInput.focus();
  }
});
