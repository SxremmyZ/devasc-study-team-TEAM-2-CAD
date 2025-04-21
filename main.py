import requests
import urllib.parse
import json
import time
import datetime

# API configuration
gemini_api_url = "https://generativelanguage.googleapis.com/v1beta"
gemini_api_key = "AIzaSyDwahtFFk8KunjI8gE9Oo21kEvVU25lotA"  # Replace with your Gemini API key

# OpenStreetMap APIs (for geocoding and directions) - free alternatives
nominatim_url = "https://nominatim.openstreetmap.org/search"
osrm_url = "http://router.project-osrm.org/route/v1"

def geocoding(location, key=None):
    """
    Get geocoding information for a location using OpenStreetMap Nominatim API
    
    Args:
        location (str): The location to geocode
        key (str): Not needed for Nominatim
        
    Returns:
        tuple: (status_code, lat, lng, formatted_address)
    """
    # Don't send empty location
    while location == "":
        location = input("Enter the location again: ")
        
    # Construct the URL - no API key required for Nominatim
    url = nominatim_url + "?" + urllib.parse.urlencode({
        "q": location,
        "format": "json",
        "limit": 1
    })
    
    # Add a user agent header as required by Nominatim
    headers = {
        "User-Agent": "DirectionsApp/1.0"
    }
    
    try:
        # Be polite and respect rate limits (max 1 request per second)
        time.sleep(1)
        
        # Send the request to Nominatim
        response = requests.get(url, headers=headers)
        json_status = response.status_code
        
        # Check if the request was successful and results are not empty
        if json_status == 200:
            json_data = response.json()
            
            if len(json_data) > 0:
                # Extract latitude, longitude, and formatted address
                lat = float(json_data[0]["lat"])
                lng = float(json_data[0]["lon"])
                formatted_address = json_data[0]["display_name"]
                
                if "type" in json_data[0]:
                    location_type = json_data[0]["type"]
                else:
                    location_type = "place"
                
                print(f"Geocoding API URL for {formatted_address} (Location Type: {location_type})")
                print(url)
                
                return json_status, lat, lng, formatted_address
            else:
                print(f"Geocoding API URL for {location} returned no results")
                print(url)
                return json_status, "null", "null", location
        else:
            # Handle errors
            print(f"Geocode API status: {json_status}\nError with request")
            return json_status, "null", "null", location
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 500, "null", "null", location

def get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode, key=None):
    """
    Get directions between two points using OpenStreetMap OSRM API
    
    Args:
        origin_lat (float): Latitude of origin
        origin_lng (float): Longitude of origin
        dest_lat (float): Latitude of destination
        dest_lng (float): Longitude of destination
        mode (str): Mode of transportation (driving, walking, bicycling)
        key (str): Not needed for OSRM
        
    Returns:
        tuple: (status_code, directions_data)
    """
    # Convert transportation mode to OSRM profile
    if mode.lower() == "driving" or mode.lower() == "car":
        osrm_profile = "car"
    elif mode.lower() == "walking" or mode.lower() == "foot":
        osrm_profile = "foot"
    elif mode.lower() == "bicycling" or mode.lower() == "bike":
        osrm_profile = "bike"
    else:
        # Default to car if mode not recognized
        osrm_profile = "car"
    
    # Construct the URL
    url = f"{osrm_url}/{osrm_profile}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&steps=true&annotations=true"
    
    try:
        # Be polite and respect rate limits
        time.sleep(1)
        
        # Send the request to OSRM
        response = requests.get(url)
        json_status = response.status_code
        
        print(f"Routing API Status: {json_status}")
        print(f"Routing API URL:\n{url}")
        
        if json_status == 200:
            json_data = response.json()
            return json_status, json_data
        else:
            return json_status, {"code": "Error", "message": f"Status code: {json_status}"}
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 500, {"code": "Error", "message": str(e)}

