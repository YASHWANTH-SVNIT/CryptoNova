#markets/views.py
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime


def market_list_view(request):
    search_term = request.GET.get('search', '')
    page = request.GET.get('page', '1')
    per_page = request.GET.get('per_page', '50')
    sort_by = request.GET.get('sort_by', 'market_cap_desc')
    
    try:
        # Convert string parameters to integers
        page = int(page)
        per_page = int(per_page)
        
        # Prepare API URL with parameters
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'inr',
            'order': sort_by,
            'per_page': per_page,
            'page': page,
            'sparkline': 'false',
            'price_change_percentage': '24h',

        }

        if search_term:
            params['ids']= search_term
        
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            coins = response.json()
            
            # Format numbers for better display
            for coin in coins:
                if coin['current_price'] > 1000:
                    coin['current_price'] = round(coin['current_price'], 2)
                elif coin['current_price'] > 0.01:
                    coin['current_price'] = round(coin['current_price'], 4)
                else:
                    coin['current_price'] = round(coin['current_price'], 8)
                    
            # Calculate pagination values
            total_coins = 500  # Approximate number of coins on CoinGecko
            total_pages = (total_coins + per_page - 1) // per_page
            
            context = {
                'coins': coins,
                'current_page': page,
                'total_pages': total_pages,
                'page_size': per_page,
                'prev_page': page > 1,
                'next_page': page < total_pages,
                'search_term': search_term,  # Add this line
                'sort_by': sort_by,  # Add this line
            }
            return render(request, 'markets/markets_list.html', context)
        else:
            return render(request, 'markets/markets_list.html', {
                'error_message': f"Error fetching data from CoinGecko: {response.status_code}"
            })
            
    except requests.exceptions.RequestException as e:
        return render(request, 'markets/markets_list.html', {
            'error_message': f"Network error: {str(e)}"
        })
    except Exception as e:
        return render(request, 'markets/markets_list.html', {
            'error_message': f"An error occurred: {str(e)}"
        })


from portfolio.models import Transaction  # ADD THIS IMPORT

def coin_detail_view(request, coin_id):
    """View to display detailed information for a specific coin."""
    coin_data = None
    error_message = None

    # Handle Buy/Sell form submission
    if request.method == 'POST' and request.user.is_authenticated:
        quantity = request.POST.get('quantity')
        transaction_type = request.POST.get('transaction_type')
        try:
            quantity = float(quantity)
            if quantity > 0 and transaction_type in ['BUY', 'SELL']:
                # Fetch current coin price (again)
                response = requests.get(f'https://api.coingecko.com/api/v3/simple/price', params={
                    'ids': coin_id,
                    'vs_currencies': 'inr'
                })
                if response.status_code == 200:
                    price_data = response.json()
                    current_price = price_data.get(coin_id, {}).get('inr', 0)
                    
                    # Save the transaction
                    Transaction.objects.create(
                        user=request.user,
                        coin_id=coin_id,
                        coin_name=coin_id.capitalize(),  # Could improve this later
                        coin_symbol=coin_id[:5].upper(), # Simple fallback symbol
                        transaction_type=transaction_type,
                        quantity=quantity,
                        price_inr=current_price,
                    )
                    return redirect('portfolio:detail')  # Redirect to portfolio after transaction
        except Exception as e:
            error_message = f"Transaction failed: {str(e)}"

    try:
        # Fetch full coin details
        coin_url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
        }
        response = requests.get(coin_url, params=params, timeout=10)
        
        if response.status_code == 200:
            coin_data = response.json()
        elif response.status_code == 429:
            error_message = "Rate limit exceeded. Please try again later."
        else:
            error_message = f"Error fetching coin data: {response.status_code}"

    except requests.exceptions.RequestException as e:
        error_message = f"Network error occurred: {str(e)}"
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"

    context = {
        'coin': coin_data,
        'coin_id': coin_id,
        'error_message': error_message,
    }

    return render(request, 'markets/coin_detail.html', context)

def api_chart_data(request):
    """API endpoint to fetch chart data for a specific coin"""
    coin_id = request.GET.get('coin_id', 'bitcoin')  # Default to bitcoin if not provided
    days = request.GET.get('days', '1')  # Default to 1 day if not provided
    
    # CoinGecko API URL for market chart data
    api_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    
    try:
        # Make request to CoinGecko API
        response = requests.get(api_url, params={
            'vs_currency': 'inr',
            'days': days,
            'interval': 'daily' if days in ['30', '365', 'max'] else None  # Use daily interval for longer periods
        })
        
        if response.status_code != 200:
            return JsonResponse({'error': f"API Error: {response.status_code}"}, status=400)
        
        data = response.json()
        
        # Process price data
        prices = data.get('prices', [])
        if not prices:
            return JsonResponse({'error': "No price data available"}, status=404)
        
        # Format data for Chart.js
        labels = []
        price_values = []
        
        for timestamp_ms, price in prices:
            # Convert timestamp to readable format based on the time range
            date = datetime.fromtimestamp(timestamp_ms / 1000)
            
            if days == '1':
                # For 1 day, show hours
                label = date.strftime('%H:%M')
            elif days in ['7', '14', '30']:
                # For 7 to 30 days, show day and month
                label = date.strftime('%d %b')
            else:
                # For longer periods, show month and year
                label = date.strftime('%b %Y')
            
            labels.append(label)
            price_values.append(price)
        
        return JsonResponse({
            'labels': labels,
            'prices': price_values
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
