import requests
import os
import time
import json
from config.system_config import JarvisConfig
from core.logger import get_logger

logger = get_logger("APIHub")

class APIHub:
    """
    Service layer for fetching external data with persistent caching.
    """
    def __init__(self):
        self.cache_file = "config/api_cache.json"
        self._ensure_cache_dir()
        self.cache = self._load_cache()

    def _ensure_cache_dir(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _is_cache_valid(self, key, expiry_hours):
        if key not in self.cache:
            return False
        timestamp = self.cache[key].get("timestamp", 0)
        return (time.time() - timestamp) < (expiry_hours * 3600)

    def get_weather(self, city: str = "Hyderabad,IN") -> dict:
        # Weather Cache: twice per 8 hours = every 4 hours
        if self._is_cache_valid("weather", 4):
            return self.cache["weather"]["data"]

        key = JarvisConfig.OPENWEATHER_API_KEY
        if not key or key == "your_key_here":
            return {
                "location": city, "temperature": 22.5, "description": "Clear skies (Sample)",
                "humidity": 45, "wind_speed": 12, "feels_like": 23
            }
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()
            weather_data = {
                "location": data["name"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"]
            }
            self.cache["weather"] = {"timestamp": time.time(), "data": weather_data}
            self._save_cache()
            return weather_data
        except Exception as e:
            logger.error(f"Weather API failed: {e}")
            return self.cache.get("weather", {}).get("data", {"error": "Weather fetch failed"})

    def get_news(self) -> list:
        # News Cache: every 5 hours
        if self._is_cache_valid("news", 5):
            return self.cache["news"]["data"]

        key = JarvisConfig.NEWS_API_KEY
        if not key or key == "your_key_here":
            return [
                {"title": "AI Breakthrough in Vision Models", "source": "TechCrunch", "time": "1h ago"},
                {"title": "New Framework for Web UI released", "source": "Dev.to", "time": "3h ago"}
            ]
        
        try:
            # Fetch both US and India news for broader coverage
            urls = [
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={key}",
                f"https://newsapi.org/v2/top-headlines?country=in&apiKey={key}"
            ]
            
            all_articles = []
            for url in urls:
                response = requests.get(url, timeout=5)
                data = response.json()
                all_articles.extend(data.get("articles", []))
            
            news_data = [{"title": art["title"], "source": art["source"]["name"], "time": "Recently"} for art in all_articles[:15]]
            self.cache["news"] = {"timestamp": time.time(), "data": news_data}
            self._save_cache()
            return news_data
        except Exception as e:
            logger.error(f"News API failed: {e}")
            return self.cache.get("news", {}).get("data", [])

    def get_movies(self) -> list:
        # Movies Cache: once per day (24 hours)
        if self._is_cache_valid("movies", 24):
            return self.cache["movies"]["data"]

        key = JarvisConfig.RAPIDAPI_KEY
        host = JarvisConfig.RAPIDAPI_HOST
        
        if not key or key == "your_key_here":
            return [
                {"title": "The Matrix Resurrections", "rating": 7.5, "genre": "Sci-Fi", "year": 2021},
                {"title": "Interstellar", "rating": 8.6, "genre": "Sci-Fi", "year": 2014}
            ]
        
        try:
            # Using GoWATCH trending movies via RapidAPI
            url = f"https://{host}/trending/movie/day"
            headers = {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": host
            }
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            
            movies_data = []
            for m in data.get("results", [])[:6]:
                movies_data.append({
                    "title": m.get("title") or m.get("original_title"),
                    "rating": m.get("vote_average"),
                    "genre": "Trending",
                    "year": m.get("release_date", "2024")[:4]
                })
            
            self.cache["movies"] = {"timestamp": time.time(), "data": movies_data}
            self._save_cache()
            return movies_data
        except Exception as e:
            logger.error(f"Movie API failed: {e}")
            return self.cache.get("movies", {}).get("data", [])

    def get_filtered_news(self, keywords=["IT", "war", "tech", "politics", "India"]) -> list:
        """Returns news articles that match specific priority keywords."""
        news = self.get_news()
        filtered = []
        for article in news:
            title = article["title"].lower()
            if any(kw.lower() in title for kw in keywords):
                filtered.append(article)
        return filtered

if __name__ == "__main__":
    hub = APIHub()
    print("Weather:", hub.get_weather())
    print("News:", hub.get_news())
    print("Movies:", hub.get_movies())
