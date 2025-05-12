document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const ctaButton = document.querySelector('.cta-button');
    
    // Add event listener for CTA button
    if (ctaButton) {
        ctaButton.addEventListener('click', function(e) {
            // The href is already set in the HTML, but we can add analytics or other functionality here
            console.log('CTA button clicked');
            // No need to prevent default as we want the normal link behavior
        });
    }
    
    // Add any animations or additional UI enhancements
    animateHeroSection();
    
    /**
     * Animate the hero section elements
     */
    function animateHeroSection() {
        // Simple fade-in animation for the headline and subheadline
        const headline = document.querySelector('.main-headline');
        const subheadline = document.querySelector('.subheadline');
        
        if (headline) {
            headline.style.opacity = '0';
            headline.style.transform = 'translateY(20px)';
            headline.style.transition = 'opacity 1s ease, transform 1s ease';
            
            setTimeout(() => {
                headline.style.opacity = '1';
                headline.style.transform = 'translateY(0)';
            }, 300);
        }
        
        if (subheadline) {
            subheadline.style.opacity = '0';
            subheadline.style.transform = 'translateY(20px)';
            subheadline.style.transition = 'opacity 1s ease, transform 1s ease';
            
            setTimeout(() => {
                subheadline.style.opacity = '1';
                subheadline.style.transform = 'translateY(0)';
            }, 600);
        }
    }
});