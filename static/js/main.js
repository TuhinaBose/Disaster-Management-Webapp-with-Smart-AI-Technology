/**
 * DISASTER MANAGEMENT WEB APPLICATION - MAIN SCRIPT
 * Enhanced with interactive scroll reveals, animated statistics counters, and button feedback.
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("Smart Disaster Management System Initialized.");

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Highlight active link in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Animated Counter for Statistics Numbers
    const counterElements = document.querySelectorAll('.stat-counter, .fw-extrabold.text-white');
    counterElements.forEach(el => {
        const text = el.textContent.trim();
        // Check if content is numeric
        if (/^\d+$/.test(text)) {
            const target = parseInt(text, 10);
            if (target > 0) {
                let current = 0;
                const duration = 1200; // ms
                const stepTime = 20;
                const totalSteps = duration / stepTime;
                const increment = Math.ceil(target / totalSteps);
                el.textContent = '0';

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        el.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        el.textContent = current.toLocaleString();
                    }
                }, stepTime);
            }
        }
    });

    // Intersection Observer for Smooth Scroll Reveal on Cards
    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('card-revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -40px 0px'
        });

        document.querySelectorAll('.glass-card').forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = `opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${index * 0.08}s, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${index * 0.08}s`;
            revealObserver.observe(card);
        });

        // Trigger reveal styling
        const style = document.createElement('style');
        style.textContent = `
            .glass-card.card-revealed {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
            .glass-card.card-revealed:hover {
                transform: translateY(-6px) scale(1.015) !important;
            }
        `;
        document.head.appendChild(style);
    }
});
