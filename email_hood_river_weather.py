import requests
import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


# --- Configuration ---
EMAIL_FROM = "dan.mcnerthney@gmail.com" 
EMAIL_TO = "dan.mcnerthney@gmail.com" 
EMAIL_SUBJECT = f'Weather Forecast'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587



# --- Send email ---
def send_email(subject, body, from_email, to_email, password):

    print(password)
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def get_noaa_weather(lat, lon):
    # Step 1: Get the forecast office and grid info for the given lat/lon
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(points_url)
    response.raise_for_status()
    data = response.json()

    # Step 2: Extract the forecast URL
    forecast_url = data['properties']['forecast']
    city = data['properties']['relativeLocation']['properties']['city']
    state = data['properties']['relativeLocation']['properties']['state']

    # Step 3: Get the forecast
    forecast_response = requests.get(forecast_url)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    forecast_text = f"Weather Forecast for {city}, {state}:\n"
    periods = forecast_data['properties']['periods']
    for period in periods:
        # print(f"{period['name']}: {period['detailedForecast']}")
        forecast_text += f"{period['name']}: {period['temperature']} {period['shortForecast']} {period['windDirection']} {period['windSpeed']}"

    return forecast_text

# Example: Hood River, OR (lat=45.7054, lon=-121.5215)
if __name__ == "__main__":
    load_dotenv()
    latitude = 45.7054
    longitude = -121.5215
    forecast = get_noaa_weather(latitude, longitude)
    EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    send_email(EMAIL_SUBJECT, forecast, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)
