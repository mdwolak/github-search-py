import psycopg2
from dotenv import dotenv_values

config = dotenv_values('.env')


class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(config.get('DATABASE_URL'))

    def execute_query(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            self.connection.commit()
            cursor.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            if self.connection is not None:
                self.connection.rollback()  # rollback the transaction on error
            raise  # Rethrow the error
        finally:
            if self.connection is not None:
                self.connection.close()

    def data_load_start(self, query_name, args=None):
        return self.execute_query(
            "SELECT staging.data_load_start(%s, %s)", (query_name, args))[0]

    def data_load_finish(self, data_load_id: int, total_count: int, error: str = None):
        return self.execute_query(
            "SELECT staging.data_load_finish(%s, %s, %s)", (data_load_id, total_count, error))[0]

    def data_page_insert(self, data_load_id, page_index, last_cursor, data):
        return self.execute_query("SELECT staging.data_page_insert(%s, %s, %s, %s)",
                                  (data_load_id, page_index, last_cursor, data))[0]
