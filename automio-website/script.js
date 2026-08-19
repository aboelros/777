document.addEventListener('DOMContentLoaded', () => {
    
    // --- Page Transitions ---
    const pageTransition = document.querySelector('.page-transition');
    if (pageTransition) {
        // Fade out on load
        setTimeout(() => {
            pageTransition.classList.add('fade-out');
            setTimeout(() => {
                pageTransition.style.display = 'none';
            }, 600); // Wait for transition to finish
        }, 300);

        // Intercept links for fade in
        document.querySelectorAll('a').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                const target = this.getAttribute('target');
                
                // Don't intercept anchor links, mailto, tel, or target="_blank"
                if (!href || href.startsWith('#') || href.includes('index.html#') || href.startsWith('mailto:') || href.startsWith('tel:') || target === '_blank') {
                    return;
                }

                e.preventDefault();
                
                pageTransition.style.display = 'flex';
                // Small delay to allow display:flex to apply before changing opacity
                setTimeout(() => {
                    pageTransition.classList.remove('fade-out');
                }, 10);

                setTimeout(() => {
                    window.location.href = href;
                }, 600);
            });
        });
    }

    // --- Mobile Menu Toggle ---
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            if (navLinks.style.display === 'flex') {
                navLinks.style.display = 'none';
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '100%';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.background = '#050505';
                navLinks.style.padding = '1rem 0';
                navLinks.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
            }
        });
    }

    // --- Smooth Scrolling ---
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            
            // Only smooth scroll if the link points to an anchor on the current page
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const isHomePage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
            const isLinkToHomeAnchor = href.startsWith('index.html#') || href.startsWith('#');
            
            if (isHomePage && isLinkToHomeAnchor) {
                e.preventDefault();
                
                if (window.innerWidth <= 768 && navLinks.style.display === 'flex') {
                    navLinks.style.display = 'none';
                }

                const targetId = href.includes('#') ? '#' + href.split('#')[1] : href;
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    const navHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // --- Navbar Blur on Scroll ---
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(5, 5, 5, 0.95)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.background = 'rgba(5, 5, 5, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    });

    // --- FAQ Accordion ---
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            // Close other open items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
            // Toggle current item
            item.classList.toggle('active');
        });
    });

    // --- Form Submission Handling ---
    const contactForm = document.getElementById('contactForm');
    const formSuccess = document.getElementById('formSuccess');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const emailInput = document.getElementById('emailInput');
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Loading state
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            try {
                // Using FormSubmit.co for free, no-registration email forwarding
                await fetch('https://formsubmit.co/ajax/arnold@automio.online', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        email: emailInput.value,
                        _subject: "New Automio Architecture Demo Request"
                    })
                });

                // Hide form and show success message smoothly
                contactForm.style.opacity = '0';
                setTimeout(() => {
                    contactForm.classList.add('hidden');
                    formSuccess.classList.remove('hidden');
                }, 300);

            } catch (error) {
                console.error("Error submitting form:", error);
                submitBtn.textContent = 'Error. Try Again.';
                submitBtn.disabled = false;
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                }, 3000);
            }
        });
    }

    // --- Scroll Animations (Intersection Observer) ---
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Optional: Stop observing once animated
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });

    // --- Custom Interactive Cursor ---
    const cursor = document.createElement('div');
    cursor.classList.add('custom-cursor');
    document.body.appendChild(cursor);

    const cursorDot = document.createElement('div');
    cursorDot.classList.add('custom-cursor-dot');
    document.body.appendChild(cursorDot);

    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        cursorDot.style.left = e.clientX + 'px';
        cursorDot.style.top = e.clientY + 'px';
    });

    // Expand cursor on hoverable elements
    const hoverables = document.querySelectorAll('a, button, .feature-card, .pricing-card');
    hoverables.forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover-link'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover-link'));
    });

    // --- 3D Tilt Effect for Cards ---
    const tiltCards = document.querySelectorAll('.feature-card, .pricing-card');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const tiltX = ((y - centerY) / centerY) * -10; // Max tilt 10deg
            const tiltY = ((x - centerX) / centerX) * 10;
            
            card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        });
    });

});
