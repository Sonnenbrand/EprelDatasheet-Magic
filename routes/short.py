
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import requests
import os

short = Blueprint('short', __name__)

SHLINK_BASE_URL = os.getenv('SHLINK_BASE_URL')
SHLINK_API_KEY = os.getenv('SHLINK_API_KEY')


@short.route('/shortcreate', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form.get('longUrl')
        if not long_url:
            return render_template('shortcreate.html', error='Missing longUrl parameter')

        # SHLINK API endpoint to create a short URL
        endpoint = f"{SHLINK_BASE_URL}/rest/v2/short-urls"

        # Headers including the API key
        headers = {
            'X-Api-Key': SHLINK_API_KEY,
            'Content-Type': 'application/json'
        }

        # Payload with the long URL
        payload = {
            'longUrl': long_url
        }

        try:
            # Make the POST request to SHLINK API
            response = requests.post(endpoint, headers=headers, json=payload)

            response_data = response.json()

            if response.status_code == 200:
                short_url = response_data.get('shortUrl')
                if short_url:
                    return render_template('shortcreate.html', short_url=short_url)
                else:
                    error_message = 'Short URL not found in response'
                    print(f"Error: {error_message}")
                    return render_template('shortcreate.html', error=error_message)
            else:
                error_message = response_data.get('detail', 'An error occurred')
                print(f"Error: {error_message} (Status Code: {response.status_code})")
                return render_template('shortcreate.html', error=error_message)
        except Exception as e:
            print(f"Exception occurred: {e}")
            return render_template('shortcreate.html', error='An unexpected error occurred')

    return render_template('shortcreate.html')

@short.route('/shortlist', methods=['GET'])
def list_short_urls():
    # SHLINK API endpoint to list short URLs
    endpoint = f"{SHLINK_BASE_URL}/rest/v2/short-urls"

    # Headers including the API key
    headers = {
        'X-Api-Key': SHLINK_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        # Make the GET request to SHLINK API
        response = requests.get(endpoint, headers=headers)

        response_data = response.json()
        
        if response.status_code == 200:
            short_urls = response_data.get('shortUrls', {}).get('data', [])
            
            return render_template('shortlist.html', short_urls=short_urls)
        else:
            error_message = response_data.get('detail', 'An error occurred')
            print(f"Error: {error_message} (Status Code: {response.status_code})")
            return render_template('shortlist.html', error=error_message)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return render_template('shortlist.html', error='An unexpected error occurred')
