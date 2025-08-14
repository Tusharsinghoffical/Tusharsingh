// Custom JavaScript for GiftNest

document.addEventListener('DOMContentLoaded', function() {
    // Logo animation on scroll
    const logo = document.querySelector('.navbar-brand img');
    if (logo) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                logo.style.transform = 'scale(0.8)';
            } else {
                logo.style.transform = 'scale(1)';
            }
        });
    }

    // Logo loading animation
    const logos = document.querySelectorAll('img[src*="GIFTNEST.png"]');
    logos.forEach(logo => {
        if (logo) {
            logo.classList.add('logo-loading');
            // Check if image is already loaded
            if (logo.complete) {
                logo.style.animationDelay = '0.2s';
            } else {
                logo.addEventListener('load', function() {
                    this.style.animationDelay = '0.2s';
                });
            }
        }
    });

    // Enable Bootstrap tooltips (with error handling)
    try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    } catch (error) {
        console.warn('Bootstrap tooltips not available:', error);
    }

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Quantity input validation
    var quantityInputs = document.querySelectorAll('input[type="number"][name="quantity"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            var value = parseInt(this.value) || 1;
            var max = parseInt(this.getAttribute('max')) || 999;
            var min = parseInt(this.getAttribute('min')) || 1;

            if (value > max) {
                this.value = max;
            }
            if (value < min) {
                this.value = min;
            }
        });
    });

    // Add to cart animation
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn, .btn-add-to-cart');
    addToCartButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-check"></i> Added!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 1000);
            }, 500);
        });
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile menu toggle enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking on a link
        const mobileMenuLinks = navbarCollapse.querySelectorAll('a');
        mobileMenuLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }
});
