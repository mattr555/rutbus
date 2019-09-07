import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from botocore.vendored import requests

from secrets import transloc_key

url = "https://transloc-api-1-2.p.rapidapi.com/arrival-estimates.json"

headers = {
    'x-rapidapi-host': "transloc-api-1-2.p.rapidapi.com",
    'x-rapidapi-key': transloc_key
}

routes = list(csv.DictReader(open('routes.csv')))
stops = list(csv.DictReader(open('stops.csv')))

def response(code, text):
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': text
    }
    
def time_to(timestr):
    dt = datetime.fromisoformat(timestr)
    return (dt.astimezone(timezone.utc) - datetime.now(timezone.utc)).seconds // 60

def right_pad(s, n, ch=' '):
    prefix = ''
    while len(s) > n:
        spaceind = s[:n].rfind(' ')
        prefix += s[:spaceind] + ' ' * (n - spaceind - 1) + '\n'
        s = '  ' + s[spaceind + 1:]
    return prefix + s + ch * (n - len(s))
    
def help_page():
    route_res = ', '.join([i['short_name'] for i in routes])
    campuses = sorted(set([i['campus'] for i in stops]))
    res = 'rutb.us: plaintext Rutgers bus predictions\nUsage: curl https://rutb.us/<route_or_stop>\n\n'
    res += 'Routes: ' + route_res + '\n\n' + 'Stops\n=====\n'
    for campus in campuses:
        res += right_pad(campus, 10) + ': '
        res += ', '.join(sorted(set([n for i in stops for n in i['short_names'].split(',') if i['campus'] == campus])))
        res += '\n'
        
    res += '\nMore information available at https://github.com/mattr555/rutbus\n'
    return res

def lambda_handler(event, context):
    if event['httpMethod'] != 'GET':
        return response(405, 'Method Not Allowed')
        
    if event['pathParameters'] is None:
        return response(200, help_page())
    
    search = event['pathParameters']['proxy']
    requested_routes = [i['id'] for i in routes if i['short_name'] == search]
    requested_stops = [i['id'] for i in stops if search in i['short_names'].split(',')]
    
    if len(requested_routes) > 0:
        resp = requests.get(url, headers=headers, params={"agencies": "1323", "routes": ','.join(requested_routes)}).json()
        route_name, route_order = [(i['long_name'], i['stops'].split(',')) for i in routes if i['id'] == requested_routes[0]][0]
        res = f"Predictions for {route_name}\n\n"
        
        stop_times = {}
        for stop in resp['data']:
            stop_name = [i['long_name'] for i in stops if i['id'] == stop['stop_id']][0]
            times = []
            for arrival in stop['arrivals']:
                times.append(str(time_to(arrival['arrival_at'])))
            if times:
                stop_times[stop['stop_id']] = (stop_name, times)
        
        for i in route_order:
            if i in stop_times:
                rendered_stop = right_pad(stop_times[i][0], 30)
                rendered_times = ': ' + ", ".join(stop_times[i][1][:3])
                ind = rendered_stop.find('\n')
                res += rendered_stop[:ind] + rendered_times + rendered_stop[ind:] + '\n'

        return response(200, res)
    
    elif len(requested_stops) > 0:
        resp = requests.get(url, headers=headers, params={"agencies": "1323", "stops": ','.join(requested_stops)}).json()
        
        stop_times = {}
        for stop in resp['data']:
            stop_name = [i['long_name'] for i in stops if i['id'] == stop['stop_id']][0]
            times = defaultdict(list)
            for arrival in stop['arrivals']:
                times[arrival['route_id']].append(str(time_to(arrival['arrival_at'])))
            stop_times[stop_name] = times
        
        res = ''
        for stop_name in sorted(stop_times.keys()):
            res += '\n' + stop_name + '\n' + '=' * len(stop_name) + '\n'
            for route_id in sorted(stop_times[stop_name].keys()):
                route_name = [i['long_name'] for i in routes if i['id'] == route_id][0]
                rendered_route = right_pad(route_name, 15)
                rendered_times = ': ' + ", ".join(stop_times[stop_name][route_id][:3])
                ind = rendered_route.find('\n')
                res += rendered_route[:ind] + rendered_times + rendered_route[ind:] + '\n'
            
        return response(200, res)
        
    else:
        return response(404, 'Route or stop not found. Available requests:\n\n' + help_page())
    