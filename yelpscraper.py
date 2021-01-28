#Business Search      URL -- 'https://api.yelp.com/v3/businesses/search'
#Business Match       URL -- 'https://api.yelp.com/v3/businesses/matches'
#Phone Search         URL -- 'https://api.yelp.com/v3/businesses/search/phone'

#Business Details     URL -- 'https://api.yelp.com/v3/businesses/{id}'
#Business Reviews     URL -- 'https://api.yelp.com/v3/businesses/{id}/reviews'

#Businesses, Total, Region

# Import the modules
import requests
import json
import argparse
import pprint
import sys
import urllib
from datetime import datetime
import csv

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode
# Define a business ID
unix_time = 1546047836
prefix = 'https://api.yelp.com/v3/businesses/'
# Define my API Key, My Endpoint, and My Header
API_KEY= 'X-yHBjZ6bMpwjTvCu8hFUWZ8MPnu1YqgPCZ-cvzcdafxIbeEIOnBWUuwm5KWaq3UDPXJoVGj09WTW-_TrUr0t-LqyiFHVjv6h7TfA53wTzYJMmspWSzhAdq2gyiEXHYx'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {
        'Authorization': 'Bearer ccJUZkyk9IKTnziyN1PcSmqh56SJYcIsxzBLxLqIEL2innFP3s2Cx4izjPfBb2s47MBL7nKpl6y9BEn4Ao3mt6kfZ4YXEM7TAtZEJPfIf1L8JkwxozgbjhCE-smKXHYx',
    }

# Define my parameters of the search
PARAMETERS = {
            'location': "New York",
            'offset': 0,
            'limit': 50,
            'term': 'Chinese' + " restaurants",
            'sort_by': 'rating'
    }


# Make a request to the Yelp API
response = requests.get(url = ENDPOINT,
                        params = PARAMETERS,
                        headers = HEADERS)

# Conver the JSON String
business_data = response.json()
business = business_data.get("businesses")
business_id = business[0]['id']
response = requests.request('GET', prefix + business_id, headers=HEADERS, params={})
response = response.json()
# print the response
print(response['id'], response['name'], str(response['location']['address1']), response['coordinates'],   response['rating'], response['location']['zip_code'])
json_file = json.dumps(business_data, indent = 3)
#print(json_file)
