# core/api_client.py

import requests
from django.conf import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

API_BASE_URL = settings.COINGECKO_API_BASE_URL
VS_CURRENCY = settings.DEFAULT_VS_CURRENCY

def make_api_request(endpoint, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {'accept': 'application/json'} 
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30) 
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"API Request Timeout to {url} with params {params}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"API Connection Error to {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"API HTTP Error for {url}: {e.response.status_code} - {e.response.text}")
        return None 
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error to {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during API request to {url}: {e}")
        return None


def get_global_market_data():
    endpoint = "/global"
    data = make_api_request(endpoint)
    if data and 'data' in data:
        try:
            market_data = data['data']
            total_mcap = market_data.get('total_market_cap', {}).get(VS_CURRENCY)
            mcap_change_24h = market_data.get('market_cap_change_percentage_24h_usd')
            active_cryptos = market_data.get('active_cryptocurrencies')
            markets = market_data.get('markets')

            return {
                'total_market_cap_inr': total_mcap,
                'market_cap_change_percentage_24h': mcap_change_24h,
                'active_cryptocurrencies': active_cryptos,
                'markets': markets,
            }
        except KeyError as e:
             logger.error(f"KeyError parsing global market data: {e} - Data: {data}")
             return None
    return None

def get_trending_coins():
    endpoint = "/search/trending"
    data = make_api_request(endpoint)
    if data and 'coins' in data:
         trending_list = []
         coin_ids = [item['item']['id'] for item in data['coins'][:7] if 'item' in item and 'id' in item['item']] 
         if not coin_ids:
             return []

         coin_details = get_coins_market_data(ids=','.join(coin_ids))

         if coin_details:
             details_map = {coin['id']: coin for coin in coin_details}
             for item in data['coins'][:5]: 
                 coin_info = item.get('item')
                 if coin_info and coin_info['id'] in details_map:
                     detail = details_map[coin_info['id']]
                     trending_list.append({
                         'id': coin_info.get('id'),
                         'name': coin_info.get('name'),
                         'symbol': coin_info.get('symbol','').upper(),
                         'thumb': coin_info.get('thumb'),
                         'market_cap_rank': coin_info.get('market_cap_rank'),
                         'current_price': detail.get('current_price'),
                         'price_change_percentage_24h': detail.get('price_change_percentage_24h'),
                     })
         return trending_list
    return [] 


def get_coins_market_data(ids=None, category=None, limit=50, page=1, sparkline=False, price_change_percentage='24h'):
    endpoint = "/coins/markets"
    params = {
        'vs_currency': VS_CURRENCY,
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': page,
        'sparkline': str(sparkline).lower(),
        'price_change_percentage': price_change_percentage, 
        'locale': 'en'
    }
    if ids:
        params['ids'] = ids 
    if category:
        params['category'] = category


    return make_api_request(endpoint, params=params)

def get_coin_market_chart(coin_id, days='1', interval=None):
    endpoint = f"/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': VS_CURRENCY,
        'days': str(days), 
    }
    
    if not isinstance(days, str):
        days = str(days)
    
    if interval:
        params['interval'] = interval
    
    try:
        if days == '1' and interval is None:
            pass
        elif days == 'max':
            params['interval'] = 'daily'
        elif days.isdigit() and int(days) > 90 and interval == 'hourly':
            logger.warning(f"Hourly interval requested for {days} days for {coin_id}. API might default to daily.")
            params['interval'] = 'daily' 
        elif days.isdigit() and int(days) <= 90 and interval is None:
            pass
    except ValueError:
        logger.warning(f"Invalid days parameter: {days} for {coin_id}. Using default API behavior.")

    chart_data = make_api_request(endpoint, params=params)

    if chart_data and 'prices' in chart_data and chart_data['prices']:
        try:
            date_format = '%Y-%m-%d %H:%M' if days == '1' else '%Y-%m-%d'
            
            formatted_data = {
                'labels': [datetime.fromtimestamp(price[0] / 1000).strftime(date_format) for price in chart_data['prices']],
                'prices': [price[1] for price in chart_data['prices']],
                'market_caps': [mc[1] for mc in chart_data.get('market_caps', [])],
                'total_volumes': [tv[1] for tv in chart_data.get('total_volumes', [])],
            }
            
            if chart_data['prices']:
                logger.debug(f"Chart data for {coin_id} ({days} days): First point: {chart_data['prices'][0]}, Last point: {chart_data['prices'][-1]}, Total points: {len(chart_data['prices'])}")
            
            return formatted_data
        except Exception as e:
            logger.error(f"Error formatting chart data for {coin_id}: {e}")
            return None
    else:
        logger.error(f"Could not fetch or parse market chart data for {coin_id} (days={days}, interval={interval})")
        return {
            'labels': [],
            'prices': [],
            'market_caps': [],
            'total_volumes': []
        }

