# views.py

from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import Property
from .property_recommender import property_recommender
from .models import PropertySearch
from django.template.loader import render_to_string

from django.utils import timezone

# Load the dataset once when the server starts
df = pd.read_csv('C:/Users/shriy/property_recommendation/property_recommender/Bangalore.csv')

def home(request):
    if request.method == 'POST':
        try:
            # Extract form data
            location = request.POST.get('location')
            bedrooms = int(request.POST.get('bedrooms'))
            min_price = int(request.POST.get('min_price'))
            max_price = int(request.POST.get('max_price'))

            # Save form data to the database
            search_date_ist = timezone.localtime(timezone.now())  # Get current time in IST
            search = PropertySearch(
                location=location,
                bedrooms=bedrooms,
                min_price=min_price,
                max_price=max_price,
                search_date=search_date_ist  # Save search date in IST
            )
            search.save()
            # Call the recommendation function
            recommendations = property_recommender(df, bedrooms, min_price, max_price, location)

            # If recommendations are found, convert DataFrame to dictionary with index
            if recommendations is not None:
                recommendations = recommendations.to_dict(orient='index')

                # Filter out only the available amenities for each property
                for key, property in recommendations.items():
                    property['Amenities'] = [amenity for amenity, available in property.items()
                                              if amenity not in ["Location", "No. of Bedrooms", "Price", "Description"] and available]

            # Pass the recommendations to the template
            return render(request, 'property_recommender/recommend_properties.html', {'recommendations': recommendations})

        except (ValueError, TypeError) as e:
            # Handle invalid form data or other exceptions
            error_message = "An error occurred while processing your request. Please try again."
            return render(request, 'property_recommender/home.html', {'error_message': error_message})

    return render(request, 'property_recommender/home.html')

from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from django.utils import timezone
from .property_recommender import property_recommender  # Adjust the import based on your module structure

def related_properties(request):
    try:
        location = request.GET.get('location')
        bedrooms = int(request.GET.get('bedrooms'))
        min_price = float(request.GET.get('min_price'))
        max_price = float(request.GET.get('max_price'))

        search_date_ist = timezone.localtime(timezone.now())  # Get current time in IST
        search = PropertySearch(
            location=location,
            bedrooms=bedrooms,
            min_price=min_price,
            max_price=max_price,
            search_date=search_date_ist
        )
        search.save()

        # Call the property recommender function
        recommended_properties = property_recommender(df, bedrooms, min_price, max_price, location)

        exclude_keys = {"index", "Location", "num_bedrooms", "price", "location", "No. of Bedrooms", "Price", "Description", "Area", "Resale"}

        if recommended_properties is not None and not recommended_properties.empty:
            # Reset the index to make it a column
            recommended_properties.reset_index(inplace=True)
            
            # Convert DataFrame to dictionary
            recommendations = recommended_properties.to_dict(orient='records')

            # Convert keys for template compatibility and include amenities
            for prop in recommendations:
                prop['num_bedrooms'] = prop.pop('No. of Bedrooms', '')
                prop['price'] = prop.pop('Price', '')
                prop['location'] = prop.pop('Location', '')
                prop['amenities'] = [key for key in prop.keys() if key not in exclude_keys and prop[key]]
        else:
            recommendations = []

        return render(request, 'property_recommender/related_property.html', {'recommended_properties': recommendations})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PropertySearch
from django.db.models import Count
from django.db.models.functions import ExtractHour
import pandas as pd

@login_required
def new_home_view(request):
    return render(request, 'property_recommender/newhome.html')

