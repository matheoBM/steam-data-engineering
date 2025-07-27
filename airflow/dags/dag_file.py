from airflow.decorators import dag, task
from datetime import datetime
from api_collector import steam_api, steam_spy
from api_collector.logger_config import logger
import time
import pandas as pd
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

@dag(dag_id = 'steam_data', schedule_interval='@daily', start_date=datetime(2025, 6, 29), catchup=False)
def steam_dag():
    
    @task 
    def get_app_list():
        return steam_api.get_steam_apps()
    
    @task
    def get_data_steamapi(steam_apps):
        app_data_list = []

        for idx, app in enumerate(steam_apps[:10]):
            response = 200
            time_sleep = 5

            for i in range(5):
                try:
                    response = steam_api.get_app_data(app['appid'], app['name'])
                except Exception as e:
                    logger.info(f'Fail to get data for {app["appid"]}')
                
                if type(response) == dict:
                    app_data_list.append(response)
                    break
                elif response == 429:
                    logger.info(f'Too many API calls {app["appid"]}')
                    time.sleep(time_sleep * (i+1))

            if idx % 100 == 0:
                logger.info(f'{idx} de {len(steam_apps)} processados')

        return app_data_list

                
    @task 
    def get_steam_spy(steam_apps):
        for app in steam_apps:
            steam_spy.get_steam_spy_data(app['appid'], app['name'])

    @task 
    def convert_list_to_pandas(app_data_list):
        df = pd.DataFrame(app_data_list)
        return df 

    @task 
    def preprocess_steam_data(df):
        logger.info('Preprocessing steam data')

        df['release_date'] = pd.to_datetime(df['release_date'], format='%d %b, %Y')

        logger.info('Preprocessing finished')
        return df

    @task
    def save_to_parquet(df:pd.DataFrame, path="/tmp/steam_data.parquet"):
        df.to_parquet(path, index=False)
        logger.info(f'Saving: \n {df.head()}')
        return path
    
    @task
    def save_to_tab(df:pd.DataFrame, path="/tmp/steam_data.parquet"):
        df.to_csv(path, sep='\t', index=False, header=False)
        logger.info(f'Saving: \n {df.head()}')
        return path
    
    @task
    def bulk_insert_tabfile_to_postgres(file_path):
        hook = PostgresHook(postgres_conn_id="Postgres")

        hook.bulk_load('steam_games', file_path)
    
    create_table = PostgresOperator(
        task_id="create_steam_games_table",
        postgres_conn_id="Postgres",  # matches your connection ID
        sql="""
        CREATE TABLE IF NOT EXISTS steam_games (
            appid TEXT,
            name TEXT,
            release_date DATE,
            price TEXT
        );
        """
    )
    app_list = get_app_list()
    steam_data = get_data_steamapi(app_list)
    #get_steam_spy(app_list)
    df = convert_list_to_pandas(steam_data)
    df = preprocess_steam_data(df)
    parquet_path = save_to_tab(df)
    bulk_insert_tabfile_to_postgres(parquet_path)

dag = steam_dag()