 
if (typeof Chart === 'undefined') {
    console.error('Chart.js is not loaded!');
}

let marketOverviewChartInstance = null; // Global variable to hold the chart instance

/**
 * Function to format currency in INR format
 * @param {number} value - The value to format
 * @param {object} options - Formatting options
 * @returns {string} - Formatted currency string
 */
function formatCurrencyINR(value, options = {}) {
    const defaults = { 
        style: 'currency', 
        currency: 'INR',
        maximumFractionDigits: 2
    };
    const mergedOptions = {...defaults, ...options};
    return new Intl.NumberFormat('en-IN', mergedOptions).format(value);
}

/**
 * Function to fetch chart data from the backend API
 * @param {string} coinId - The ID of the coin (e.g., 'bitcoin')
 * @param {string} days - The number of days ('1', '7', '30', '365', 'max')
 * @param {string} apiUrl - The URL of the backend API endpoint
 * @returns {Promise<object|null>} - A promise resolving to the chart data or null on error
 */
async function fetchChartData(coinId, days, apiUrl) {
    const url = `${apiUrl}?coin_id=${coinId}&days=${days}`;
    const loadingIndicator = document.querySelector('.overview-chart-container .chart-loading');
    if(loadingIndicator) loadingIndicator.style.display = 'block'; // Show loading

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        if (!data.prices || data.prices.length === 0) {
            console.warn(`No price data received for ${coinId} (${days} days)`);
            return null; // Return null if no price data
        }
        return data;
    } catch (error) {
        console.error("Error fetching chart data:", error);
        // Display error message to user
        const chartContainer = document.getElementById('marketOverviewChart')?.parentElement;
        if (chartContainer) {
            // Remove existing error message if any
            const existingError = chartContainer.querySelector('.chart-error-message');
            if (existingError) existingError.remove();
            
            // Create new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chart-error-message error';
            errorDiv.textContent = 'Could not load chart data.';
            chartContainer.appendChild(errorDiv);
        }
        return null; // Indicate failure
    } finally {
        if(loadingIndicator) loadingIndicator.style.display = 'none'; // Hide loading
    }
}

/**
 * Helper function to determine appropriate fraction digits for y-axis
 * @param {number} value - The value to format
 * @returns {number} - Number of fraction digits to display
 */
function getFractionDigits(value) {
    if (value === 0) return 2;
    const absValue = Math.abs(value);
    if (absValue >= 1) return 2;
    if (absValue < 0.001) return 8;
    if (absValue < 0.01) return 6;
    if (absValue < 0.1) return 4;
    return 2; 
}

/**
 * Function to create or update the market overview chart
 * @param {object} chartData 
 */