from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import PropertySearch  # Adjust the import based on your module structure
from django.utils import timezone
@login_required
def get_traffic_data(request):
    try:
        # Retrieve all search dates
        searches = PropertySearch.objects.all()
        search_data = searches.values_list('search_date', flat=True)
        
        # Create a DataFrame from the search data
        df = pd.DataFrame(list(search_data), columns=['search_date'])
        
        # Convert the 'search_date' to datetime and assume it is in UTC
        df['search_date'] = pd.to_datetime(df['search_date'], utc=True)
        
        # Print the original search dates for debugging
        print("Original search dates (UTC):", df['search_date'])
        
        # Convert UTC time to IST
        df['search_date_ist'] = df['search_date'].dt.tz_convert('Asia/Kolkata')
        
        # Print the converted search dates for debugging
        print("Converted search dates (IST):", df['search_date_ist'])
        
        # Extract the hour in IST
        df['hour'] = df['search_date_ist'].dt.hour
        
        # Print the extracted hours for debugging
        print("Extracted hours (IST):", df['hour'])
        
        # Group by hour and count the occurrences
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        # Print the hourly counts for debugging
        print("Hourly counts:", hourly_counts)
        
        # Prepare the data for JSON response
        data = {
            'hours': hourly_counts['hour'].tolist(),
            'counts': hourly_counts['count'].tolist()
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@login_required
def get_rooms_data(request):
    searches = PropertySearch.objects.values('bedrooms').annotate(count=Count('id')).order_by('bedrooms')
    data = {'rooms': [item['bedrooms'] for item in searches], 'counts': [item['count'] for item in searches]}
    return JsonResponse(data)

from django.shortcuts import render
from django.http import JsonResponse
from .models import PropertySearch
from django.db.models import Count

import requests
from django.http import JsonResponse
from .models import PropertySearch
from django.conf import settings



def locations_data_api(request):
    # Query top 5 most frequent locations and their frequencies
    top_locations = PropertySearch.objects.values('location').annotate(frequency=models.Count('location')).order_by('-frequency')[:5]

    # Initialize list to store geojson features
    geojson_features = []

    # Mapbox API endpoint for geocoding
    geocoding_url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/{place}.json'

    # Mapbox access token (replace with your actual token)
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN

    for loc in top_locations:
        location_name = loc['location']

        # Make request to Mapbox Geocoding API
        response = requests.get(geocoding_url.format(place=location_name), params={'access_token': mapbox_access_token})

        # Parse the response and extract latitude and longitude
        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])
            if features:
                # Take the first result, assuming it's the most relevant
                geometry = features[0].get('geometry', {})
                if geometry.get('type') == 'Point':
                    latitude, longitude = geometry.get('coordinates', [None, None])

                    # Create GeoJSON feature
                    geojson_feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [longitude, latitude],
                        },
                        'properties': {
                            'location_name': location_name,
                            'frequency': loc['frequency']
                        }
                    }

                    geojson_features.append(geojson_feature)

    # Create GeoJSON object
    geojson_data = {
        'type': 'FeatureCollection',
        'features': geojson_features
    }

    # Return JSON response
    return JsonResponse(geojson_data)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def new_home(request):
    username = request.user.username  # Assuming username is part of your User model
    return render(request, 'your_app/newhome.html', {'username': username})

# views.py

from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import PropertySearch

def price_data_final(request):
    # Calculate date range for last 10 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=10)

    # Query PropertySearch instances within the date range
    property_searches = PropertySearch.objects.filter(search_date__range=(start_date, end_date))

    # Aggregate data
    total_min_price = property_searches.aggregate(avg_min_price=models.Avg('min_price'))['avg_min_price']
    total_max_price = property_searches.aggregate(avg_max_price=models.Avg('max_price'))['avg_max_price']

    # Prepare response data
    data = {
        'avg_min_price': total_min_price if total_min_price else 0,
        'avg_max_price': total_max_price if total_max_price else 0,
    }

    return JsonResponse(data)

from django.http import JsonResponse
from django.db.models import Avg
from django.utils.timezone import now
from datetime import timedelta
from .models import PropertySearch  # Adjust the import based on your model

def price_data_api(request):
    try:
        # Get today's date
        today = now().date()
        
        # Initialize empty lists for dates and prices
        dates = []
        avg_max_prices = []
        avg_min_prices = []

        # Iterate over the last 7 days including today
        for i in range(7):
            current_date = today - timedelta(days=i)
            # Get the data for the current date
            price_data = PropertySearch.objects.filter(search_date__date=current_date).aggregate(
                avg_max_price=Avg('max_price'),
                avg_min_price=Avg('min_price')
            )
            # Append the data to the lists
            dates.append(current_date.strftime('%B %d, %Y'))
            avg_max_prices.append(price_data['avg_max_price'] or 0)
            avg_min_prices.append(price_data['avg_min_price'] or 0)

        # Prepare data for JSON response
        data = {
            'dates': dates[::-1],  # Reverse to get dates in ascending order
            'avg_max_prices': avg_max_prices[::-1],
            'avg_min_prices': avg_min_prices[::-1],
        }

        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



