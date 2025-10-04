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

// Auto-submit when 6 digits are entered
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
        codeInput.addEventListener('input', function(e) {
            if (e.target.value.length === 6) {
                setTimeout(() => {
                    e.target.form.submit();
                }, 500);
            }
        });
    }
});

// Auto-hide error flash messages after 5 minutes
document.addEventListener('DOMContentLoaded', function() {
    const errorMessages = document.querySelectorAll('.alert-error');
    
    errorMessages.forEach(function(message) {
        setTimeout(function() {
            // Use Bootstrap's alert dismiss functionality
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            } else {
                // Fallback: manually hide the alert
                message.style.transition = 'opacity 0.5s';
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 500);
            }
        }, 5 * 60 * 1000); // 5 minutes in milliseconds
    });
});
