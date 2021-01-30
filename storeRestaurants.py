# Sample Command: 
# curl -XPOST -u 'username:password' 'https://search-restaurants-ztv76gvwrmqfszdm56bl6hkkqa.us-west-2.es.amazonaws.com/_bulk' --data-binary @bulk_restaurants.json -H 'Content-Type: application/json'
import csv
import json
with open('bulk_restaurants.json', 'w') as json_file:
    for category in ['chinese', 'japanese', 'korean', 'american']:
        with open('{}++.csv'.format(category), newline = '') as csvfile:
            restaurants = csv.reader(csvfile, delimiter = ',')
            for row in restaurants:
                id = row[0]
                if id == "Business_ID":
                    continue
                cuisine = category
                index = {"index": {"_index": "restaurants", "_type": "Restaurant"}}
                info = {"RestaurantID": id, "cuisine": cuisine}
                json.dump(index, json_file)
                json_file.write('\n')
                json.dump(info, json_file)
                json_file.write('\n')
            

    
