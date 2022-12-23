import psycopg2


class AccessControlSystem:
    def __init__(self, user='postgres', password='postgres', host='localhost', dbname='AccessControlSystem'):
        # 连接到数据库
        self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)

    def __del__(self):
        self.conn.close()

    def close(self):
        self.__del__()