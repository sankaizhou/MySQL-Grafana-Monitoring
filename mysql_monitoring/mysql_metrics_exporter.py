from prometheus_client import start_http_server, Gauge, Counter
import mysql.connector
import time
import psutil  # For system metrics
from threading import Thread
import logging
import os
import signal
import sys

# Configure logging
logging.basicConfig(
    filename='mysql_exporter.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Define Prometheus metrics with 'instance' label
mysql_up = Gauge('mysql_up', 'MySQL server availability', ['instance'])  # Indicates if the MySQL server is up (1) or down (0).
mysql_connections = Gauge('mysql_connections', 'Number of active connections', ['instance'])  # Current number of active connections to the MySQL server.
mysql_max_connections = Gauge('mysql_max_connections', 'Maximum allowed connections', ['instance'])  # Maximum number of connections allowed by the MySQL server.
mysql_queries_total = Counter('mysql_queries_total', 'Total number of queries executed', ['instance'])  # Total count of all queries executed on the server.
mysql_slow_queries = Counter('mysql_slow_queries', 'Number of slow queries', ['instance'])  # Total count of queries that exceed the defined slow query threshold.
mysql_questions = Counter('mysql_questions', 'Number of statements executed', ['instance'])  # Total number of statements executed (including SELECT, INSERT, etc.).
mysql_commands = Counter('mysql_commands', 'Number of SQL commands executed', ['instance', 'command'])  # Count of executed SQL commands, categorized by command type.
mysql_replication_lag_seconds = Gauge('mysql_replication_lag_seconds', 'Replication lag in seconds', ['instance'])  # Time lag in seconds for replication on slave servers.
mysql_slave_io_running = Gauge('mysql_slave_io_running', 'Slave I/O thread status', ['instance'])  # Status of the slave I/O thread (1 if running, 0 if not).
mysql_slave_sql_running = Gauge('mysql_slave_sql_running', 'Slave SQL thread status', ['instance'])  # Status of the slave SQL thread (1 if running, 0 if not).
mysql_slave_retried_transactions = Counter('mysql_slave_retried_transactions', 'Number of retried transactions on slave', ['instance'])  # Count of transactions that were retried on the slave server.
mysql_innodb_buffer_pool_size = Gauge('mysql_innodb_buffer_pool_size', 'InnoDB buffer pool size', ['instance'])  # Size of the InnoDB buffer pool in bytes.
mysql_innodb_buffer_pool_used = Gauge('mysql_innodb_buffer_pool_used', 'InnoDB buffer pool used', ['instance'])  # Amount of the InnoDB buffer pool currently in use.
mysql_innodb_buffer_pool_pages_data = Gauge('mysql_innodb_buffer_pool_pages_data', 'InnoDB buffer pool pages containing data', ['instance'])  # Number of pages in the buffer pool that contain data.
mysql_innodb_buffer_pool_pages_free = Gauge('mysql_innodb_buffer_pool_pages_free', 'InnoDB buffer pool free pages', ['instance'])  # Number of free pages in the InnoDB buffer pool.
mysql_innodb_row_lock_time_avg = Gauge('mysql_innodb_row_lock_time_avg', 'Average InnoDB row lock time', ['instance'])  # Average time spent waiting for row locks in InnoDB.
mysql_innodb_row_lock_time_max = Gauge('mysql_innodb_row_lock_time_max', 'Maximum InnoDB row lock time', ['instance'])  # Maximum time spent waiting for a row lock in InnoDB.
mysql_innodb_row_lock_time_total = Gauge('mysql_innodb_row_lock_time_total', 'Total InnoDB row lock time', ['instance'])  # Total time spent waiting for row locks in InnoDB.
mysql_innodb_transactions = Gauge('mysql_innodb_transactions', 'Number of active InnoDB transactions', ['instance'])  # Current number of active transactions in InnoDB.
mysql_innodb_read_io_requests = Gauge('mysql_innodb_read_io_requests', 'Number of InnoDB read I/O requests', ['instance'])  # Total count of read I/O requests in InnoDB.
mysql_innodb_write_io_requests = Gauge('mysql_innodb_write_io_requests', 'Number of InnoDB write I/O requests', ['instance'])  # Total count of write I/O requests in InnoDB.
mysql_innodb_data_reads = Gauge('mysql_innodb_data_reads', 'Number of InnoDB data reads', ['instance'])  # Total count of data reads from InnoDB.
mysql_innodb_data_writes = Gauge('mysql_innodb_data_writes', 'Number of InnoDB data writes', ['instance'])  # Total count of data writes to InnoDB.
mysql_query_cache_size = Gauge('mysql_query_cache_size', 'Size of the query cache', ['instance'])  # Total size of the query cache in bytes.
mysql_query_cache_hits = Counter('mysql_query_cache_hits', 'Number of query cache hits', ['instance'])  # Total count of times queries were served from the cache.
mysql_query_cache_misses = Counter('mysql_query_cache_misses', 'Number of query cache misses', ['instance'])  # Total count of times queries were not found in the cache.
mysql_query_cache_free_memory = Gauge('mysql_query_cache_free_memory', 'Free memory in query cache', ['instance'])  # Amount of free memory available in the query cache.
mysql_memory_used = Gauge('mysql_memory_used', 'Memory used by MySQL', ['instance'])  # Total memory currently used by the MySQL server.
mysql_memory_free = Gauge('mysql_memory_free', 'Memory free in MySQL', ['instance'])  # Total free memory available to the MySQL server.
mysql_max_memory_usage = Gauge('mysql_max_memory_usage', 'Maximum memory usage by MySQL', ['instance'])  # Peak memory usage recorded by the MySQL server.
mysql_disk_usage_percent = Gauge('mysql_disk_usage_percent', 'Disk usage percentage of MySQL data directory', ['instance'])  # Percentage of disk space used in the MySQL data directory.
mysql_disk_read_io_requests = Counter('mysql_disk_read_io_requests', 'Number of disk read I/O requests', ['instance'])  # Total count of disk read I/O requests made by MySQL.
mysql_disk_write_io_requests = Counter('mysql_disk_write_io_requests', 'Number of disk write I/O requests', ['instance'])  # Total count of disk write I/O requests made by MySQL.
mysql_disk_read_bytes = Counter('mysql_disk_read_bytes', 'Bytes read from disk by MySQL', ['instance'])  # Total number of bytes read from disk by MySQL.
mysql_disk_write_bytes = Counter('mysql_disk_write_bytes', 'Bytes written to disk by MySQL', ['instance'])  # Total number of bytes written to disk by MySQL.
mysql_threads_running = Gauge('mysql_threads_running', 'Number of running MySQL threads', ['instance'])  # Current number of threads actively running in MySQL.
mysql_threads_created = Counter('mysql_threads_created', 'Number of MySQL threads created', ['instance'])  # Total count of threads created by MySQL since startup.
mysql_threads_cached = Gauge('mysql_threads_cached', 'Number of cached MySQL threads', ['instance'])  # Current number of threads that are cached and can be reused.
mysql_errors_total = Counter('mysql_errors_total', 'Total number of MySQL errors', ['instance'])  # Total count of errors encountered by the MySQL server.
mysql_aborted_clients = Counter('mysql_aborted_clients', 'Number of aborted MySQL client connections', ['instance'])  # Total count of client connections that were aborted.
mysql_aborted_connects = Counter('mysql_aborted_connects', 'Number of aborted MySQL connection attempts', ['instance'])  # Total count of connection attempts that were aborted.
mysql_uptime_seconds = Gauge('mysql_uptime_seconds', 'Uptime of MySQL server in seconds', ['instance'])  # Total uptime of the MySQL server in seconds.
mysql_tmp_tables = Counter('mysql_tmp_tables', 'Number of temporary tables created in memory', ['instance'])  # Total count of temporary tables created in memory.
mysql_tmp_disk_tables = Counter('mysql_tmp_disk_tables', 'Number of temporary tables created on disk', ['instance'])  # Total count of temporary tables created on disk.
mysql_tmp_table_size = Gauge('mysql_tmp_table_size', 'Maximum size of internal in-memory temporary tables', ['instance'])  # Maximum size allowed for internal in-memory temporary tables.
mysql_handler_read_rnd_next = Counter('mysql_handler_read_rnd_next', 'Number of requests to read the next row in data files', ['instance'])  # Total count of requests to read the next row in data files.
mysql_perf_schema_events_waits = Counter('mysql_perf_schema_events_waits', 'Number of wait events in Performance Schema', ['instance'])  # Total count of wait events recorded in the Performance Schema.
mysql_perf_schema_events_statements = Counter('mysql_perf_schema_events_statements', 'Number of statements in Performance Schema', ['instance'])  # Total count of statements recorded in the Performance Schema.
mysql_cpu_usage = Gauge('mysql_cpu_usage', 'CPU usage percentage of MySQL process', ['instance'])  # Current CPU usage percentage of the MySQL server process. # Add this line

# Configuration for multiple MySQL servers
MYSQL_SERVERS = [
    {
        'instance': 'master',
        'host': '127.0.0.1',  # Same IP address
        'port': 3306,          # Master port
        'user': 'root',
        'password': '',  # Replace with your MySQL exporter's password
        'database': 'replicated_db',    # Ensure this database exists
        'data_dir': 'C:/mysql/master/bin/data'  # Replace with Master data directory
    },
    {
        'instance': 'slave1',
        'host': '127.0.0.1',
        'port': 3307,          # Slave1 port
        'user': 'root',
        'password': '',
        'database': 'replicated_db',
        'data_dir': 'C:/mysql/slave1/bin/data'  # Replace with Slave1 data directory
    },
    {
        'instance': 'slave2',
        'host': '127.0.0.1',
        'port': 3308,          # Slave2 port
        'user': 'root',
        'password': '',
        'database': 'replicated_db',
        'data_dir': 'C:/mysql/slave2/bin/data'  # Replace with Slave2 data directory
    }
    # Add more servers if needed
]

def collect_mysql_metrics(server):
    """
    Collects MySQL metrics for a given server and updates Prometheus gauges/counters.
    """
    instance = server['instance']
    host = server['host']
    port = server['port']
    user = server['user']
    password = server['password']
    database = server['database']
    data_dir = server['data_dir']

    while True:
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            cursor = connection.cursor(dictionary=True)

            # Set mysql_up to 1 (up)
            mysql_up.labels(instance=instance).set(1)

            # Get number of active connections
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Threads_connected';")
            result = cursor.fetchone()
            connections = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_connections.labels(instance=instance).set(connections)

            # Get maximum connections
            cursor.execute("SHOW VARIABLES LIKE 'max_connections';")
            result = cursor.fetchone()
            max_connections = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_max_connections.labels(instance=instance).set(max_connections)

            # Get total number of queries
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Queries';")
            result = cursor.fetchone()
            queries = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_queries_total.labels(instance=instance).inc(queries - mysql_queries_total.labels(instance=instance)._value.get())

            # Get slow queries
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Slow_queries';")
            result = cursor.fetchone()
            slow_queries = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_slow_queries.labels(instance=instance).inc(slow_queries - mysql_slow_queries.labels(instance=instance)._value.get())

            # Get number of statements executed
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Questions';")
            result = cursor.fetchone()
            questions = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_questions.labels(instance=instance).inc(questions - mysql_questions.labels(instance=instance)._value.get())

            # Get number of SQL commands executed
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_%';")
            results = cursor.fetchall()
            for row in results:
                command = row['Variable_name']
                value = int(row['Value']) if row['Value'].isdigit() else 0
                mysql_commands.labels(instance=instance, command=command).inc(value - mysql_commands.labels(instance=instance, command=command)._value.get())

            # Get replication lag (for slaves)
            cursor.execute("SHOW SLAVE STATUS;")
            slave_status = cursor.fetchone()
            if slave_status:
                replication_lag = slave_status.get('Seconds_Behind_Master', 0)
                mysql_replication_lag_seconds.labels(instance=instance).set(float(replication_lag) if replication_lag else 0)

                # Get slave thread statuses
                io_running = 1 if slave_status.get('Slave_IO_Running', '').lower() == 'yes' else 0
                sql_running = 1 if slave_status.get('Slave_SQL_Running', '').lower() == 'yes' else 0
                mysql_slave_io_running.labels(instance=instance).set(io_running)
                mysql_slave_sql_running.labels(instance=instance).set(sql_running)

                # Get retried transactions
                retried_transactions = int(slave_status.get('Retrieved_Rows', 0))
                mysql_slave_retried_transactions.labels(instance=instance).inc(retried_transactions - mysql_slave_retried_transactions.labels(instance=instance)._value.get())
            else:
                # If not a slave, set replication lag and slave threads to 0
                mysql_replication_lag_seconds.labels(instance=instance).set(0)
                mysql_slave_io_running.labels(instance=instance).set(0)
                mysql_slave_sql_running.labels(instance=instance).set(0)
                mysql_slave_retried_transactions.labels(instance=instance).inc(0)

            # Get InnoDB Buffer Pool Size
            cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size';")
            result = cursor.fetchone()
            buffer_pool_size = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_buffer_pool_size.labels(instance=instance).set(buffer_pool_size)

            # Get InnoDB Buffer Pool Used
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_data';")
            result = cursor.fetchone()
            buffer_pool_used_pages = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_buffer_pool_used.labels(instance=instance).set(buffer_pool_used_pages)

            # Get InnoDB Buffer Pool Pages Free
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_free';")
            result = cursor.fetchone()
            buffer_pool_free_pages = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_buffer_pool_pages_free.labels(instance=instance).set(buffer_pool_free_pages)

            # Get InnoDB Row Lock Times
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time_avg';")
            result = cursor.fetchone()
            row_lock_time_avg = float(result['Value']) if result and result['Value'] else 0.0
            mysql_innodb_row_lock_time_avg.labels(instance=instance).set(row_lock_time_avg)

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time_max';")
            result = cursor.fetchone()
            row_lock_time_max = float(result['Value']) if result and result['Value'] else 0.0
            mysql_innodb_row_lock_time_max.labels(instance=instance).set(row_lock_time_max)

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time_total';")
            result = cursor.fetchone()
            row_lock_time_total = float(result['Value']) if result and result['Value'] else 0.0
            mysql_innodb_row_lock_time_total.labels(instance=instance).set(row_lock_time_total)

            # Get InnoDB Transactions
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_transactions';")
            result = cursor.fetchone()
            innodb_transactions = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_transactions.labels(instance=instance).set(innodb_transactions)

            # Get InnoDB Read/Write I/O Requests
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_data_reads';")
            result = cursor.fetchone()
            innodb_data_reads = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_data_reads.labels(instance=instance).set(innodb_data_reads)

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_data_writes';")
            result = cursor.fetchone()
            innodb_data_writes = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_innodb_data_writes.labels(instance=instance).set(innodb_data_writes)

            # Get Query Cache Metrics
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Qcache_size';")
            result = cursor.fetchone()
            query_cache_size = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_query_cache_size.labels(instance=instance).set(query_cache_size)

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Qcache_hits';")
            result = cursor.fetchone()
            query_cache_hits = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_query_cache_hits.labels(instance=instance).inc(query_cache_hits)

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Qcache_inserts';")
            result = cursor.fetchone()
            query_cache_inserts = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_query_cache_misses.labels(instance=instance).inc(query_cache_inserts)  # Adjust accordingly

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Qcache_free_memory';")
            result = cursor.fetchone()
            query_cache_free_memory = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_query_cache_free_memory.labels(instance=instance).set(query_cache_free_memory)

            # Get Memory Metrics
            cursor.execute("SHOW STATUS LIKE 'Max_used_connections';")
            result = cursor.fetchone()
            max_used_connections = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_max_memory_usage.labels(instance=instance).set(max_used_connections)

            # Get Disk Usage Metrics
            if os.path.exists(data_dir):
                disk_usage = psutil.disk_usage(data_dir)
                mysql_disk_usage_percent.labels(instance=instance).set(disk_usage.percent)

                # Get Disk I/O Metrics (Read/Write Requests)
                # Note: This requires system-level monitoring; alternatively, use MySQL's status variables if available
                # For simplicity, we'll skip detailed disk I/O metrics here
            else:
                mysql_disk_usage_percent.labels(instance=instance).set(0)
                logging.error(f"Data directory does not exist for {instance}: {data_dir}")

            # Get Uptime
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Uptime';")
            result = cursor.fetchone()
            uptime_seconds = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_uptime_seconds.labels(instance=instance).set(uptime_seconds)

            # Get Temporary Tables Metrics
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Created_tmp_tables';")
            result = cursor.fetchone()
            created_tmp_tables = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_tmp_tables.labels(instance=instance).inc(created_tmp_tables - mysql_tmp_tables.labels(instance=instance)._value.get())

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Created_tmp_disk_tables';")
            result = cursor.fetchone()
            created_tmp_disk_tables = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_tmp_disk_tables.labels(instance=instance).inc(created_tmp_disk_tables - mysql_tmp_disk_tables.labels(instance=instance)._value.get())

            cursor.execute("SHOW VARIABLES LIKE 'tmp_table_size';")
            result = cursor.fetchone()
            tmp_table_size = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_tmp_table_size.labels(instance=instance).set(tmp_table_size)

            # Get Handler Metrics
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Handler_read_rnd_next';")
            result = cursor.fetchone()
            handler_read_rnd_next = int(result['Value']) if result and result['Value'].isdigit() else 0
            mysql_handler_read_rnd_next.labels(instance=instance).inc(handler_read_rnd_next)

            # Get Performance Schema Metrics
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Performance_schema_%';")
            results = cursor.fetchall()
            for row in results:
                variable = row['Variable_name']
                value = int(row['Value']) if row['Value'].isdigit() else 0
                if variable == 'Performance_schema_events_waits_current':
                    mysql_perf_schema_events_waits.labels(instance=instance).inc(value)
                elif variable == 'Performance_schema_events_statements_current':
                    mysql_perf_schema_events_statements.labels(instance=instance).inc(value)

            cursor.close()
            connection.close()
        except Exception as e:
            mysql_up.labels(instance=instance).set(0)
            mysql_connections.labels(instance=instance).set(0)
            mysql_max_connections.labels(instance=instance).set(0)
            mysql_queries_total.labels(instance=instance).inc(0)
            mysql_slow_queries.labels(instance=instance).inc(0)
            mysql_questions.labels(instance=instance).inc(0)
            mysql_commands.labels(instance=instance, command='all').inc(0)
            mysql_replication_lag_seconds.labels(instance=instance).set(0)
            mysql_slave_io_running.labels(instance=instance).set(0)
            mysql_slave_sql_running.labels(instance=instance).set(0)
            mysql_slave_retried_transactions.labels(instance=instance).inc(0)
            mysql_innodb_buffer_pool_size.labels(instance=instance).set(0)
            mysql_innodb_buffer_pool_used.labels(instance=instance).set(0)
            mysql_innodb_buffer_pool_pages_data.labels(instance=instance).set(0)
            mysql_innodb_buffer_pool_pages_free.labels(instance=instance).set(0)
            mysql_innodb_row_lock_time_avg.labels(instance=instance).set(0)
            mysql_innodb_row_lock_time_max.labels(instance=instance).set(0)
            mysql_innodb_row_lock_time_total.labels(instance=instance).set(0)
            mysql_innodb_transactions.labels(instance=instance).set(0)
            mysql_innodb_data_reads.labels(instance=instance).set(0)
            mysql_innodb_data_writes.labels(instance=instance).set(0)
            mysql_query_cache_size.labels(instance=instance).set(0)
            mysql_query_cache_hits.labels(instance=instance).inc(0)
            mysql_query_cache_misses.labels(instance=instance).inc(0)
            mysql_query_cache_free_memory.labels(instance=instance).set(0)
            mysql_memory_used.labels(instance=instance).set(0)
            mysql_memory_free.labels(instance=instance).set(0)
            mysql_max_memory_usage.labels(instance=instance).set(0)
            mysql_disk_usage_percent.labels(instance=instance).set(0)
            mysql_uptime_seconds.labels(instance=instance).set(0)
            mysql_tmp_tables.labels(instance=instance).inc(0)
            mysql_tmp_disk_tables.labels(instance=instance).inc(0)
            mysql_tmp_table_size.labels(instance=instance).set(0)
            mysql_handler_read_rnd_next.labels(instance=instance).inc(0)
            mysql_perf_schema_events_waits.labels(instance=instance).inc(0)
            mysql_perf_schema_events_statements.labels(instance=instance).inc(0)
            logging.error(f"Error collecting MySQL metrics for {instance}: {e}")
        time.sleep(1)

def collect_system_metrics(server):
    """
    Collects system metrics (CPU and Disk usage) for a given server and updates Prometheus gauges/counters.
    """
    instance = server['instance']
    data_dir = server['data_dir']

    while True:
        try:
            # Validate data directory
            if not os.path.exists(data_dir):
                logging.error(f"MYSQL_DATA_DIR does not exist for {instance}: {data_dir}")
                mysql_disk_usage_percent.labels(instance=instance).set(0)
            else:
                # Get Disk usage percentage for MySQL data directory
                disk_usage = psutil.disk_usage(data_dir)
                mysql_disk_usage_percent.labels(instance=instance).set(disk_usage.percent)

            # Get CPU usage percentage of MySQL process
            # Find MySQL process
            mysql_processes = [proc for proc in psutil.process_iter(['name']) if 'mysqld' in proc.info['name'].lower()]
            total_cpu = 0
            for proc in mysql_processes:
                try:
                    cpu = proc.cpu_percent(interval=0.1)
                    total_cpu += cpu
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            mysql_cpu_usage.labels(instance=instance).set(total_cpu)

            # Optionally, collect memory metrics
            # This requires accessing OS-level memory stats; alternatively, use MySQL's variables
            # For simplicity, we skip detailed memory metrics here
        except Exception as e:
            mysql_cpu_usage.labels(instance=instance).set(0)
            mysql_disk_usage_percent.labels(instance=instance).set(0)
            logging.error(f"Error collecting system metrics for {instance}: {e}")

        time.sleep(5)  # Adjust the frequency as needed

def signal_handler(sig, frame):
    logging.info("Shutting down exporter...")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    logging.info("Prometheus metrics server started on port 8000")
    print("Prometheus metrics server started on port 8000")

    # Start metric collection threads for each server
    threads = []
    for server in MYSQL_SERVERS:
        # Start MySQL metrics collection thread
        t_mysql = Thread(target=collect_mysql_metrics, args=(server,))
        t_mysql.start()
        threads.append(t_mysql)

        # Start system metrics collection thread
        t_system = Thread(target=collect_system_metrics, args=(server,))
        t_system.start()
        threads.append(t_system)

    # Keep the main thread alive
    for t in threads:
        t.join()