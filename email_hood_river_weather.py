import requests
import smtplib
import os
from yattag import Doc

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
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

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

    return create_html_from_weather_data(city,state,forecast_data)


def create_html_from_weather_data(city, state, forecast_data):

    # Create the HTML document
    doc, tag, text = Doc().tagtext()

    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text(f"Weather Forecast for {city},{state}")
            with tag('style'):
                text("""
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { color: #2c3e50; }
                    ul { list-style-type: none; padding: 0; }
                    li { margin-bottom: 2px; background: #f2f2f2; padding: 5px; border-radius: 5px; }
                """)
        with tag('body'):
            with tag('h1'):
                 text(f"{city},{state} Weather")
            with tag('ul'):
                    periods = forecast_data['properties']['periods']
                    for period in periods:
                        with tag('li'):
                            text(f"{period['name']}: {period['temperature']} {period['shortForecast']} {period['windDirection']} {period['windSpeed']}")
        # with open('weather_forecast.html', 'w') as f:
        #    f.write(doc.getvalue())

    return doc.getvalue()


# Example: Hood River, OR (lat=45.7054, lon=-121.5215)
if __name__ == "__main__":
    load_dotenv()
    latitude = 45.7054
    longitude = -121.5215
    forecast_html = get_noaa_weather(latitude, longitude)
    EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    send_email(EMAIL_SUBJECT, forecast_html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)