function renderMarketOverviewChart(chartData) {
    const ctx = document.getElementById('marketOverviewChart')?.getContext('2d');
    if (!ctx) {
        console.error('Canvas context not found for marketOverviewChart');
        return;
    }
    
    // Remove any previous error messages
    const chartContainer = ctx.canvas.parentElement;
    const existingError = chartContainer.querySelector('.chart-error-message');
    if (existingError) existingError.remove();

    // If no data, show message and destroy old chart if exists
    if (!chartData || !chartData.prices || chartData.prices.length === 0) {
        if (marketOverviewChartInstance) {
            marketOverviewChartInstance.destroy();
            marketOverviewChartInstance = null;
        }
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height); // Clear canvas
        ctx.font = "16px 'Poppins', sans-serif";
        ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-muted-color') || '#757575';
        ctx.textAlign = "center";
        ctx.fillText("No data available for this period.", ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const gridColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const labelColor = theme === 'dark' ? '#bdbdbd' : '#424242';
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim() || '#673ab7';

    const chartConfig = {
        type: 'line',
        data: {
            labels: chartData.labels, // Timestamps from API
            datasets: [{
                label: 'Price (INR)',
                data: chartData.prices, // Prices from API
                borderColor: primaryColor,
                borderWidth: 2,
                pointRadius: 0, // Hide points for cleaner line
                tension: 0.1, // Slight curve
                fill: true, // Fill area below line
                backgroundColor: (context) => { // Gradient fill
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) return null; // Return if chartArea is not defined yet

                    // Use the dynamically fetched primary color for gradient
                    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    // Extract RGB values from primaryColor for gradient
                    let primaryRgb = primaryColor;
                    // Convert hex to rgba if needed
                    if (primaryColor.startsWith('#')) {
                        const r = parseInt(primaryColor.slice(1, 3), 16);
                        const g = parseInt(primaryColor.slice(3, 5), 16);
                        const b = parseInt(primaryColor.slice(5, 7), 16);
                        primaryRgb = `rgba(${r}, ${g}, ${b}`;
                    } else if (primaryColor.startsWith('rgb(')) {
                        // Convert rgb() to rgba()
                        primaryRgb = primaryColor.replace('rgb(', 'rgba(').replace(')', ',');
                    }
                    
                    gradient.addColorStop(0, `${primaryRgb}, 0.0)`); // Start transparent
                    gradient.addColorStop(1, `${primaryRgb}, 0.3)`); // End with primary color (30% opacity)
                    return gradient;
                },
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: {
                        color: labelColor,
                        maxRotation: 0, // Prevent label rotation
                        autoSkip: true, // Automatically skip labels to prevent overlap
                        maxTicksLimit: 7 // Limit the number of visible ticks
                    },
                    grid: {
                        display: false // Hide vertical grid lines
                    },
                    border: {
                        color: gridColor // X-axis line color
                    }
                },
                y: {
                    ticks: {
                        color: labelColor,
                        callback: function(value) {
                            // Format Y-axis labels as currency
                            return formatCurrencyINR(value, { maximumFractionDigits: getFractionDigits(value) });
                        }
                    },
                    grid: {
                        color: gridColor // Horizontal grid lines
                    },
                    border: {
                        display: false // Hide Y-axis line itself
                    }
                }
            },
            plugins: {
                legend: {
                    display: false // Hide legend if only one dataset
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: theme === 'dark' ? '#333' : '#fff',
                    titleColor: theme === 'dark' ? '#eee' : '#333',
                    bodyColor: theme === 'dark' ? '#eee' : '#333',
                    borderColor: gridColor,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += formatCurrencyINR(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            hover: { // More responsive hover
                mode: 'nearest',
                intersect: true
            }
        }
    };

    // Destroy previous chart instance if it exists
    if (marketOverviewChartInstance) {
        marketOverviewChartInstance.destroy();
    }

    // Create new chart instance
    marketOverviewChartInstance = new Chart(ctx, chartConfig);
}

/**
 * Initialize the overview chart and set up event listeners for range buttons
 * @param {string} initialCoinId - The coin ID to load initially
 * @param {string} apiUrl - The URL for the chart data API endpoint
 */
function initializeOverviewChart(initialCoinId, apiUrl) {
    // Validate inputs
    if (!initialCoinId || !apiUrl) {
        console.error('Missing required parameters: initialCoinId or apiUrl');
        return;
    }
    
    const rangeButtons = document.querySelectorAll('.chart-toggle .btn-chart-range');
    const chartCoinNameSpan = document.getElementById('chart-coin-name'); // Span to display current coin name

    // Function to load chart based on button clicked
    async function loadChart(event) {
        const button = event.target.closest('.btn-chart-range'); // Ensure we get the button
        if (!button) return;

        const days = button.dataset.days;
        const coinId = button.dataset.coin || initialCoinId; // Use button's coin or default

         // Update active button state
        rangeButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

         // Update coin name display (simple capitalize)
         if (chartCoinNameSpan) {
             chartCoinNameSpan.textContent = coinId.charAt(0).toUpperCase() + coinId.slice(1);
         }

        // Fetch and render
        const data = await fetchChartData(coinId, days, apiUrl);
        if (data) {
            renderMarketOverviewChart(data);
        } else {
            // Handle case where no data is returned (already handled in renderMarketOverviewChart)
            renderMarketOverviewChart(null);
        }
    }

    // Attach event listeners to buttons
    rangeButtons.forEach(button => {
        button.addEventListener('click', loadChart);
    });

    // Initial load (find the default active button - usually '1D')
    const initialActiveButton = document.querySelector('.chart-toggle .btn-chart-range.active') || rangeButtons[0];
    if (initialActiveButton) {
        const initialDays = initialActiveButton.dataset.days;
        const initialCoin = initialActiveButton.dataset.coin || initialCoinId;
        
        // Debug output
        console.log(`Loading initial chart: ${initialCoin}, ${initialDays} days, API: ${apiUrl}`);
        
        if (chartCoinNameSpan) { // Set initial name
            chartCoinNameSpan.textContent = initialCoin.charAt(0).toUpperCase() + initialCoin.slice(1);
        }
        
        fetchChartData(initialCoin, initialDays, apiUrl).then(data => {
            renderMarketOverviewChart(data);
        });
    } else {
        console.warn("No initial active chart button found.");
        // Optionally load default (e.g., bitcoin 1d) anyway
        console.log(`Loading default chart: ${initialCoinId}, 1 day, API: ${apiUrl}`);
        fetchChartData(initialCoinId, '1', apiUrl).then(data => {
            renderMarketOverviewChart(data);
        });
    }

    // Re-render chart on theme change to update colors
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            // Small delay to allow theme variables to update
            setTimeout(() => {
                const activeButton = document.querySelector('.chart-toggle .btn-chart-range.active');
                if (activeButton) { // Check if there's an active button
                    const currentDays = activeButton.dataset.days;
                    const currentCoin = activeButton.dataset.coin || initialCoinId;
                    fetchChartData(currentCoin, currentDays, apiUrl).then(data => {
                        renderMarketOverviewChart(data); // Re-render with new theme colors
                    });
                }
            }, 100);
        });
    }
}

// IMPORTANT: Remove the problematic event listener that tries to initialize with default values
// This would conflict with the initialization in index.html