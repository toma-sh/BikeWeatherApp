import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
import requests

API_KEY = 'twoj_klucz_api'

# Funkcja do wczytywania miast z pliku JSON
def load_cities_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Wczytanie miast z pliku JSON
CITIES = load_cities_from_json('cities.json')

class WeatherApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # Spinner do wyboru miasta
        self.city_spinner = Spinner(
            text="Wybierz miasto",
            values=list(CITIES.keys()),
            size_hint=(1, 0.2)
        )
        self.city_spinner.bind(text=self.on_city_select)
        self.layout.add_widget(self.city_spinner)
        
        # Przyciski i etykiety
        self.title_label = Label(text="Pogoda na najbliższe 7 dni", font_size='24sp', size_hint=(1, 0.2))
        self.layout.add_widget(self.title_label)
        
        self.weather_label = Label(text="Kliknij 'Pobierz prognozę', aby zobaczyć pogodę", font_size='18sp', size_hint=(1, 0.6))
        self.layout.add_widget(self.weather_label)
        
        self.refresh_button = Button(text="Pobierz prognozę", font_size='20sp', size_hint=(1, 0.2))
        self.refresh_button.bind(on_press=self.get_weather)
        self.layout.add_widget(self.refresh_button)
        
        # Domyślne współrzędne (Warszawa)
        self.lat, self.lon = CITIES["Warszawa"]
        
        return self.layout

    def on_city_select(self, spinner, city_name):
        # Aktualizuj współrzędne na podstawie wybranego miasta
        self.lat, self.lon = CITIES[city_name]
        self.weather_label.text = f"Wybrano miasto: {city_name}. Kliknij 'Pobierz prognozę'."

    def get_weather(self, instance):
        # Wywołanie API z OpenWeatherMap One Call 3.0 dla wybranych współrzędnych
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={self.lat}&lon={self.lon}&exclude=minutely,hourly,alerts&appid={API_KEY}&units=metric&lang=pl"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            forecast_text = ""
            for day in data['daily'][:7]:  # Pobierz dane dla najbliższych 7 dni
                date = day['dt']
                temp = day['temp']['day']
                rain_chance = day.get('pop', 0) * 100  # Szansa na deszcz (pop - probability of precipitation)
                wind_speed = day['wind_speed']
                
                # Oblicz wynik procentowy na podstawie algorytmu
                bike_score = self.calculate_bike_score(temp, rain_chance, wind_speed)
                
                # Formatowanie tekstu prognozy
                forecast_text += f"{date}: {temp}°C, Szansa na deszcz: {rain_chance}%, Wiatr: {wind_speed} m/s, Ocena jazdy na rowerze: {bike_score}%\n"
            
            self.weather_label.text = forecast_text
        else:
            self.weather_label.text = "Nie udało się pobrać danych pogodowych."

    def calculate_bike_score(self, temp, rain_chance, wind_speed):
        score = 100
        
        # Ocena na podstawie temperatury
        if 15 <= temp <= 25:
            score += 20
        elif 10 <= temp < 15 or 25 < temp <= 30:
            score += 10
        else:
            score -= 20
        
        # Ocena na podstawie szansy na deszcz
        if rain_chance < 20:
            score += 20
        elif rain_chance < 50:
            score += 10
        else:
            score -= 20
        
        # Ocena na podstawie prędkości wiatru
        if wind_speed < 3:
            score += 20
        elif wind_speed < 6:
            score += 10
        else:
            score -= 20
        
        # Zabezpieczenie, aby wynik był w przedziale 0-100
        score = max(0, min(score, 100))
        
        return score

if __name__ == '__main__':
    WeatherApp().run()
