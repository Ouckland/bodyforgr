// ===== MINIMAL RIGHT-SIDE NAVIGATION =====
function initMinimalNavigation() {
    const minimalNav = document.getElementById('minimalNav');
    const navDots = minimalNav.querySelectorAll('.nav-dot');
    const progressFill = minimalNav.querySelector('.progress-fill');
    const navBrand = minimalNav.querySelector('.nav-brand');
    
    if (!minimalNav) return;
    
    // Update active dot and progress
    function updateNavigation() {
        const sections = document.querySelectorAll('section');
        const scrollPosition = window.scrollY + 100;
        
        // Update progress indicator
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (window.scrollY / totalHeight) * 100;
        progressFill.style.height = `${progress}%`;
        
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
            
            // Scroll to section
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = 80;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL
                history.pushState(null, null, targetId);
                
                // Add click feedback
                const dotElement = this.querySelector('.dot');
                dotElement.style.transform = 'scale(1.5)';
                setTimeout(() => {
                    dotElement.style.transform = 'scale(1)';
                }, 200);
            }
        });
    });
    
    // Brand click handler
    navBrand.addEventListener('click', function() {
        // Scroll to top
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        
        // Add click animation
        this.style.transform = 'scale(0.9)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 200);
    });
    
    // Update on scroll
    window.addEventListener('scroll', updateNavigation);
    
    // Initial update
    updateNavigation();
    
    // Add parallax effect to progress track
    function updateNavParallax() {
        const scrollY = window.scrollY;
        const progressTrack = minimalNav.querySelector('.progress-track');
        
        // Subtle parallax effect
        progressTrack.style.transform = `translateY(${scrollY * 0.05}px)`;
    }
    
    window.addEventListener('scroll', updateNavParallax);
    
    // Add CSS for smooth transitions
    const style = document.createElement('style');
    style.textContent = `
        .nav-dot.active .dot {
            animation: dotPulse 2s ease-in-out infinite;
        }
        
        @keyframes dotPulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 0 8px rgba(0, 255, 255, 0.5);
            }
            50% {
                transform: scale(1.2);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
            }
        }
        
        /* Smooth scroll */
        html {
            scroll-behavior: smooth;
        }
    `;
    document.head.appendChild(style);
}

// Update the main init function
document.addEventListener('DOMContentLoaded', function() {
    initMinimalNavigation(); // Replace initGuidelineNavigation with this
    initSmoothScroll();
    initFormValidation();
    initAnimations();
    initParallaxEffect();
});