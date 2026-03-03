import json
import googlemaps
import os
import time

# Load API Key
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if not api_key:
    print("❌ GOOGLE_MAPS_API_KEY not found.")
    exit(1)

gmaps = googlemaps.Client(key=api_key)

try:
    with open('routes.json', 'r', encoding='utf-16') as f:
        routes = json.load(f)
except Exception as e:
    print(f"Error reading routes.json: {e}")
    exit(1)

# Sampling if too many to avoid long runs and API costs
# Actually, the user wants EXACT, so let's try to process as many as possible
# but safely.
unique_lines = {} # key: line_id, value: {agency, vehicle, name, short_name}

print(f"Analyzing {len(routes)} unique routes...")

for i, route in enumerate(routes):
    origin = f"{route['CEP']}, Brasil"
    dest = f"{route['ENDEREÇO OBRA']}, Brasil"
    
    if i % 10 == 0:
        print(f"Processing {i}/{len(routes)}...")

    try:
        res = gmaps.directions(origin, dest, mode="transit", language="pt-BR")
        if res:
            for leg in res[0].get('legs', []):
                for step in leg.get('steps', []):
                    if step.get('travel_mode') == 'TRANSIT':
                        details = step.get('transit_details', {})
                        line = details.get('line', {})
                        short_name = line.get('short_name', 'N/A')
                        name = line.get('name', 'N/A')
                        agency = line.get('agencies', [{}])[0].get('name', 'N/A')
                        vehicle = line.get('vehicle', {}).get('name', 'N/A')
                        
                        line_id = f"{agency}_{short_name}"
                        if line_id not in unique_lines:
                            unique_lines[line_id] = {
                                "agency": agency,
                                "vehicle": vehicle,
                                "short_name": short_name,
                                "name": name
                            }
    except Exception as e:
        print(f"Error on route {i}: {e}")
    
    time.sleep(0.05)

with open('unique_lines.json', 'w', encoding='utf-8') as f:
    json.dump(unique_lines, f, indent=2, ensure_ascii=False)

print(f"Done! Found {len(unique_lines)} unique lines. Saved to unique_lines.json")
