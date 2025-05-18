// Fetch cities data
const cities = {
    "Warsaw": [52.2298, 21.0118],
    "Krakow": [50.0647, 19.9450],
    "Gdansk": [54.3520, 18.6466],
    "Tarnów": [50.0138, 20.9864],
    // Add more cities as needed
};

// Load cities into the dropdown
const citySelect = document.getElementById("city-select");
for (let city in cities) {
    const option = document.createElement("option");
    option.value = city;
    option.innerText = city;
    citySelect.appendChild(option);
}

// API Key for OpenWeatherMap
const API_KEY = 'a31216e1e9d6d6b9d716020e4e6d21d2';

// Function to calculate bike score
function calculateBikeScore(temp, rainChance, windSpeed) {
    let score = 80;
    if (temp >= 15 && temp <= 25) score += 20;
    else if (temp >= 7 && temp < 15 || temp > 25 && temp <= 28) score += 10;
    else score -= 20;

    if (rainChance < 10) score += 20;
    else if (rainChance < 40) score += 10;
    else score -= 60;

    if (windSpeed < 2) score += 20;
    else if (windSpeed < 5) score += 10;
    else score -= 30;

    return Math.max(0, Math.min(score, 100));
}

// Function to fetch the weather data
async function fetchWeatherData(lat, lon) {
    const url = `https://api.openweathermap.org/data/3.0/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly&appid=${API_KEY}&units=metric`;
    const response = await fetch(url);
    const data = await response.json();
    updateForecast(data.daily);
}

// Function to update the forecast display
function updateForecast(dailyForecast) {
    const forecastContainer = document.getElementById("forecast-container");
    forecastContainer.innerHTML = ""; // Clear previous forecasts

    dailyForecast.forEach(day => {
        const date = new Date(day.dt * 1000).toLocaleDateString();
        const temp = day.temp.day;
        const rainChance = day.pop * 100;
        const windSpeed = day.wind_speed;
        const bikeScore = calculateBikeScore(temp, rainChance, windSpeed);

        // Create forecast card
        const forecastCard = document.createElement("div");
        forecastCard.classList.add("forecast-card");

        // Calculate the stroke-dashoffset value for the score
        const circumference = 2 * Math.PI * 40; // Circumference of the circle
        const offset = circumference * (1 - bikeScore / 100); // Offset based on bikeScore percentage
        console.log(offset)

        forecastCard.innerHTML = `
            <div class="forecast-header">${date}</div>
            <div class="forecast-details">Temp: ${temp}°C</div>
            <div class="forecast-details">Wind: ${windSpeed} m/s</div>
            <div class="forecast-details">Rain Chance: ${rainChance}%</div>
            <div class="bike-score">
                <div class="score-ring" style="stroke-dashoffset: ${offset};" data-score="${bikeScore}"></div>
                <span>${bikeScore}%</span>
            </div>
        `;

        forecastContainer.appendChild(forecastCard);
    });
}

// Event listener for city selection
citySelect.addEventListener("change", (event) => {
    const city = event.target.value;
    if (city) {
        const [lat, lon] = cities[city];
        fetchWeatherData(lat, lon);
    }
});
