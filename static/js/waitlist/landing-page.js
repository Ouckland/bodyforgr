// Waitlist Landing Page JavaScript - Optimized for Mobile
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initDesktopNavigation();
    initMobileNavigation();
    initFormValidation();
    initSmoothScroll();
    initAnimations();
    
    // Handle orientation changes
    let orientationTimeout;
    window.addEventListener('orientationchange', function() {
        clearTimeout(orientationTimeout);
        orientationTimeout = setTimeout(() => {
            initDesktopNavigation();
            initMobileNavigation();
        }, 300);
    });
    
    // Handle resize events with debouncing
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            initDesktopNavigation();
            initMobileNavigation();
        }, 250);
    });
});

// ===== DESKTOP NAVIGATION =====
function initDesktopNavigation() {
    const minimalNav = document.getElementById('minimalNav');
    if (!minimalNav) return;
    
    // Only initialize on desktop
    if (window.innerWidth < 769) {
        minimalNav.style.display = 'none';
        return;
    }
    
    const navDots = minimalNav.querySelectorAll('.nav-dot');
    const progressFill = minimalNav.querySelector('.progress-fill');
    const navBrand = minimalNav.querySelector('.nav-brand');
    
    minimalNav.style.display = 'flex';
    
    // Update active dot and progress
    function updateNavigation() {
        const sections = document.querySelectorAll('section');
        const scrollPosition = window.scrollY + 100;
        
        // Update progress indicator
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (window.scrollY / totalHeight) * 100;
        if (progressFill) {
            progressFill.style.height = `${progress}%`;
        }
        
        // Find active section
        let currentSection = '';
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                currentSection = section.id;
            }
        });
        
        // Update dots
        navDots.forEach(dot => {
            dot.classList.remove('active');
            if (dot.getAttribute('data-section') === currentSection) {
                dot.classList.add('active');
            }
        });
    }
    
    // Add click handlers to dots
    navDots.forEach(dot => {
        dot.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const targetPosition = targetSection.offsetTop;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                history.pushState(null, null, targetId);
                
                // Add click feedback
                const dotElement = this.querySelector('.dot');
                if (dotElement) {
                    dotElement.style.transform = 'scale(1.5)';
                    setTimeout(() => {
                        dotElement.style.transform = 'scale(1)';
                    }, 200);
                }
            }
        });
    });
    
    // Brand click handler
    if (navBrand) {
        navBrand.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    }
    
    // Update on scroll
    window.addEventListener('scroll', updateNavigation);
    updateNavigation();
}

// ===== MOBILE NAVIGATION =====
function initMobileNavigation() {
    const mobileNav = document.getElementById('mobileNav');
    const mobileHeader = document.querySelector('.mobile-header');
    
    if (!mobileNav || !mobileHeader) return;
    
    // Only initialize on mobile
    if (window.innerWidth >= 769) {
        mobileNav.style.display = 'none';
        mobileHeader.style.display = 'none';
        return;
    }
    
    const mobileNavItems = mobileNav.querySelectorAll('.mobile-nav-item');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    
    mobileNav.style.display = 'block';
    mobileHeader.style.display = 'flex';
    
    // Update active nav item based on scroll
    function updateActiveMobileNav() {
        const sections = document.querySelectorAll('section');
        const scrollPosition = window.scrollY + 100;
        
        // Find active section
        let currentSection = '';
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                currentSection = section.id;
            }
        });
        
        // Update mobile nav items
        mobileNavItems.forEach(item => {
            item.classList.remove('active');
            const href = item.getAttribute('href');
            if (href === `#${currentSection}`) {
                item.classList.add('active');
            }
        });
    }
    
    // Add click handlers to mobile nav items
    mobileNavItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = mobileHeader.offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                history.pushState(null, null, targetId);
                
                // Add click feedback
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);
            }
        });
    });
    
    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            
            // For now, scroll to top
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Update on scroll
    window.addEventListener('scroll', updateActiveMobileNav);
    updateActiveMobileNav();
}

