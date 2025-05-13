# core/view.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse 
from . import api_client
import json 
import logging

logger = logging.getLogger(__name__)


def _handle_api_error(data, default=None, error_msg="Error fetching data from API."):
    if data is None:
        logger.warning(error_msg) 
        return default, error_msg 
    return data, None 


def index_view(request):
    global_data, global_error = _handle_api_error(
        api_client.get_global_market_data(),
        default={},
        error_msg="Failed to fetch global market data."
    )
    trending_coins, trending_error = _handle_api_error(
        api_client.get_trending_coins(),
        default=[],
        error_msg="Failed to fetch trending coins."
    )
    # Fetch top 10 coins for Movers/Gainers/Losers sections
    top_coins, top_coins_error = _handle_api_error(
        api_client.get_coins_market_data(limit=10, price_change_percentage='24h'), # Ensure 24h % change is requested
        default=[],
        error_msg="Failed to fetch top coins market data."
    )

    # Prepare market movers (e.g., top 5 by absolute % change)
    market_movers = []
    if top_coins:
        # Sort by absolute value of 24h price change percentage
        try:
            market_movers = sorted(
                top_coins,
                key=lambda x: abs(x.get('price_change_percentage_24h', 0) or 0), # Handle None value
                reverse=True
            )[:5] # Get top 5
        except Exception as e:
             logger.error(f"Error sorting market movers: {e}")


    # Combine errors for display (optional)
    api_errors = [msg for msg in [global_error, trending_error, top_coins_error] if msg]

    context = {
        'global_data': global_data,
        'trending_coins': trending_coins, # Already limited to 5 in api_client logic
        'market_movers': market_movers,
        'top_coins': top_coins[:5], # Can reuse top coins for another section if needed
        'api_errors': api_errors, # Pass errors to template to optionally display
        # Initial chart data (e.g., Bitcoin for overview) - fetched via separate request later
        'initial_chart_coin_id': 'bitcoin', # Example: Default chart is Bitcoin
    }
    return render(request, 'core/index.html', context)

def placeholder_view(request, page_name="Placeholder"):
    """Generic view for simple static-like pages."""
    # You could create a specific template 'core/placeholder.html'
    # Or render simple HttpResponse for now
    # return render(request, 'core/placeholder.html', {'page_name': page_name})
    return HttpResponse(f"<h1>{page_name}</h1><p>Content for this page is coming soon.</p><a href='/'>Go Home</a>")

# --- API Views (for AJAX calls from frontend) ---

def market_chart_data_api(request):
    """API endpoint to fetch market chart data dynamically."""
    coin_id = request.GET.get('coin_id', 'bitcoin') # Default to bitcoin
    days = request.GET.get('days', '1') # Default to 1 day
    interval = request.GET.get('interval') # Optional interval

    # Validate 'days' input if necessary (e.g., ensure it's a number or allowed string)
    allowed_days = ['1', '7', '14', '30', '90', '180', '365', 'max']
    if days not in allowed_days:
        try:
            # Allow integer days as well, convert to string
            days = str(int(days))
            if int(days) < 1: days = '1'
        except ValueError:
            days = '1' # Default if invalid

    chart_data = api_client.get_coin_market_chart(coin_id, days=days, interval=interval)

    if chart_data:
        return JsonResponse(chart_data)
    else:
        return JsonResponse({'error': f'Could not fetch chart data for {coin_id}.'}, status=500)