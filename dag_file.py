from airflow.decorators import dag, task
from datetime import datetime
from api_collector import steam_api, steam_spy
from api_collector.logger_config import logger
import time


@dag(dag_id = 'steam_data', schedule_interval='@daily', start_date=datetime(2025, 4, 8), catchup=False)
def steam_dag():
    
    @task 
    def get_app_list():
        return steam_api.get_steam_apps()
    
    @task(retries=3)
    def get_data_steamapi(steam_apps):
        for app in steam_apps:
            response = 200
            time_sleep = 5

            for i in range(5):
                try:
                    response = steam_api.get_app_data(app['appid'], app['name'])
                except Exception as e:
                    logger.info(f'Fail to get data for {app["appid"]}')
                
                if response == 200:
                    break
                elif response == 429:
                    logger.info(f'Too many API calls {app["appid"]}')
                    time.sleep(time_sleep * (i+1))
                
    @task 
    def get_steam_spy(steam_apps):
        for app in steam_apps:
            steam_spy.get_steam_spy_data(app['appid'], app['name'])
    
    app_list = get_app_list()
    get_data_steamapi(app_list)
    get_steam_spy(app_list)

dag = steam_dag()