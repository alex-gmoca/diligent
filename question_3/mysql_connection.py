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

    def initiate_hosts_table(self, hosts):
        with self.connection.cursor() as cursor:
            #clears the table before inserting
            cursor.execute("DELETE from hosts")
            for host in hosts:
                cursor.execute("""
                    INSERT INTO hosts (hostname, port, available)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE port = %s, available = %s
                """, (host['hostname'], host['port'], True, host['port'], True))
            conn.commit()

    def check_host_availability(self):
        return self.connection.cursor().execute("""
            SELECT hostname
            FROM hosts
            WHERE available = 1
            LIMIT 1
        """).fetchone()

    def change_host_availability(self, host, available):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE hosts
                SET available = %s
                WHERE hostname = %s
            """, (available, host))
            conn.commit()

    def close(self):
        self.connection.close()