from lambda_function import headers
import requests
import csv
import sys

if __name__ == "__main__":
    url = "https://transloc-api-1-2.p.rapidapi.com/stops.json"
    querystring = {"agencies":"1323"}
    data = requests.get(url, headers=headers, params=querystring).json()['data']
    fieldnames = ["id", "long_name", "short_names", "campus"]
    writer = csv.DictWriter(sys.stdout, fieldnames)
    for i in data:
        writer.writerow({'id': i['stop_id'], 'long_name': i['name'], 'short_names': '', 'campus': ''})

