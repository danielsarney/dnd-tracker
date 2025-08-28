// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger to X
            const spans = navToggle.querySelectorAll('span');
            spans.forEach((span, index) => {
                if (navMenu.classList.contains('active')) {
                    if (index === 0) span.style.transform = 'rotate(45deg) translate(5px, 5px)';
                    if (index === 1) span.style.opacity = '0';
                    if (index === 2) span.style.transform = 'rotate(-45deg) translate(7px, -6px)';
                } else {
                    span.style.transform = 'none';
                    span.style.opacity = '1';
                }
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                const spans = navToggle.querySelectorAll('span');
                spans.forEach(span => {
                    span.style.transform = 'none';
                    span.style.opacity = '1';
                });
            }
        });
    }
    
    // User Dropdown Toggle
    const userDropdown = document.querySelector('.user-dropdown');
    if (userDropdown) {
        const dropdownToggle = userDropdown.querySelector('.user-dropdown-toggle');
        
        dropdownToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userDropdown.contains(event.target)) {
                userDropdown.classList.remove('active');
            }
        });
        
        // Close dropdown when pressing Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                userDropdown.classList.remove('active');
            }
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    

    
    // Profile image preview
    const avatarInput = document.querySelector('input[type="file"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const avatarImg = document.querySelector('.profile-avatar');
                        if (avatarImg) {
                            avatarImg.src = e.target.result;
                        }
                    };
                    reader.readAsDataURL(file);
                } else {
                    // File is not a valid image
                    console.warn('Please select a valid image file.');
                }
            }
        });
    }
    
    // Campaign card hover effects
    const campaignCards = document.querySelectorAll('.campaign-card');
    campaignCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Campaign form validation
    const campaignForm = document.querySelector('.campaign-form');
    if (campaignForm) {
        campaignForm.addEventListener('submit', function(e) {
            const nameInput = this.querySelector('input[name="name"]');
            const dmInput = this.querySelector('input[name="dm"]');
            
            if (!nameInput.value.trim()) {
                e.preventDefault();
                showFieldError(nameInput, 'Campaign name is required');
                return;
            }
            
            if (!dmInput.value.trim()) {
                e.preventDefault();
                showFieldError(dmInput, 'Dungeon Master is required');
                return;
            }
        });
    }
    
    // Delete confirmation enhancement
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const isCharacter = form.closest('.character-detail-container') !== null;
            const itemType = isCharacter ? 'character' : 'campaign';
            if (!confirm(`Are you absolutely sure you want to delete this ${itemType}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
    
    // Character card hover effects
    const characterCards = document.querySelectorAll('.character-card');
    characterCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Character form validation
    const characterForm = document.querySelector('.character-form');
    if (characterForm) {
        characterForm.addEventListener('submit', function(e) {
            const campaignSelect = this.querySelector('select[name="campaign"]');
            const typeSelect = this.querySelector('select[name="type"]');
            const nameInput = this.querySelector('input[name="name"]');
            
            if (!campaignSelect.value) {
                e.preventDefault();
                showFieldError(campaignSelect, 'Please select a campaign');
                return;
            }
            
            if (!typeSelect.value) {
                e.preventDefault();
                showFieldError(typeSelect, 'Please select a character type');
                return;
            }
            
            if (!nameInput.value.trim()) {
                e.preventDefault();
                showFieldError(nameInput, 'Character name is required');
                return;
            }
        });
    }
    
    // Character filter form enhancement
    const filterForm = document.querySelector('.filter-form');
    if (filterForm) {
        const campaignSelect = filterForm.querySelector('select[name="campaign"]');
        const typeSelect = filterForm.querySelector('select[name="type"]');
        const searchInput = filterForm.querySelector('input[name="search"]');
        
        // Auto-submit on filter change
        [campaignSelect, typeSelect].forEach(select => {
            if (select) {
                select.addEventListener('change', () => filterForm.submit());
            }
        });
        
        // Search with debouncing
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    filterForm.submit();
                }, 500);
            });
        }
    }
    
    // Game session card hover effects
    const sessionCards = document.querySelectorAll('.session-card');
    sessionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Game session form validation
    const sessionForm = document.querySelector('.session-form');
    if (sessionForm) {
        sessionForm.addEventListener('submit', function(e) {
            const campaignSelect = this.querySelector('select[name="campaign"]');
            const dateInput = this.querySelector('input[name="date"]');
            const summaryInput = this.querySelector('textarea[name="summary"]');
            
            if (!campaignSelect.value) {
                e.preventDefault();
                showFieldError(campaignSelect, 'Please select a campaign');
                return;
            }
            
            if (!dateInput.value) {
                e.preventDefault();
                showFieldError(dateInput, 'Please select a session date');
                return;
            }
            
            if (!summaryInput.value.trim()) {
                e.preventDefault();
                showFieldError(summaryInput, 'Session summary is required');
                return;
            }
        });
    }
    
    // Game session filter form enhancement
    const sessionFilterForm = document.querySelector('.sessions-filters .filter-form');
    if (sessionFilterForm) {
        const campaignSelect = sessionFilterForm.querySelector('select[name="campaign"]');
        const dateFromInput = sessionFilterForm.querySelector('input[name="date_from"]');
        const dateToInput = sessionFilterForm.querySelector('input[name="date_to"]');
        const searchInput = sessionFilterForm.querySelector('input[name="search"]');
        
        // Auto-submit on filter change
        [campaignSelect, dateFromInput, dateToInput].forEach(select => {
            if (select) {
                select.addEventListener('change', () => sessionFilterForm.submit());
            }
        });
        
        // Search with debouncing
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    sessionFilterForm.submit();
                }, 500);
            });
        }
    }
});

// Helper function to show field errors
function showFieldError(field, message) {
    // Remove existing error
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
    
    // Focus on the field
    field.focus();
    
    // Remove error after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}



// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});


