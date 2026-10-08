import urllib.request
import urllib.parse
import urllib.error
import json
from dataclasses import dataclass


@dataclass
class WeatherData:
    city: str
    temp_c: int
    country: str


def format_temp(temp: float, decimals: int = 0) -> str:
    if decimals > 0:
        return f"{temp:+.{decimals}f} °C"
    return f"{round(temp):+d} °C"


def main():
    filename = 'cities.txt'

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            cities = list(dict.fromkeys(line.strip() for line in f if line.strip()))
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")
        return

    weather_results: list[WeatherData] = []

    for city in cities:
        safe_city = urllib.parse.quote(city)
        url = f"https://wttr.in/{safe_city}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                temp_c = int(data['current_condition'][0]['temp_C'])
                country = data['nearest_area'][0]['country'][0]['value']

                weather_data = WeatherData(city=city, temp_c=temp_c, country=country)
                weather_results.append(weather_data)

                print(f"{weather_data.city}, {weather_data.country} {format_temp(weather_data.temp_c)}")

        except (urllib.error.URLError, TimeoutError) as e:
            print(f"Сетевая ошибка при запросе для '{city}': {e}")
        except json.JSONDecodeError:
            print(f"Ошибка парсинга JSON для '{city}'")
        except (KeyError, ValueError, IndexError) as e:
            print(f"Неожиданная структура данных для '{city}': {e}")

    if not weather_results:
        print("\nНет данных для агрегации.")
        return

    print("\n--- Группировка по странам ---\n")

    countries_data: dict[str, list[WeatherData]] = {}
    for weather in weather_results:
        countries_data.setdefault(weather.country, []).append(weather)

    for country, items in sorted(countries_data.items()):
        temps = [item.temp_c for item in items]
        count = len(temps)
        avg_temp = sum(temps) / count

        city_word = "city" if count == 1 else "cities"

        print(f"{country} — {count} {city_word}, "
              f"avg: {format_temp(avg_temp, decimals=1)}, "
              f"min: {format_temp(min(temps))}, "
              f"max: {format_temp(max(temps))}")


if __name__ == '__main__':
    main()