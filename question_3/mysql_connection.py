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

    def get_queued_job(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, job_parameters
                FROM jobs
                WHERE job_status = 'QUEUED'
                ORDER BY creation_time ASC
                LIMIT 1
            """)
            return cursor.fetchone()

    def count_running_jobs(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM jobs
                WHERE job_status = 'RUNNING'
            """)
            return cur.fetchone()[0]


    def update_job_status(self, job_id, status, task_arn=None):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE jobs
                SET job_status = %s, scanner_host = %s, creation_time = NOW()
                WHERE id = %s
            """, (status, task_arn, job_id))
            conn.commit()

    def get_idle_jobs(self, max_idle_time=5):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM jobs
                WHERE job_status = 'RUNNING'
                AND creation_time < NOW() - INTERVAL %s MINUTE
            """), (max_idle_time)
            return cursor.fetchall()

    def close(self):
        self.connection.close()