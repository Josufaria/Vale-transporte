
import googlemaps
import os
import json

# Load API Key
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if not api_key:
    print("❌ GOOGLE_MAPS_API_KEY not found.")
    exit(1)

gmaps = googlemaps.Client(key=api_key)

# Test Coordinates/Addresses (Using generic São Paulo addresses for testing)
# MASP to Ibirapuera
origin = "Av. Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-200"
dest = "Av. Pedro Álvares Cabral - Vila Mariana, São Paulo - SP"

print(f"🕵️ Investigating route from '{origin}' to '{dest}'...")

try:
    # We use 'directions' instead of 'distance_matrix' to see if we get FARE info
    directions_result = gmaps.directions(
        origin,
        dest,
        mode="transit",
        transit_routing_preference="less_walking", # optimize for bus/subway
        language="pt-BR"
    )

    if directions_result:
        route = directions_result[0]
        
        # Check for Fare
        if "fare" in route:
            print(f"\n💰 Fare Found: {route['fare']}")
        else:
            print("\n⚠️ No 'fare' information in the response.")

        # Check Legs
        legs = route.get("legs", [])
        if legs:
            print(f"\n📏 Distance: {legs[0]['distance']['text']}")
            print(f"⏱️ Duration: {legs[0]['duration']['text']}")
            
            # Check Steps for specific transit agencies/lines
            steps = legs[0].get("steps", [])
            transit_count = 0
            print("\n🚌 Transit Layout:")
            for step in steps:
                if step.get("travel_mode") == "TRANSIT":
                    transit_count += 1
                    details = step.get("transit_details", {})
                    line = details.get("line", {}).get("short_name", "Unknown Line")
                    vehicle = details.get("line", {}).get("vehicle", {}).get("name", "Bus")
                    print(f"   - {vehicle} ({line})")
            
            print(f"\n🔄 Total Transit Legs (Buses/Trains): {transit_count}")
        
        # Save full JSON for inspection if needed
        with open("debug_route.json", "w", encoding="utf-8") as f:
            json.dump(directions_result, f, indent=4, ensure_ascii=False)
            print("\n💾 Full response saved to 'debug_route.json'")

    else:
        print("❌ No routes found.")

except Exception as e:
    print(f"❌ Error: {e}")
