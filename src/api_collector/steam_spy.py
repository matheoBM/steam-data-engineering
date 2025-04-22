import requests

def get_steam_spy_data(app_id):
    response = requests.get(f"https://steamspy.com/api.php?request=appdetails&appid={app_id}")

    return response.json()['ccu']