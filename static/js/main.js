// core/static/core/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    /**
     * --- Theme Toggle Functionality ---
     */
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = themeToggle?.querySelector('.fa-sun');
    const moonIcon = themeToggle?.querySelector('.fa-moon');
    const htmlElement = document.documentElement; // Get the <html> element

    // Function to update icon based on theme
    function updateThemeIcon(theme) {
        if (!sunIcon || !moonIcon) return;
        if (theme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline-block';
        } else {
            sunIcon.style.display = 'inline-block';
            moonIcon.style.display = 'none';
        }
    }

    // Apply the saved theme on initial load
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Event listener for theme toggle button
    themeToggle?.addEventListener('click', () => {
        let currentTheme = htmlElement.getAttribute('data-theme');
        let newTheme = currentTheme === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme); // Save preference
        updateThemeIcon(newTheme);
    });


    /**
     * --- Mobile Menu Toggle Functionality ---
     */
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNavLinksContainer = document.querySelector('.mobile-nav-links');
    const menuIcon = mobileMenuToggle?.querySelector('i');

    mobileMenuToggle?.addEventListener('click', () => {
        const isDisplayed = mobileNavLinksContainer.style.display === 'block';
        mobileNavLinksContainer.style.display = isDisplayed ? 'none' : 'block';
        // Toggle icon
        if (menuIcon) {
            menuIcon.classList.toggle('fa-bars');
            menuIcon.classList.toggle('fa-times'); // FontAwesome close icon
        }
    });

    // Close mobile menu if window is resized to desktop width
    window.addEventListener('resize', () => {
         if (window.innerWidth > 992 && mobileNavLinksContainer.style.display === 'block') { // Match breakpoint
             mobileNavLinksContainer.style.display = 'none';
             if (menuIcon && menuIcon.classList.contains('fa-times')) {
                 menuIcon.classList.remove('fa-times');
                 menuIcon.classList.add('fa-bars');
             }
         }
     });

    // --- Add Active Class to Nav Links --- (Simple version based on path)
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a'); // Desktop links
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-links a'); // Mobile links

    function setActiveLink(links) {
         links.forEach(link => {
            // Check if the link's href is the current path OR
            // if the current path starts with the link's href (for parent sections)
            // Avoid setting '/' active if on a sub-page
             if (link.getAttribute('href') === currentPath || (currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/')) {
                 link.classList.add('active');
             } else {
                 link.classList.remove('active');
             }
         });
    }
    //setActiveLink(navLinks); // Currently disabled as sub-paths make it tricky
    //setActiveLink(mobileNavLinks);

}); // End DOMContentLoaded


/**
 * --- Global Helper Functions ---
 */

// Format number as INR currency
function formatCurrencyINR(value, options = {}) {
    const defaults = {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    };
    const formatOptions = { ...defaults, ...options };

    if (value === null || value === undefined || isNaN(value)) {
        return options.defaultValue !== undefined ? options.defaultValue : 'N/A';
    }
    return new Intl.NumberFormat('en-IN', formatOptions).format(value);
}

// Format large number (like market cap) with no decimals
function formatMarketCapINR(value) {
    return formatCurrencyINR(value, { maximumFractionDigits: 0, defaultValue: 'N/A' });
}

// Format percentage with +/- sign and class
function formatPercentage(value) {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    const formatted = value.toFixed(2);
    const className = value >= 0 ? 'positive' : 'negative';
    const sign = value >= 0 ? '+' : ''; // Keep minus sign inherent
    // Use span for styling
    return `<span class="${className}">${sign}${formatted}%</span>`;
}