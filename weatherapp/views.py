from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import datetime
from .models import WeatherRecord
from django.http import JsonResponse

# Create your views here.
API_KEY = "4861248117d4f33e5dbd1913688111d0"

def get_current_city():
    try:
        response = requests.get("https://ipinfo.io/json", timeout = 5)
        response.raise_for_status()
        data = response.json()
        city = data.get("city")
        if city:
            return city
        else:
            return "City is not found."
    except requests.exceptions.RequestException as e:
        return f"Error fetching location:{e}"

def home(request):
    
    city = country = postal_code = ''
    weather_data = {}
    image_url = "https://via.placeholder.com/1920x1080"
    
    if request.method == "POST":
        city = request.POST.get('city', '')
        country = request.POST.get('country', '')
        #postal_code = request.POST.get('postal_code', '')
        
        
        #if postal_code and country:
            #location = f"{postal_code},{country}"
        if city and country:
            location = f"{city},{country}"
        elif city:
            location = city
        else:
            location = get_current_city()
    else:
        location = get_current_city()
    
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={API_KEY}'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={API_KEY}'
    
    try:
        response = requests.get(weather_url).json()
        if response.get('cod') != 200:
            raise ValueError(response.get('message', 'Error retrieving weather'))
            
        weather_data = {
            'city': response.get('name', ''),
            'country' : response.get('sys', {}).get('country', ''),
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],                'temp': response['main']['temp'],
            'humidity' : response['main']['humidity'],
            'wind_speed': response['wind']['speed'],
            'day': datetime.date.today(),
        }
            
        record = WeatherRecord(
            city = weather_data['city'],
            country = weather_data['country'],
            date = weather_data['day'],
            temperature = weather_data['temp'],
            humidity = weather_data['humidity'],
            wind_speed = weather_data['wind_speed'],
            description = weather_data['description']
        )
        record.save()
            
            # Get main weather condition
        description = response['weather'][0]['description'].lower()
            
            # Set background image based on weather
        if "cloud" in description:
            image_url = "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?auto=format&fit=crop&w=1920&q=80"
        elif "rain" in description:
            image_url = "https://images.pexels.com/photos/459451/pexels-photo-459451.jpeg"
        elif "clear" in description:
            image_url = "https://images.pexels.com/photos/355465/pexels-photo-355465.jpeg"
        elif "snow" in description:
            image_url = "https://images.pexels.com/photos/688660/pexels-photo-688660.jpeg"
        else:
            image_url = "https://images.pexels.com/photos/531756/pexels-photo-531756.jpeg"
                        
        forecast_response = requests.get(forecast_url).json()
        forecast_list = []
        for item in forecast_response.get('list', [])[:5]:                
            forecast_list.append({
                'date': item['dt_txt'],
                'temp': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon']
            })
        weather_data['forecast'] = forecast_list
            
            
        map_url = f"https://www.google.com/maps?q={location}&output=embed"
            
        context = {
            'weather': weather_data,
            'image_url': image_url,                
            'map_url': map_url,
            'exception_occured': False
        }            
    
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        current_location = get_current_city()
        context = {
            'weather': {
                'city': current_location,
                'description': 'Data unavailable',
                'icon': '01d',
                'temp': 0,
                'humidity': 0,
                'wind_speed': 0,
                'day': datetime.date.today(),
                'forecast':[]
            },
            'image_url' : image_url,
            'map_url': 'https://maps.google.com',
            'exception_occured': True
            }

    #else:
     #   context = {
      #      'weather': {
       #         'city': 'Winnipeg',
        #        'description': 'clear sky',
         #       'icon': '01d',
          #      'temp': 0,
           #     'humidity': 0,
            #    'wind_speed': 0,
             #   'day' : datetime.date.today(),
              #  'forecast':[]
            #}
            #,
            #'image_url': image_url,
            #'map_url' : 'https://maps.google.com',
            #'exception_occured': False
        #}
        
    return render(request, 'index.html', context)


  
def delete_weather(request, record_id):
    try:
        record = WeatherRecord.objects.get(id = record_id)
        record.delete()
        messages.success(request, f"Record for {record.city} deleted!")
    except WeatherRecord.DoesNotExist:
        messages.error(request, "Record not found!")
    return redirect('home')

def update_weather(request, record_id):
    try:
        record = WeatherRecord.objects.get(id = record_id)
    except WeatherRecord.DoesNotExist:
        messages.error(request, "Record not found!")
        return redirect('home')
    
    if request.method == "POST":
        record.city = request.POST.get('city', record.city)
        record.country = request.POST.get('country', record.country)
        record.temperature = request.POST.get('temperature', record.temperature)
        record.humidity = request.POST.get('humidity', record.humidity)
        record.wind_speed = request.POST.get('wind_speed', record.wind_speed)
        record.description = request.POST.get('description', record.description)
        record.save()
        messages.success(request, f"Record for {record.city} updated!")
        return redirect('home')
    
    
def export_json(request):
    records = WeatherRecord.objects.all().values()
    data = list(records)
    return JsonResponse(data, safe = False)