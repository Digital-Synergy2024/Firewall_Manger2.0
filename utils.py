from datetime import datetime
import re
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError

def log_action(action):
    """Log actions with timestamps."""
    with open("action_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - ACTION: {action}\n")

def log_error(error):
    """Log errors with timestamps."""
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.now()} - ERROR: {error}\n")

def is_valid_ip(ip):
    """Validate an IP address."""
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(pattern.match(ip))

def download_image_from_url(url):
    """Download an image from a URL and return it as a PIL Image object."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
        image_data = BytesIO(response.content)
        return Image.open(image_data)
    except UnidentifiedImageError:
        raise RuntimeError("Failed to download image: Unsupported or corrupted image file.")
    except Exception as e:
        raise RuntimeError(f"Failed to download image from URL: {e}")