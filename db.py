import psycopg2
import psycopg2.extras as psql_extras
from configparser import ConfigParser
from typing import Dict, List
import numpy as np
import pandas as pd

class PgDB(object):

    def __init__(self, ini_filename = 'db.ini'):
        conn_info = self.load_connection_info(ini_filename)
        self.conn_info = conn_info
        # Подключаемся к PostgreSQL с пользователем, загруженным из файла .ini
        psql_connection_string = f"host={conn_info['host']} port={conn_info['port']} " \
                                 f"user={conn_info['user']} " \
                                 f"password={conn_info['password']} dbname={conn_info['database']}"
        self.conn = psycopg2.connect(psql_connection_string)
        
        
    def load_connection_info(self, ini_filename: str) -> Dict[str, str]:
        parser = ConfigParser()
        parser.read(ini_filename)
        # Создадим словарь переменных, хранящихся в разделе "postgresql" файла .ini
        conn_info = {param[0]: param[1] for param in parser.items("postgresql")}
        return conn_info


    def exec(self, sql: str) -> None:         
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            print(f"Query: {cur.query}")
            self.conn.rollback()
        else:
            self.conn.commit()  
            cur.close()  

    def insert_data(self, query: str, data, page_size: int) -> None:
        cur = self.conn.cursor()
        try:
            psql_extras.execute_values(cur, query, data, page_size=page_size)
            #print("Query:", cur.query)
        except Exception as error:
            print(f"{type(error).__name__}: {error}")
            #print("Query:", cur.query)
            self.conn.rollback()            
        else:
            self.conn.commit()            
            cur.close()
    
    def get_column_names(self, table: str) -> List[str]:
        cur = self.conn.cursor()
        cur.execute(
            f"SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
        col_names = [result[0] for result in cur.fetchall()]
        return col_names


    def select(self, sql, dtypes=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql)
            data = cur.fetchall()
            columns = data[0].keys()
            df =  pd.DataFrame(np.array(data), columns=columns, dtype=dtypes)
        except Exception as error:
            print(f"{type(error).__name__}: {error}")
            print("Query:", cur.query)
            self.conn.rollback()            
            df =  pd.DataFrame()
        else:
            cur.close()
            return df
        
    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()