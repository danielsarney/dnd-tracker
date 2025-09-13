document.addEventListener('DOMContentLoaded', function() {
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Add active state to current navigation item
    highlightCurrentNavItem();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add smooth scrolling to anchor links
    addSmoothScrolling();
    
    // Add form validation styling
    addFormValidationStyling();
});

// Highlight the current navigation item based on URL
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href.replace('/', ''))) {
            link.classList.add('active');
        }
    });
}

// Add smooth scrolling to anchor links
function addSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Add form validation styling
function addFormValidationStyling() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Add validation classes on blur
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            // Remove validation classes on input
            input.addEventListener('input', function() {
                this.classList.remove('is-valid', 'is-invalid');
            });
        });
    });
}



// Add card hover effects
function addCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.8)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.6)';
        });
    });
}

// Initialize card hover effects
document.addEventListener('DOMContentLoaded', function() {
    addCardHoverEffects();
    
    // Initialize character form field toggling
    initializeCharacterFormToggling();
});

// Character form field toggling functionality
function initializeCharacterFormToggling() {
    const typeSelect = document.getElementById('id_type');
    const monsterFields = document.getElementById('monster-fields');
    const playerNpcFields = document.getElementById('player-npc-fields');
    
    // Only initialize if we're on a character form page
    if (!typeSelect || !monsterFields || !playerNpcFields) {
        return;
    }
    
    function toggleFields() {
        const selectedType = typeSelect.value;
        
        if (selectedType === 'MONSTER') {
            monsterFields.style.display = 'block';
            playerNpcFields.style.display = 'none';
        } else {
            monsterFields.style.display = 'none';
            playerNpcFields.style.display = 'block';
        }
    }
    
    // Initial toggle based on current value
    toggleFields();
    
    // Toggle on change
    typeSelect.addEventListener('change', toggleFields);
}

// Initiative tracking specific functions
function initializeInitiativeTracking() {
    // Auto-populate name field and focus on initiative input when character is selected
    const characterSelect = document.getElementById('id_character');
    const nameInput = document.getElementById('id_name');
    const initiativeRollInput = document.getElementById('id_initiative_roll');
    
    if (characterSelect && nameInput && initiativeRollInput) {
        characterSelect.addEventListener('change', function() {
            if (this.value) {
                // Get the selected option
                const selectedOption = this.options[this.selectedIndex];
                const characterName = selectedOption.text.split(' (')[0]; // Remove type from display name
                const characterType = selectedOption.getAttribute('data-type');
                
                // Check if this is a monster or NPC
                if (characterType === 'MONSTER' || characterType === 'NPC') {
                    // For monsters and NPCs, use the DM name
                    const dmName = document.querySelector('[data-dm-name]')?.getAttribute('data-dm-name') || 'DM';
                    nameInput.value = dmName;
                } else {
                    // For player characters, use the character name
                    nameInput.value = characterName;
                }
                
                // Focus on initiative input for quick entry
                initiativeRollInput.focus();
            } else {
                // Clear name field if no character selected
                nameInput.value = '';
            }
        });
    }
}

// Combat encounter management functions
function initializeCombatEncounter() {
    // Add keyboard shortcuts for combat
    document.addEventListener('keydown', function(e) {
        // Space bar to end turn (only on combat detail page)
        if (e.code === 'Space' && window.location.pathname.includes('/combat/detail/')) {
            e.preventDefault();
            const endTurnBtn = document.querySelector('button[onclick="endTurn()"]');
            if (endTurnBtn && !endTurnBtn.disabled) {
                endTurnBtn.click();
            }
        }
        
        // Enter key to submit forms
        if (e.code === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            const form = e.target.closest('form');
            if (form) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }
    });
    
    // Add visual feedback for current turn
    highlightCurrentTurn();
}

function highlightCurrentTurn() {
    const currentTurnRow = document.querySelector('.table-active');
    if (currentTurnRow) {
        // Add pulsing animation to current turn
        currentTurnRow.style.animation = 'pulse 2s infinite';
    }
}

// Initialize initiative tracking when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeInitiativeTracking();
    initializeCombatEncounter();
});
