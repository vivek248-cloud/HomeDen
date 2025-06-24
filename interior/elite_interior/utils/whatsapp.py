# yourapp/utils/whatsapp.py
import requests

def send_whatsapp_message(to_number):
    access_token = 'EAAY21HlH90YBOxV5CDhjkrXyZAp8NEeW1ZCB8l3dsEJ9GO9VQRZCxvlJVUdrYvhcbzUir0W2SvCjL6B5iEo6pvl0D6QDiIFIEq6S8m7ZCOku2M5IZAbUELaERIQ4aPPfMd3edP5WZAiu0FpaHEQ6JuPweZChZAMHaJOFQIwqO10NbS0uiNFBM7a34jXqAJGQbl7ZBtkkeYE33ZCZAHhi3RlZB9dliaLz98HaaSQZD'  # Replace this string

    phone_number_id = '673301622532805'

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": { "code": "en_US" }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
