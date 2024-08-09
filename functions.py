import requests
import json
import polyline

# Google api 경로 계산
def compute_routes(api_key, origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "mode": "transit",
        "key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
    
    
# OpenRoute api 도보 거리 계산
def get_walking_directions(api_key, origin, destination):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/json"

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [origin[1], origin[0]],  # OpenRouteService는 [longitude, latitude] 순으로 좌표를 받습니다.
            [destination[1], destination[0]]
        ],
        "instructions": "true"
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
    

# json 파일로 맵 생성
def get_html_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()

html_content = get_html_file('mapView.html')

def map_call(route_json):
    json_script = f'<script id="json-data" type="application/json">{json.dumps(route_json)}</script>'
    html_with_json = html_content.replace(
        '<script id="json-data" type="application/json"></script>', 
        json_script
    )
    return html_with_json


html_content2 = get_html_file('index.html')

def map_call2(route_json):
    json_script = f'<script id="json-data" type="application/json">{json.dumps(route_json)}</script>'
    html_with_json = html_content2.replace(
        '<script id="json-data" type="application/json"></script>', 
        json_script
    )
    
    return html_with_json


# def make_json(open_json):
#     result = "{\"routes\": [{\"bounds\": {\"northeast\": {\"lat\": "
#     result = result + str(open_json['bbox'][1]) + ", \"lng\": " + str(open_json['bbox'][0])
#     result = result + "}, \"southwest\": {\"lat\": " + str(open_json['bbox'][3]) + ", \"lng\": " + str(open_json['bbox'][2])
#     result = result + "}\}, \"copyrights\": \"true\"" + ", \"legs\": [{\'distance\': {\"value\": " + str(open_json['routes'][0]['summary']['distance']) + "},"
#     result = result + " \"steps\": ["
#     result = result + make_steps(open_json)
#     return result


# def make_steps(opj):
#     encoded_geometry = opj['routes'][0]['geometry']
#     decoded = polyline.decode(encoded_geometry)

#     step = opj['routes'][0]['segments'][0]['steps']
#     result = ""
#     for i in range(len(step)-1):
#         result = result + "{\"end_location\": {\"lat\": " + str(decoded[step[i]['way_points'][1]])
#         result = result + ", \"lng\": " + str(decoded[step[i]['way_points'][0]]) + "}, \"start_location\": {\"lat\": "
#         if(i == 0):
#             result = result + str(opj['bbox'][1]) + ", \"lng\": " + str(opj['bbox'][0])
#         else:
#             result = result + str(decoded[step[i-1]['way_points'][1]]) + ", \"lng\": " + str(decoded[step[i-1]['way_points'][0]])
#         result = result + "}, \"html_instructions\": \"" + step[i]['instruction'] + "\", \"travel_mode\": \"WALKING\"},"
#     result = result[:-1] + "]}]}], \"status\": \"OK\"}"
#     return result

def make_json(open_json):
    # Create the JSON structure as a dictionary
    result = {
        "routes": [{
            "bounds": {
                "northeast": {
                    "lat": open_json['bbox'][1],
                    "lng": open_json['bbox'][0]
                },
                "southwest": {
                    "lat": open_json['bbox'][3],
                    "lng": open_json['bbox'][2]
                }
            },
            "copyrights": "true",
            "legs": [{
                "distance": {
                    "value": open_json['routes'][0]['summary']['distance']
                },
                "steps": make_steps(open_json)
            }]
        }],
        "status": "OK"
    }
    
    # Convert the dictionary to a JSON string
    return json.dumps(result)

def make_steps(opj):
    encoded_geometry = opj['routes'][0]['geometry']
    decoded = polyline.decode(encoded_geometry)

    step = opj['routes'][0]['segments'][0]['steps']
    steps = []
    for i in range(len(step)):
        start_location = {
            "lat": decoded[step[i]['way_points'][0]][0],
            "lng": decoded[step[i]['way_points'][0]][1]
        }
        end_location = {
            "lat": decoded[step[i]['way_points'][1]][0],
            "lng": decoded[step[i]['way_points'][1]][1]
        }
        
        if i == 0:
            start_location = {
                "lat": opj['bbox'][1],
                "lng": opj['bbox'][0]
            }
        
        steps.append({
            "start_location": start_location,
            "end_location": end_location,
            "html_instructions": step[i]['instruction'],
            "travel_mode": "WALKING"
        })
    
    return steps