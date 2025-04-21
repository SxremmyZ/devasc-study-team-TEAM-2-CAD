# Enhanced Directions App

A command-line application that provides directions and travel information using free mapping APIs and enhances the experience with Google's Gemini AI.

![App Demo](https://via.placeholder.com/800x400?text=Enhanced+Directions+App)

## Features

- **Free Mapping Services**: Uses OpenStreetMap's Nominatim for geocoding and OSRM for routing
- **AI-Enhanced Directions**: Leverages Google's Gemini AI to provide additional information about your journey
- **Multiple Transportation Modes**: Support for car, bike, and walking directions
- **Detailed Turn-by-Turn Guidance**: Step-by-step directions with distance information
- **Robust Error Handling**: Gracefully handles API errors and connectivity issues
- **Dynamic AI Model Selection**: Automatically selects the best available Gemini model

## Prerequisites

- Python 3.6 or higher
- Internet connection
- Google Gemini API key

## Installation

1. Clone this repository:
   ```
   not yet
   ```

2. Install the required dependencies:
   ```
   pip install requests
   ```

3. Set up your API key:
   - Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Replace the placeholder API key in the code with your own key:
     ```python
     gemini_api_key = "YOUR_API_KEY_HERE"
     ```

## Usage

Run the application:
```
python directions_app.py
```

Follow the prompts to:
1. Choose a transportation mode (car, bike, foot)
2. Enter your starting location
3. Enter your destination
4. Review the directions and AI-enhanced information

To exit the application, type `q` or `quit` at any prompt.

## Example Output

```
===================================================
Welcome to the Enhanced Directions App!
This app uses OpenStreetMap for directions and
Google's Gemini AI to provide additional information.
===================================================

Checking available Gemini models...
Found 14 available models
===================================================

+++++++++++++++++++++++++++++++++++++++++++++
Transportation modes available:
+++++++++++++++++++++++++++++++++++++++++++++
car, bike, foot, driving, bicycling, walking
Note: 'driving' and 'bicycling' are Google Maps terms.
They will be converted to 'car' and 'bike' respectively.
To quit the program, type 'q' at any prompt.
+++++++++++++++++++++++++++++++++++++++++++++

Enter a transportation mode from the list above: car
Starting Location: New York
Destination: Boston

=================================================
Directions from New York to Boston by car
=================================================
Distance Traveled: 215.7 miles / 347.1 km
Trip Duration: 03:42:15
=================================================
1. Depart onto I-95 N (5.2 km / 3.2 miles)
2. Continue onto I-278 E (6.8 km / 4.2 miles)
...

Additional Information from Gemini AI:
=================================================
Here's some information to enhance your journey from New York to Boston by car:

Landmarks along the route:
- Yale University in New Haven, Connecticut
- Mystic Seaport, a maritime museum in Mystic, Connecticut
- Providence, Rhode Island (capital city)
- The Big Dig tunnels as you enter Boston

Historical facts:
New York:
- Originally called New Amsterdam when founded by Dutch settlers in 1624
- Became the first capital of the United States in 1789

Boston:
- Founded in 1630, making it one of America's oldest cities
- Site of the Boston Tea Party (1773) and the start of the American Revolution
- Home to the first public park (Boston Common, 1634) and public school (Boston Latin, 1635)

Travel tips:
- The I-95 corridor can get congested, especially during rush hours (7-9am, 4-7pm)
- Consider a rest stop in Mystic, CT or Providence, RI to break up the journey
- Watch for tolls along the route - have cash or electronic payment ready
- For the best skyline view of Boston, approach via the Tobin Bridge if possible
=================================================
```

## API Information

This application uses:

1. **OpenStreetMap Nominatim API**
   - For geocoding (converting addresses to coordinates)
   - Free to use with appropriate rate limiting
   - Documentation: https://nominatim.org/release-docs/latest/

2. **OSRM (Open Source Routing Machine)**
   - For calculating routes and directions
   - Free to use with appropriate rate limiting
   - Documentation: http://project-osrm.org/docs/

3. **Google Gemini API**
   - For AI-generated information about the journey
   - Requires an API key
   - Automatically detects and uses available models
   - Documentation: https://ai.google.dev/docs

## Limitations

- OSRM may not be able to calculate routes between very distant locations or across water bodies
- The quality of AI-enhanced information depends on the Gemini API's knowledge about the locations
- API rate limits may apply (the code implements proper delays to avoid hitting these limits)
- Geocoding may not find all locations, especially in remote areas or with ambiguous names

## Troubleshooting

- **No routes found**: Try locations that are closer together or within the same region
- **Geocoding errors**: Make sure location names are specific and correctly spelled
- **AI enhancement errors**: Verify your API key is valid and has access to Gemini models
- **Slow response times**: The application respects API rate limits, which may cause some delays

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenStreetMap contributors for the free mapping data
- OSRM team for the routing engine
- Google for the Gemini AI API
