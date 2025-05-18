import os
import json
import requests
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle, Line

# Wczytanie klucza API z pliku .env
load_dotenv()
API_KEY = os.getenv('API_KEY')



from kivy.graphics import Color, RoundedRectangle, Line

class DayForecast(BoxLayout):
    def __init__(self, date, temp, rain_chance, wind_speed, bike_score, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 150
        self.padding = 10
        self.spacing = 20  # Dodanie większej odległości między ramkami (współczynnik odstępu)

        # Ustalenie koloru tła na podstawie bike_score
        color_value = 1 - (bike_score / 100)  # Przemiana bike_score na wartość od 0 do 1
        background_color = (color_value, 1 - color_value, 0, 1)  # Zielony dla wysokiego wyniku, czerwony dla niskiego

        # Tło ramki dnia z zaokrąglonymi rogami
        with self.canvas.before:
            Color(*background_color)  # Użycie koloru tła
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])  # Zaokrąglone rogi (promień 20)
            self.bind(size=self.update_rect, pos=self.update_rect)

            # Krawędź ramki
            edge_color = (0, 0, 0, 1)  # Czarne krawędzie
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2, color=edge_color)

        # Kolumna z tekstowymi danymi
        text_layout = BoxLayout(orientation='vertical', padding=5)
        formatted_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')
        
        # Zmieniony kolor czcionki dla każdego labela
        text_layout.add_widget(Label(text=f"Data: {formatted_date}", font_size=16, color=(0.2, 0.5, 1, 1)))  # Niebieski kolor
        text_layout.add_widget(Label(text=f"Temperatura: {temp}°C", font_size=16, color=(1, 0.5, 0, 1)))  # Pomarańczowy kolor
        text_layout.add_widget(Label(text=f"Wiatr: {wind_speed} m/s", font_size=16, color=(0, 0.7, 0, 1)))  # Zielony kolor
        text_layout.add_widget(Label(text=f"Szansa na deszcz: {rain_chance}%", font_size=16, color=(0.8, 0.8, 0, 1)))  # Żółty kolor
        
        # Wykres kołowy
        img = self.create_pie_chart(bike_score)
        chart_img = Image(texture=img.texture, size_hint=(1, 1))
        chart_layout = BoxLayout(size_hint=(0.4, 1))
        chart_layout.add_widget(chart_img)

        # Dodanie do głównego układu
        self.add_widget(text_layout)
        self.add_widget(chart_layout)

    def create_pie_chart(self, score):
        fig, ax = plt.subplots()
        ax.pie([score, 100 - score], colors=['#4CAF50', '#E0E0E0'], startangle=90)
        ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=20, color="black")
        ax.set_aspect('equal')
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = CoreImage(buf, ext='png')
        buf.close()
        plt.close(fig)
        return img

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.border.rectangle = (self.x, self.y, self.width, self.height)  # Aktualizacja krawędzi



class ForecastApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        
        # Spinner do wyboru miasta
        self.city_spinner = Spinner(
            text='Wybierz miasto',
            size_hint=(1, 0.1)
        )
        self.city_spinner.bind(text=self.on_city_select)
        root.add_widget(self.city_spinner)
        
        # ScrollView do przewijania prognozy
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.days_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.days_layout.bind(minimum_height=self.days_layout.setter('height'))
        self.scroll_view.add_widget(self.days_layout)
        
        # Wczytanie listy miast
        self.load_cities()
        
        # Dodanie ScrollView do głównego układu
        root.add_widget(self.scroll_view)
        
        return root

    def load_cities(self):
        # Wczytanie pliku JSON z miastami
        with open("cities.json", "r", encoding="utf-8") as f:
            self.cities = json.load(f)
        
        # Dodanie miast do spinnera
        for city in self.cities.keys():
            self.city_spinner.values = list(self.cities.keys())

    def on_city_select(self, spinner, city):
        # Pobranie współrzędnych wybranego miasta
        coords = self.cities.get(city)
        if coords:
            lat, lon = coords
            self.fetch_forecast(lat, lon)

    def fetch_forecast(self, lat, lon):
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            self.update_forecast(data["daily"])
        else:
            print(f"Nie udało się pobrać danych: {response.status_code}")

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


    def update_forecast(self, daily_forecast):
        # Czyszczenie poprzednich prognoz
        self.days_layout.clear_widgets()
        
        for day in daily_forecast:
            date = day['dt']
            temp = day['temp']['day']
            rain_chance = day.get('pop', 0) * 100  # pop - probability of precipitation
            wind_speed = day['wind_speed']
            # Oblicz wynik procentowy na podstawie algorytmu
            bike_score = self.calculate_bike_score(temp, rain_chance, wind_speed)
            
            # Dodanie prognozy dnia
            forecast = DayForecast(
                date=date,
                temp=temp,
                rain_chance=rain_chance,
                wind_speed=wind_speed,
                bike_score=bike_score
            )
            self.days_layout.add_widget(forecast)

if __name__ == '__main__':
    ForecastApp().run()
