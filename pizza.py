import os

import requests
from dotenv import load_dotenv


def get_token(client_id):
    data = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    return response.json()['access_token']


def add_product(access_token, name, slug, sku, description, price):

    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json',
    }
    product_descriprion = {
        'data': {
            'type': 'product',
            'name': name,
            'slug': slug,
            'sku': sku,
            'description': description,
            'manage_stock': False,
            'price': [
                {
                    'amount': price,
                    'currency': 'RUB',
                    'includes_tax': True
                }
            ],
            'status': 'live',
            'commodity_type': 'physical'
        }
    }

    response = requests.post(
        'https://api.moltin.com/v2/products',
        headers=headers,
        json={'data': product_descriprion}
    )

    return response.json()


load_dotenv()
client_id = os.environ['CLIENT_ID']

address_urls = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
menu_urls = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'

addresses = requests.get(address_urls).json()
products = requests.get(menu_urls).json()
product_test = products[0]
access_token = get_token(client_id)
product_id = add_product(
    access_token=access_token,
    name=product_test['name'], 
    slug=product_test['name'],
    sku=product_test['id'],
    description=product_test['description'],
    price=product_test['price']
)
print(product_id)
