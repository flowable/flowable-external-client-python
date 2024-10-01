from robocorp.actions import action

@action
def get_weather_forecast(city: str, days: int, scale: str = "celsius") -> dict[str, int]:
    # Just a random implementation which multiplies the length of the city by the days
    return {
        "temperature": days * len(city)
    }