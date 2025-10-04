// Auto-focus on the code input when it appears
document.addEventListener('DOMContentLoaded', function() {
    // Try to find code input by ID 'code' first, then by any input with pattern for 6-digit codes
    let codeInput = document.getElementById('code');
    if (!codeInput) {
        codeInput = document.querySelector('input[pattern="[0-9]{6}"]');
    }
    if (!codeInput) {
        codeInput = document.querySelector('input[maxlength="6"]');
    }
    
    if (codeInput) {
        codeInput.focus();
    }
});

// Note: Auto-submit disabled to prevent CSRF token issues
// Users will need to manually submit the form after entering the 6-digit code