// ===== FORM VALIDATION & SUBMISSION =====
function initFormValidation() {
    const waitlistForm = document.getElementById('waitlistForm');
    if (!waitlistForm) return;
    
    // Form validation configuration
    const validationConfig = {
        minNameLength: 2,
        maxNameLength: 100,
        emailRegex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        debounceDelay: 300,
        loadingTimeout: 10000,
    };
    
    // State management
    let isSubmitting = false;
    let validationTimeout = null;
    
    const formElements = {
        name: waitlistForm.querySelector('#id_name'),
        email: waitlistForm.querySelector('#id_email'),
        confirmEmail: waitlistForm.querySelector('#id_confirm_email'),
        role: waitlistForm.querySelector('#id_role'),
        source: waitlistForm.querySelector('#id_source'),
        submitBtn: waitlistForm.querySelector('.btn-submit'),
    };
    
    // Initialize real-time validation
    initRealTimeValidation();
    
    // Handle form submission
    waitlistForm.addEventListener('submit', handleFormSubmit);
    
    // ===== HELPER FUNCTIONS =====
    
    function initRealTimeValidation() {
        // Add input event listeners for real-time validation
        [formElements.name, formElements.email, formElements.confirmEmail].forEach(input => {
            if (input) {
                input.addEventListener('input', debounce(validateField, validationConfig.debounceDelay));
                input.addEventListener('blur', validateField);
            }
        });
        
        // Role validation on change
        if (formElements.role) {
            formElements.role.addEventListener('change', function() {
                validateSelectField(this);
            });
        }
    }
    
    function debounce(func, delay) {
        return function(...args) {
            clearTimeout(validationTimeout);
            validationTimeout = setTimeout(() => func.apply(this, args), delay);
        };
    }
    
    function validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        const fieldName = field.name;
        
        // Clear previous error for this field
        clearFieldError(field);
        
        // Skip validation if field is empty (handled in final validation)
        if (!value) return true;
        
        let isValid = true;
        let errorMessage = '';
        
        switch(fieldName) {
            case 'name':
                isValid = validateName(value);
                if (!isValid) errorMessage = 'Name must be at least 2 characters';
                break;
                
            case 'email':
                isValid = validateEmail(value);
                if (!isValid) errorMessage = 'Please enter a valid email address';
                break;
                
            case 'confirm_email':
                const emailValue = formElements.email ? formElements.email.value.trim() : '';
                isValid = validateEmailConfirmation(value, emailValue);
                if (!isValid) errorMessage = 'Email addresses do not match';
                break;
        }
        
        if (!isValid) {
            showFieldError(field, errorMessage);
        } else {
            showFieldSuccess(field);
        }
        
        return isValid;
    }
    
    function validateSelectField(selectElement) {
        const value = selectElement.value;
        const isValid = value !== '';
        
        if (selectElement === formElements.role) {
            if (!isValid) {
                showFieldError(selectElement, 'Please select your role');
            } else {
                clearFieldError(selectElement);
                showFieldSuccess(selectElement);
            }
        }
        
        return isValid;
    }
    
    function validateName(name) {
        if (!name || name.length < validationConfig.minNameLength) return false;
        if (name.length > validationConfig.maxNameLength) return false;
        const nameRegex = /^[a-zA-Z\s\-']+$/;
        return nameRegex.test(name);
    }
    
    function validateEmail(email) {
        return validationConfig.emailRegex.test(email);
    }
    
    function validateEmailConfirmation(confirmEmail, email) {
        return confirmEmail === email;
    }
    
    function validateAllFields() {
        let isValid = true;
        
        // Clear all existing errors first
        clearAllErrors();
        
        // Validate name
        if (formElements.name) {
            const nameValue = formElements.name.value.trim();
            if (!nameValue || !validateName(nameValue)) {
                showFieldError(formElements.name, 'Please enter your full name (min 2 characters)');
                isValid = false;
            }
        }
        
        // Validate email
        if (formElements.email) {
            const emailValue = formElements.email.value.trim();
            if (!emailValue || !validateEmail(emailValue)) {
                showFieldError(formElements.email, 'Please enter a valid email address');
                isValid = false;
            }
        }
        
        // Validate email confirmation
        if (formElements.confirmEmail && formElements.email) {
            const confirmValue = formElements.confirmEmail.value.trim();
            const emailValue = formElements.email.value.trim();
            if (!confirmValue || !validateEmailConfirmation(confirmValue, emailValue)) {
                showFieldError(formElements.confirmEmail, 'Email addresses do not match');
                isValid = false;
            }
        }
        
        // Validate role (required)
        if (formElements.role) {
            if (!formElements.role.value) {
                showFieldError(formElements.role, 'Please select your role');
                isValid = false;
            }
        }
        
        // Highlight first invalid field for focus
        if (!isValid) {
            const firstErrorField = waitlistForm.querySelector('.form-input.error');
            if (firstErrorField) {
                firstErrorField.focus();
            }
        }
        
        return isValid;
    }
    
    function showFieldError(field, message) {
        field.classList.add('error');
        field.classList.remove('success');
        
        // Create or update error message
        let errorElement = field.parentNode.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.opacity = '1';
        errorElement.style.transform = 'translateY(0)';
    }
    
    function showFieldSuccess(field) {
        field.classList.remove('error');
        field.classList.add('success');
        
        // Remove error message if it exists
        const errorElement = field.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.style.opacity = '0';
            errorElement.style.transform = 'translateY(-5px)';
            setTimeout(() => {
                if (errorElement.parentNode) {
                    errorElement.parentNode.removeChild(errorElement);
                }
            }, 300);
        }
    }
    
    function clearFieldError(field) {
        field.classList.remove('error');
        const errorElement = field.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    function clearAllErrors() {
        const errorElements = waitlistForm.querySelectorAll('.error-message');
        errorElements.forEach(el => el.remove());
        
        const errorFields = waitlistForm.querySelectorAll('.form-input.error');
        errorFields.forEach(field => field.classList.remove('error'));
        
        const successFields = waitlistForm.querySelectorAll('.form-input.success');
        successFields.forEach(field => field.classList.remove('success'));
    }
    
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        if (isSubmitting) return;
        
        // Validate all fields
        const isValid = validateAllFields();
        if (!isValid) {
            // Add shake animation to invalid form
            waitlistForm.classList.add('shake');
            setTimeout(() => waitlistForm.classList.remove('shake'), 500);
            return;
        }
        
        // Start submission process
        isSubmitting = true;
        const submitBtn = formElements.submitBtn;
        const originalBtnState = getButtonState(submitBtn);
        
        // Show loading state
        setButtonLoading(submitBtn, true);
        
        try {
            // Prepare form data
            const formData = new FormData(waitlistForm);
            
            // Remove confirm_email from form data (not needed for backend)
            formData.delete('confirm_email');
            
            // Send AJAX request
            const response = await fetch(waitlistForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Success - show success message and reset form
                handleSuccessResponse(data);
                waitlistForm.reset();
                clearAllErrors();
            } else {
                // Error from server
                handleErrorResponse(data, response.status);
            }
            
        } catch (error) {
            // Network error
            handleNetworkError(error);
        } finally {
            // Reset button state after timeout
            setTimeout(() => {
                setButtonLoading(submitBtn, false, originalBtnState);
                isSubmitting = false;
            }, validationConfig.loadingTimeout);
        }
    }
    
    function getButtonState(button) {
        const span = button.querySelector('span');
        const icon = button.querySelector('i');
        return {
            text: span ? span.textContent : 'Join Waitlist',
            iconClass: icon ? icon.className : 'fas fa-paper-plane'
        };
    }
    
    function setButtonLoading(button, isLoading, originalState = null) {
        const span = button.querySelector('span');
        const icon = button.querySelector('i');
        
        if (isLoading) {
            button.disabled = true;
            if (span) span.textContent = 'Processing...';
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin';
            }
        } else {
            button.disabled = false;
            if (span && originalState) span.textContent = originalState.text;
            if (icon && originalState) icon.className = originalState.iconClass;
        }
    }
    
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    
    function handleSuccessResponse(data) {
        // Show success message
        showNotification(data.message, 'success');
        
        // Update stats if provided
        if (data.total_users) {
            updateStatsCounter(data.total_users);
        }
        
        // Show early bird badge if applicable
        if (data.is_early_adopter) {
            showEarlyBirdBadge(data.position);
        }
        
        // Optional: Redirect to thank you page after 3 seconds
        setTimeout(() => {
            const params = new URLSearchParams({
                name: formElements.name ? formElements.name.value : '',
                email: formElements.email ? formElements.email.value : '',
                early: data.is_early_adopter,
                position: data.position || ''
            });
            window.location.href = `/waitlist/thanks/?${params.toString()}`;
        }, 3000);
    }
    
    function handleErrorResponse(data, statusCode) {
        let errorMessage = 'Something went wrong. Please try again.';
        
        if (data.errors) {
            // Handle server-side validation errors
            Object.keys(data.errors).forEach(fieldName => {
                const field = waitlistForm.querySelector(`[name="${fieldName}"]`);
                if (field) {
                    const errorMsg = Array.isArray(data.errors[fieldName]) 
                        ? data.errors[fieldName][0] 
                        : data.errors[fieldName];
                    showFieldError(field, errorMsg);
                }
            });
            
            // Focus on first error field
            const firstErrorField = waitlistForm.querySelector('.form-input.error');
            if (firstErrorField) {
                firstErrorField.focus();
            }
            
            return;
        }
        
        if (data.error) {
            errorMessage = data.error;
        }
        
        showNotification(errorMessage, 'error');
    }
    
    function handleNetworkError(error) {
        showNotification('Network error. Please check your connection and try again.', 'error');
    }
    
    function showNotification(message, type) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.form-notification');
        existingNotifications.forEach(n => n.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `form-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to form
        waitlistForm.parentNode.insertBefore(notification, waitlistForm);
        
        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-10px)';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto-remove after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.opacity = '0';
                    notification.style.transform = 'translateY(-10px)';
                    setTimeout(() => notification.remove(), 300);
                }
            }, 5000);
        }
    }
    
    function updateStatsCounter(newTotal) {
        const statsElement = document.querySelector('[data-total-users]');
        if (statsElement) {
            const currentTotal = parseInt(statsElement.textContent) || 0;
            animateCounter(statsElement, currentTotal, newTotal, 1000);
        }
    }
    
    function animateCounter(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value.toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
    
    function showEarlyBirdBadge(position) {
        const badgeHtml = `
            <div class="early-bird-notification">
                <div class="early-bird-content">
                    <i class="fas fa-crown"></i>
                    <div>
                        <h4>🎉 Early Bird Status!</h4>
                        <p>You're position #${position} in line</p>
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.waitlist-form-container');
        if (container) {
            container.insertAdjacentHTML('beforeend', badgeHtml);
        }
    }
    
    // Add CSS for notifications and animations
    addFormValidationStyles();
}

function addFormValidationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Form validation styles */
        .form-input.error {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.1) !important;
            animation: shake 0.5s ease-in-out;
        }
        
        .form-input.success {
            border-color: #10b981 !important;
        }
        
        .error-message {
            color: var(--accent-primary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
            opacity: 0;
            transform: translateY(-5px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .error-message:not(:empty) {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Form notifications */
        .form-notification {
            background: var(--glass-overlay);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideIn 0.3s ease-out;
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .form-notification.success {
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.1);
        }
        
        .form-notification.error {
            border-color: rgba(239, 68, 68, 0.3);
            background: rgba(239, 68, 68, 0.1);
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
        }
        
        .notification-content i {
            font-size: 1.25rem;
        }
        
        .form-notification.success .notification-content i {
            color: #10b981;
        }
        
        .form-notification.error .notification-content i {
            color: #ef4444;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.25rem;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
        }
        
        .notification-close:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Early bird notification */
        .early-bird-notification {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1));
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-top: 1.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .early-bird-content {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: #FFD700;
        }
        
        .early-bird-content i {
            font-size: 2rem;
        }
        
        .early-bird-content h4 {
            margin: 0;
            font-size: 1.25rem;
        }
        
        .early-bird-content p {
            margin: 0.25rem 0 0;
            opacity: 0.9;
        }
        
        /* Animations */
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Loading button state */
        .btn-submit:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .fa-spinner {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Mobile optimizations */
        @media (max-width: 768px) {
            .form-notification {
                padding: 0.875rem 1.25rem;
                flex-direction: column;
                align-items: stretch;
                gap: 0.75rem;
            }
            
            .notification-content {
                justify-content: center;
                text-align: center;
            }
            
            .notification-close {
                align-self: flex-end;
            }
        }
    `;
    document.head.appendChild(style);
}

// ===== SMOOTH SCROLL =====
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#0') return;
            
            const targetElement = document.querySelector(href);
            if (targetElement) {
                e.preventDefault();
                
                const isMobile = window.innerWidth < 769;
                const headerOffset = isMobile ? 60 : 0;
                const targetPosition = targetElement.offsetTop - headerOffset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                history.pushState(null, null, href);
            }
        });
    });
}

// ===== ANIMATIONS =====
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);
    
    // Observe elements
    const animateElements = document.querySelectorAll('.problem-card, .feature-card, .user-type-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .problem-card, .feature-card, .user-type-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .problem-card.animated, .feature-card.animated, .user-type-card.animated {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Staggered delays */
        .problem-card:nth-child(odd).animated { transition-delay: 0.1s; }
        .problem-card:nth-child(even).animated { transition-delay: 0.2s; }
        .feature-card:nth-child(odd).animated { transition-delay: 0.15s; }
        .feature-card:nth-child(even).animated { transition-delay: 0.25s; }
        
        /* Error states */
        .form-input.error {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.1) !important;
        }
        
        /* Mobile menu toggle animation */
        .mobile-menu-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(6px, 6px);
        }
        
        .mobile-menu-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .mobile-menu-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(6px, -6px);
        }
    `;
    document.head.appendChild(style);
}