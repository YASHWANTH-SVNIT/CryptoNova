from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
import requests

@login_required
def portfolio_view(request):
    # Fetch all user transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate holdings
    holdings = {}
    for tx in transactions:
        if tx.coin_id not in holdings:
            holdings[tx.coin_id] = {
                'coin_name': tx.coin_name,
                'coin_symbol': tx.coin_symbol,
                'quantity': 0,
                'average_buy_price': 0,
                'total_spent': 0,
            }
        if tx.transaction_type == 'BUY':
            holdings[tx.coin_id]['quantity'] += tx.quantity
            holdings[tx.coin_id]['total_spent'] += tx.quantity * tx.price_inr
        elif tx.transaction_type == 'SELL':
            
                holdings[tx.coin_id]['quantity'] -= tx.quantity
                holdings[tx.coin_id]['total_spent'] -= tx.quantity * tx.price_inr
            
    
    # Remove coins with zero or negative holdings
    holdings = {coin_id: data for coin_id, data in holdings.items() if data['quantity'] > 0}
    
    # Fetch current prices (simple)
    coin_ids = ','.join(holdings.keys())
    current_prices = {}
    if coin_ids:
        try:
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=inr")
            if response.status_code == 200:
                current_prices = response.json()
        except Exception as e:
            print("Error fetching prices:", e)
    
    # Calculate portfolio stats
    portfolio_value = 0
    for coin_id, data in holdings.items():
        current_price = current_prices.get(coin_id, {}).get('inr', 0)
        data['current_price'] = current_price
        data['current_value'] = current_price * data['quantity']
        data['profit_loss'] = data['current_value'] - data['total_spent']
        portfolio_value += data['current_value']
    
    context = {
        'holdings': holdings,
        'transactions': transactions,
        'portfolio_value': portfolio_value,
    }
    return render(request, 'portfolio/portfolio_detail.html', context)
