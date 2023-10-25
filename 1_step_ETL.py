import pandas as pd
from db import PgDB
import pickle


class ETL:
    def __init__(self, filename, columns, table_name, chunksize=1000, ):            
        self.db = PgDB()
        self.columns = columns
        self.filename = filename
        self.chunksize = chunksize
        self.table_name = table_name

    def create_table(self):          
            self.db.exec(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
            (
                id int PRIMARY KEY,
                contract_number char(20),
                object_name text, 
                object_code char(6), 
                cost numeric, 
                contract_execution_days int
            )''')

    def get_days(self, row):
        try:
            date_start = pd.to_datetime(row['contract_execution_start_date'], format='%Y-%m-%d') 
            date_end = pd.to_datetime(row['contract_execution_end_date'], format='%Y-%m-%d') 
            return  (date_end  - date_start).days
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            return None


    def get_cost(self, row):
        try:
            return float(row['cost']) 
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            return None

    def set_count(self, count):
         with open("data.pickle", "wb") as file:
            pickle.dump(count, file)

    def get_count(self):
        try: 
            with open("data.pickle", "rb") as file:
                return pickle.load(file)
        except Exception as e:
            self.set_count(1)
            
    def reset_count(self):
        self.set_count(0)
        return 1

    def extract(self, count=0):
        with pd.read_csv(self.filename, chunksize=self.chunksize, on_bad_lines='skip', low_memory=False) as reader:
            print('Continue from ', count)
            for df in reader:
                df.columns = self.columns
                df = df[['id', 'contract_number', 'object_name', 'object_code', 'cost', 'contract_execution_start_date', 'contract_execution_end_date']]
                df['id'] = df['id'].astype(int)
                df['object_name'] = df['object_name'].astype(str)
                df['object_code'] = df['object_code'].astype(str)

                df['contract_execution_days'] = df.apply(lambda row: self.get_days(row), axis=1)
                df['cost'] = df.apply(lambda row: self.get_cost(row), axis=1)
                df = df[['id','contract_number','object_name', 'object_code', 'cost', 'contract_execution_days']]
                df = df.query('contract_execution_days.notnull() & cost.notnull()', engine='python')
                self.load(df)
                print('Chunk ', count, 'rows: ', count * self.chunksize)
                count +=1
                self.set_count(count)
                
                
    def run(self):
        count = self.reset_count()
        self.extract(count)

    def resume(self,  chunksize=1000):
        count = self.get_count()
        self.extract(count)


    def load(self, df):  
            """ 
            Загружает данные в базу данных
            """      
            data = [tuple(x) for x in df.to_numpy()] 
  
            columns = ','.join(list(df.columns)) 
            
            query = f"""INSERT INTO {self.table_name} ({columns}) VALUES %s
                        ON CONFLICT (id) DO NOTHING;"""

            self.db.insert_data(query, data, self.chunksize)

    def get_column_names(self):
        return self.db.get_column_names('contracts')         

    def select(self, query):
        return self.db.select(query)


columns =  ['id', 'contract_number', 'purchase_code', 'provider_inn', 'provider_name', 'provider_region_name', 
            'customer_inn','customer_name', 'customer_region_name', 
            'kbk_cod', 'mark_of_execution_conclusion', 'contract_subject', 'budget_name', 
            'contact_conclusion_date', 'contract_execution_start_date', 
            'contract_execution_end_date', 'contract_update_date', 'contract_update_date',
            'null_1', 'null_2', 'contract_price', 'cost', 'nds', 'contract_note_changing_terms',
            'null_3', 'object_name' , 'object_code']



etl = ETL('fz.csv', columns, 'contracts', 10**5)
etl.create_table()
#etl.get_column_names()
#etl.reset_count()

#
#etl.run()
#etl.resume()
df = etl.select('''select * from contracts''')
#print(df)
df.to_csv('datasets/dataset.csv', sep=';', index=False)