from django.http import JsonResponse
from .models import PropertySearch

# Define the coordinates_dict at the module level
coordinates_dict = {
    'JP Nagar Phase 1': [77.5860843, 12.9116408],
    'Doddanekundi': [77.6964768, 12.9713194],
    'Kengeri': [77.4837568, 12.9176571],
    'Horamavu': [77.6601508, 13.0273312],
    'Thanisandra': [77.6339258, 13.054713],
    'Ramamurthy Nagar': [77.6777817, 13.0120218],
    'Electronic City Phase 1': [77.6649749, 12.8496783],
    'Yelahanka': [77.5963454, 13.1006982],
    'Anjanapura': [77.3883166, 14.1595946],
    'Jalahalli': [76.5066292, 11.9917786],
    'Kasavanahalli': [77.5675665, 13.2414761],
    'Bommasandra': [77.6916113, 12.8162443],
    'Bellandur': [77.6782471, 12.93103185],
    'RR Nagar': [77.93356445178478, 9.46693815],
    'Hosa Road': [77.64481805008592, 12.8816077],
    'Kadugodi': [77.7609716, 12.9985767],
    'Jakkur': [77.6068938, 13.0784743],
    'Jigani': [77.64102425962022, 12.7807858],
    'Krishnarajapura': [77.40031443577197, 13.1243851],
    'Varthur': [77.7469937, 12.9406152],
    'Vidyaranyapura': [77.2498674, 13.4061933],
    'Electronic City Phase 2': [77.6769267, 12.8468545],
    'J. P. Nagar': [77.5866067, 12.9096941],
    'K. Chudahalli': [77.3339009, 12.540237],
    'Narayanaghatta': [77.7260023, 12.8364852],
    'Sarjapur': [77.53841148585812, 25.24043475],
    'Koramangala': [77.7519261, 13.2923988],
    'Hebbal': [77.5919, 13.0382184],
    'Budigere Cross': [77.7504176, 13.0465209],
    'Bommanahalli': [77.6239038, 12.9089453],
    'Chikkalasandra': [77.5476337, 12.9121916],
    'Kogilu': [77.6167721, 13.103973],
    'Nayandahalli': [77.5212118, 12.9413253],
    'Bilekahalli': [77.6085699, 12.8979703],
    'Muneshwara Nagar': [77.61090664984235, 13.0155777],
    'Junnasandra': [77.6844696, 12.9106362],
    'R T Nagar': [77.58860281641668, 13.03335625],
    'JP Nagar Phase 7': [77.5866067, 12.9096941],
    'Subramanyapura': [77.5377864, 12.8963963],
    'JP Nagar Phase 4': [77.5866067, 12.9096941],
    'JP Nagar Phase 8': [77.5866067, 12.9096941],
    'Amruthahalli': [77.6007336, 13.0656864],
    'Nagarbhavi': [77.52883895255425, 13.00196975],
    'RMV Extension Stage 2': [77.5781101, 13.0222132],
    'Kudlu': [77.6555716, 12.8889126],
    'Carmelaram': [77.7065133, 12.9111998],
    'Uttarahalli': [77.5455438, 12.9055682],
}

from django.core.cache import cache

def location_frequency_api(request):
    cache.clear()  # Clear the cache at the beginning of the view
    try:
        # Fetch all location names from the PropertySearch model
        locations = PropertySearch.objects.values_list('location', flat=True)
        location_counts = {}
        
        # Count the frequency of each location
        for location in locations:
            if location in coordinates_dict:
                location_counts[location] = location_counts.get(location, 0) + 1
        
        # Prepare the data to return as JSON
        data = {
            'locations': [{'name': loc, 'coordinates': coordinates_dict[loc], 'count': count} for loc, count in location_counts.items()]
        }
        return JsonResponse(data)

    except Exception as e:
        logger.error("Error fetching location frequency data: %s", e)
        return JsonResponse({'error': 'An error occurred while fetching location frequency data.'}, status=500)
