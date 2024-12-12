class MySQL:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=os.environ.get('db_host'),
                user=os.environ.get('db_user'),
                password=os.environ.get('db_password'),
                database=os.environ.get('db_name')
            )
        except Exception as e:
            raise Exception("Error while connecting to MySQL: " + str(e))

    def insert(self, script_id, script_location, status):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO scripts (script_id, script_location, status) VALUES (%s, %s, %s)',
                (script_id, script_location, status)
            )
        self.connection.commit()

    def update(self, script_id, output_location, status):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE scripts SET output_location = %s, status = %s WHERE script_id = %s',
                (output_location, status, script_id)
            )
        self.connection.commit()

    def get(self, script_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM scripts WHERE script_id = %s',
                (script_id)
            )
            return cursor.fetchone()

    def close(self):
        self.connection.close()