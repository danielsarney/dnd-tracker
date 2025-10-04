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
