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

    def insert(self, job_id, folder, status):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO jobs (job_id, folder, status) VALUES (%s, %s, %s)',
                (job_id, folder, status)
            )
        self.connection.commit()

    def update(self, job_id, status):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE jobs SET status = %s WHERE job_id = %s',
                (status, job_id)
            )
        self.connection.commit()

    def get(self, job_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM jobs WHERE job_id = %s',
                (job_id)
            )
            return cursor.fetchone()

    def close(self):
        self.connection.close()