def list_available_gemini_models(key):
    """
    List all available Gemini models for the given API key
    
    Args:
        key (str): API key for Gemini
        
    Returns:
        list: List of available model names
    """
    url = f"{gemini_api_url}/models"
    headers = {
        "x-goog-api-key": key
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models_data = response.json()
            available_models = []
            if "models" in models_data:
                for model in models_data["models"]:
                    if "name" in model:
                        model_name = model["name"].split("/")[-1]  # Extract just the model name
                        # Check if model supports generateContent
                        if "supportedGenerationMethods" in model and "generateContent" in model["supportedGenerationMethods"]:
                            available_models.append(model_name)
            return available_models
        else:
            print(f"Error listing models: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
            return []
    except Exception as e:
        print(f"Exception listing models: {str(e)}")
        return []

def enhance_directions_with_gemini(origin, destination, mode, directions_data, key, model=None):
    """
    Enhance directions data with additional information using Gemini API
    
    Args:
        origin (str): Origin location name
        destination (str): Destination location name
        mode (str): Mode of transportation
        directions_data (dict): Directions data from OSRM
        key (str): API key for Gemini
        model (str): Gemini model to use (will be determined if None)
        
    Returns:
        str: Enhanced directions information
    """
    # Extract basic directions information
    if directions_data.get("code") != "Ok" or "routes" not in directions_data or not directions_data["routes"]:
        return "Could not enhance directions - no valid directions data available."
    
    # First, list available models to determine which one to use
    if model is None:
        print("Checking for compatible Gemini models...")
        available_models = list_available_gemini_models(key)
        
        # Try to find a suitable model
        preferred_models = ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro", "text-bison", "gemini-1.5-flash"]
        selected_model = None
        
        for preferred in preferred_models:
            if preferred in available_models:
                selected_model = preferred
                break
                
        if not selected_model and available_models:
            # Use the first available model if none of the preferred ones are available
            selected_model = available_models[0]
            
        if not selected_model:
            return "No Gemini models available for your API key. Please check your API key or account permissions."
            
        model = selected_model
        print(f"Using Gemini model: {model}")
    
    route = directions_data["routes"][0]
    
    # Calculate distance and duration in user-friendly format
    distance_km = route["distance"] / 1000  # Convert meters to kilometers
    distance_miles = distance_km / 1.61     # Convert kilometers to miles
    
    # Convert seconds to hours, minutes, seconds
    duration_seconds = route["duration"]
    duration_time = str(datetime.timedelta(seconds=int(duration_seconds)))
    
    # Create a prompt for Gemini to enhance the directions
    prompt = f"""
    I'm traveling from {origin} to {destination} by {mode}. 
    The route is approximately {distance_km:.1f} km ({distance_miles:.1f} miles) 
    and will take about {duration_time}.
    
    Based on this information, could you provide:
    1. Any special landmarks along this route
    2. Brief historical facts about {origin} and {destination}
    3. Any travel tips for this journey
    
    Keep your response concise, focusing on interesting and helpful information.
    """
    
    # Construct URL based on the model name
    full_url = f"{gemini_api_url}/models/{model}:generateContent"
    
    # Prepare the headers with API key
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key  # Key should be in header, not in URL
    }
    
    # Prepare the request payload according to Gemini API specs
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        # Send the request to Gemini API
        response = requests.post(full_url, headers=headers, json=data)
        
        # Print details for debugging
        print(f"Gemini API Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the generated text
            try:
                # Fixed the path to extract text from the response
                candidates = response_data.get("candidates", [])
                if candidates and len(candidates) > 0:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts and len(parts) > 0:
                        response_text = parts[0].get("text", "")
                        return response_text
                return "Could not extract enhancement text from Gemini response."
            except (KeyError, IndexError) as e:
                print(f"Error parsing Gemini response: {str(e)}")
                # Print response for debugging
                print(f"Response: {json.dumps(response_data, indent=2)}")
                return "Could not extract enhancement text from Gemini response."
        else:
            # Try to get more detailed error information
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_msg = error_data["error"]["message"]
                # Print error response for debugging
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                error_msg = f"Status code: {response.status_code}"
                
            return f"Error enhancing directions with Gemini: {error_msg}"
            
    except Exception as e:
        print(f"Error connecting to Gemini API: {str(e)}")
        return f"Error: {str(e)}"

def display_directions(directions_data, origin, destination, mode, enhanced_info=None):
    """
    Format and display directions information from OSRM
    
    Args:
        directions_data (dict): Directions data from OSRM
        origin (str): Origin location
        destination (str): Destination location
        mode (str): Mode of transportation
        enhanced_info (str): Enhanced information from Gemini API
    """
    if directions_data.get("code") != "Ok" or "routes" not in directions_data or not directions_data["routes"]:
        print("=================================================")
        print(f"Directions from {origin} to {destination} by {mode}")
        print("=================================================")
        print(f"Error: {directions_data.get('code', 'Unknown error')}")
        if "message" in directions_data:
            print(f"Error message: {directions_data['message']}")
        print("*************************************************")
        return
    
    route = directions_data["routes"][0]
    
    # Calculate distance in miles and kilometers
    distance_meters = route["distance"]  # in meters
    km = distance_meters / 1000
    miles = km / 1.61
    
    # Get duration in hh:mm:ss format
    duration_seconds = route["duration"]  # in seconds
    hr = int(duration_seconds / 3600)
    min = int((duration_seconds % 3600) / 60)
    sec = int(duration_seconds % 60)
    
    # Display summary information
    print("=================================================")
    print(f"Directions from {origin} to {destination} by {mode}")
    print("=================================================")
    print(f"Distance Traveled: {miles:.1f} miles / {km:.1f} km")
    print(f"Trip Duration: {hr:02d}:{min:02d}:{sec:02d}")
    print("=================================================")
    
    # Display turn-by-turn directions
    if "legs" in route and len(route["legs"]) > 0:
        leg = route["legs"][0]  # Get the first leg
        if "steps" in leg:
            for i, step in enumerate(leg["steps"], 1):
                # Extract maneuver and road name information
                maneuver = ""
                if "maneuver" in step:
                    if "type" in step["maneuver"]:
                        maneuver = step["maneuver"]["type"].capitalize()
                    if "modifier" in step["maneuver"]:
                        maneuver += " " + step["maneuver"]["modifier"]
                
                # Get road name if available
                road = ""
                if "name" in step and step["name"]:
                    road = "onto " + step["name"]
                
                # Format the instruction
                instruction = maneuver
                if road:
                    instruction += " " + road
                
                # If no maneuver info, provide basic guidance
                if not instruction or instruction.isspace():
                    instruction = "Continue straight"
                
                # Format distance
                step_distance_m = step["distance"]
                step_distance_km = step_distance_m / 1000
                step_distance_mi = step_distance_km / 1.61
                
                print(f"{i}. {instruction} ({step_distance_km:.1f} km / {step_distance_mi:.1f} miles)")
    
    # If no steps found but there's a route geometry
    else:
        print(f"Follow the route ({km:.1f} km / {miles:.1f} miles)")
        print("Arrive at destination")
    
    print("=================================================")
    
    # Display enhanced information if available
    if enhanced_info:
        print("\nAdditional Information from Gemini AI:")
        print("=================================================")
        print(enhanced_info)
        print("=================================================")

def main():
    """Main function for the directions application"""
    
    print("\n" + "=" * 50)
    print("Welcome to the Enhanced Directions App!")
    print("This app uses OpenStreetMap for directions and")
    print("Google's Gemini AI to provide additional information.")
    print("=" * 50 + "\n")
    
    # Check for available Gemini models at startup
    print("Checking available Gemini models...")
    available_models = list_available_gemini_models(gemini_api_key)
    if available_models:
        print(f"Found {len(available_models)} available models")
    else:
        print("Warning: No Gemini models found. AI enhancement may not be available.")
        print("Please check your API key and ensure you have access to Gemini models.")
    print("=" * 50 + "\n")
    
    while True:
        # Display available transportation modes
        print("\n+++++++++++++++++++++++++++++++++++++++++++++")
        print("Transportation modes available:")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        print("car, bike, foot, driving, bicycling, walking")
        print("Note: 'driving' and 'bicycling' are Google Maps terms.")
        print("They will be converted to 'car' and 'bike' respectively.")
        print("To quit the program, type 'q' at any prompt.")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        
        # Get transportation mode
        valid_modes = ["car", "bike", "foot", "driving", "bicycling", "walking"]
        mode = input("Enter a transportation mode from the list above: ").lower()
        if mode in ["quit", "q"]:
            print("Thank you for using the Enhanced Directions App. Goodbye!")
            break
        elif mode in valid_modes:
            # Map to OSRM profile naming if user enters Google-style modes
            if mode == "driving":
                mode = "car"
            elif mode == "bicycling":
                mode = "bike"
            elif mode == "walking":
                mode = "foot"
        else:
            mode = "car"
            print("No valid transportation mode was entered. Using the car mode.")
        
        # Get origin location
        loc1 = input("Starting Location: ")
        if loc1 in ["quit", "q"]:
            print("Thank you for using the Enhanced Directions App. Goodbye!")
            break
        
        # Get origin coordinates
        orig = geocoding(loc1)
        if orig[1] == "null" or orig[2] == "null":
            print("Could not find the starting location. Please try again.")
            continue  # If geocoding failed, restart the loop
        
        # Get destination location
        loc2 = input("Destination: ")
        if loc2 in ["quit", "q"]:
            print("Thank you for using the Enhanced Directions App. Goodbye!")
            break
        
        # Get destination coordinates
        dest = geocoding(loc2)
        if dest[1] == "null" or dest[2] == "null":
            print("Could not find the destination. Please try again.")
            continue  # If geocoding failed, restart the loop
        
        print("=================================================")
        
        # If both geocoding requests were successful, get directions
        if orig[0] == 200 and dest[0] == 200:
            # Get directions from OSRM
            directions_status, directions_data = get_directions(
                orig[1], orig[2], dest[1], dest[2], mode
            )
            
            # If directions request was successful, display directions
            if directions_status == 200 and directions_data.get("code") == "Ok":
                try:
                    if available_models:
                        # Get enhanced information from Gemini
                        print("Fetching additional information from Gemini AI...")
                        enhanced_info = enhance_directions_with_gemini(
                            orig[3], dest[3], mode, directions_data, gemini_api_key
                        )
                        
                        # Display directions with enhanced information
                        display_directions(directions_data, orig[3], dest[3], mode, enhanced_info)
                    else:
                        print("Skipping AI enhancement - no available Gemini models")
                        display_directions(directions_data, orig[3], dest[3], mode)
                except Exception as e:
                    print(f"Error while enhancing directions: {str(e)}")
                    # Still display directions even if enhancement fails
                    display_directions(directions_data, orig[3], dest[3], mode)
            else:
                # Display error if directions request failed
                print(f"Directions API Status: {directions_status}")
                if "message" in directions_data:
                    print(f"Error message: {directions_data['message']}")
                print("*************************************************")
                print("Note: OSRM may not be able to calculate routes between very distant locations.")
                print("Try locations that are closer together or within the same region.")

if __name__ == "__main__":
    main()