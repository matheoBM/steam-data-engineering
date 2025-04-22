import requests
from api_collector.logger_config import logger 

def get_steam_apps():
    ''' 
        Return list of dict with appid and name of games
    '''
    # Pega lista de jogos
    response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json')
    
    # Limpa
    new_apps_list = []
    for app in response.json()['applist']['apps']:
        if app['name'] != '':
            new_apps_list.append(app)
    
    return new_apps_list

def get_app_data(app_id, app_name):
    response = requests.get(f'http://store.steampowered.com/api/appdetails?appids={app_id}')
    
    if response.status_code == 429:
        return response.status_code 
    
    try:
        response_json = response.json()
    except ValueError:
        logger.warning(f'Invalid JSON for app {app_id} ({app_name}). Response text: {response.text[:200]}')
        return 500  # Or a custom code indicating bad JSON
    
    response_json = response.json()
    response_json = response_json[str(app_id)]

    if not response_json['success']:
        return  response.status_code

    response_json = response_json['data'] # Está tudo dentro de data

    app_type = response_json['type']

    if app_type != 'game':
        return response.status_code
    
    try:
        release_date = response_json['release_date']['date']
        price = response_json['price_overview']['initial']
        logger.info("STEAM API: ", app_name, ' ', release_date, ' ', price)
    except KeyError as ke:
        logger.info(f"{app_name} sem dados validos")
        return response.status_code

def get_apps_data(new_apps_list):
    for app in new_apps_list:
        app_id = app['appid']
        response = requests.get(f'http://store.steampowered.com/api/appdetails?appids={app_id}')

        response_json = response.json()
        response_json = response_json['app_id']['data'] # Está tudo dentro de data

        app_type = response_json['type']
        release_date = response_json['release_date']['date']
        price = response_json['price_overview']['initial']

        if app_type == 'game':
            logger.info(f'STEAM SPY: {app_type}, {release_date}, {price}') 