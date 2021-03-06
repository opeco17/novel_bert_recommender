from typing import Iterator, List, Tuple

import MySQLdb
from  MySQLdb.connections import Connection 
from MySQLdb.cursors import Cursor
import pandas as pd
from pandas.core.frame import DataFrame

from config import Config
from logger import logger


class DBConnector(object):
    """DBとの接続を担う"""
    
    @classmethod
    def get_conn_and_cursor(cls) -> Tuple[Connection, Cursor]:
        """DBのConnectorとCursorを提供"""
        try:
            conn = MySQLdb.connect(
                host = Config.DB_HOST_NAME,
                port = Config.DB_PORT,
                user = Config.DB_USER_NAME,
                password = Config.DB_PASSWORD,
                database = Config.DB_NAME,
                use_unicode=True,
                charset="utf8"
            )
            cursor = conn.cursor()
            logger.info('Get DB connector and cursor.')
            return conn, cursor
        
        except Exception as e:
            extra = {'Class': 'DBConnector', 'Method': 'get_conn_and_cursor', 'ErrorType': type(e), 'Error': str(e)}
            logger.error('Unable to get DB connector and cursor.')
            raise
        
    @classmethod
    def get_details_df_iterator(cls, conn: Connection, queue_data: int, completions: int, test: bool) -> Iterator[DataFrame]:
        """predicted_pointが1のミニバッチをイテレータで取得"""
        try:
            # test==Trueの際は全レコードを処理対象とする。
            if test:
                query = f"SELECT ncode, title, writer, keyword, story, genre, biggenre, text \
                            FROM details \
                            WHERE MOD(general_firstup, {completions})={queue_data}"
            else:      
                query = f"SELECT ncode, title, writer, keyword, story, genre, biggenre, text \
                            FROM details \
                            WHERE predicted_point=1 AND global_point=0 AND added_to_es=0 AND MOD(general_firstup, {completions})={queue_data}"
                            
            details_df_iterator = pd.read_sql_query(
                sql=query,
                con=conn, 
                chunksize=Config.FEATURE_EXTRACTION_BATCH_SIZE
            )
            logger.info('Get details df iterator.')
            return details_df_iterator
        
        except Exception as e:
            extra = {'Class': 'DBConnector', 'Method': 'get_details_df_iterator', 'ErrorType': type(e), 'Error': str(e)}
            logger.error('Unable to get details df iterator.')
            raise
        
    @classmethod
    def update_added_to_es(cls, conn: Connection, cursor: Cursor, ncodes: List[str]):
        """Elasticsearchへレコードがインサートされたか否かを示すadded_to_esカラムを更新する"""
        tupled_ncodes = [(ncode, ) for ncode in ncodes]
        try:
            cursor.executemany("UPDATE details SET added_to_es=True WHERE ncode=%s", tupled_ncodes)
            conn.commit()
            logger.info(f"{len(ncodes)} data were updated with added_to_es.")
        except Exception as e:
            extra = {'Class': 'DBConnector', 'Method': 'update_added_to_es', 'ErrorType': type(e), 'Error': str(e)}
            logger.error('Unable to update added_to_es column.')
            raise