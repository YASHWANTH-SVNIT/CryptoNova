// markets.js

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('coinSearch');
    const searchBtn = document.getElementById('searchBtn');
    const sortBySelect = document.getElementById('sortBy');
    const pageSizeSelect = document.getElementById('pageSize');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const tableBody = document.getElementById('marketsTableBody');
    
    // State
    let currentPage = parseInt(document.getElementById('currentPage').textContent.split(' ')[1]) || 1;
    let pageSize = parseInt(pageSizeSelect.value) || 50;
    let sortBy = sortBySelect.value || 'market_cap_desc';
    let searchTerm = '';
    
    // Add event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            handleSearch();
        }
    });
    
    sortBySelect.addEventListener('change', function() {
        sortBy = this.value;
        currentPage = 1; // Reset to first page on sort change
        loadMarketData();
    });
    
    pageSizeSelect.addEventListener('change', function() {
        pageSize = parseInt(this.value);
        currentPage = 1; // Reset to first page on page size change
        loadMarketData();
    });
    
    prevPageBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadMarketData();
        }
    });
    
    nextPageBtn.addEventListener('click', function() {
        currentPage++;
        loadMarketData();
    });
    
    // Handle coin row clicks to navigate to coin detail page
    document.querySelectorAll('.coin-row').forEach(row => {
        row.addEventListener('click', function() {
            const coinId = this.getAttribute('data-coin-id');
            if (coinId) {
                window.location.href = `/coin/${coinId}/`;
            }
        });
    });
    
    // Format number with commas and INR symbol
    function formatCurrency(number) {
        return '₹' + new Intl.NumberFormat('en-IN').format(number);
    }
    
    // Format percentage with + or - sign
    function formatPercentage(number) {
        const sign = number >= 0 ? '+' : '';
        return `${sign}${number.toFixed(2)}%`;
    }
    
    // Handle search
    function handleSearch() {
        searchTerm = searchInput.value.trim().toLowerCase();
        if (searchTerm) {
            // If search term is specific enough, it might be a direct coin ID
            // In a real app, we'd have an API endpoint to search for coins
            // For now, we'll just filter client-side
            tableBody.innerHTML = '<tr><td colspan="6" class="loading-message">Searching...</td></tr>';
            
            // Reset to first page and load with search term
            currentPage = 1;
            loadMarketData();
        }
    }
    
    // Load market data from API
    // Load market data from API
function loadMarketData() {
    tableBody.innerHTML = '<tr><td colspan="6" class="loading-message">Loading cryptocurrency data...</td></tr>';
    
    // Build URL with query parameters
    const url = new URL(window.location.pathname, window.location.origin);
    url.searchParams.set('page', currentPage);
    url.searchParams.set('per_page', pageSize);
    url.searchParams.set('sort_by', sortBy);
    
    if (searchTerm) {
        url.searchParams.set('search', searchTerm);
    }
    
    // Use History API to update URL without reloading
    window.history.pushState({}, '', url);
    
    // Use fetch instead of page reload
    fetch(url)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML to extract just the table content
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newTableContent = doc.getElementById('marketsTableBody').innerHTML;
            tableBody.innerHTML = newTableContent;
            
            // Re-attach event listeners to new rows
            document.querySelectorAll('.coin-row').forEach(row => {
                row.addEventListener('click', function() {
                    const coinId = this.getAttribute('data-coin-id');
                    if (coinId) {
                        window.location.href = `/coin/${coinId}/`;
                    }
                });
            });
            
            // Update pagination info
            document.getElementById('currentPage').textContent = `Page ${currentPage}`;
            
            // Initialize animations
            animateTableRows();
        })
        .catch(error => {
            showTableError(`Failed to load data: ${error}`);
        });
}
});