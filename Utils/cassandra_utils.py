from cassandra.cluster import Cluster
import os
from secret_utils import secrets

class CassandraUtils:
    def __init__(self, host, keyspace, username, password):
        self.host = host
        self.keyspace = keyspace
        self.username = username
        self.password = password
        self.cluster = None
        self.session = None

    def connect_to_database(self):
        if not self.cluster:
            self.cluster = Cluster([self.host], auth_provider={'username': self.username, 'password': self.password})
            self.session = self.cluster.connect(self.keyspace)
        return self.session

    def close_connection(self):
        if self.cluster:
            self.cluster.shutdown()
            self.cluster = None
            self.session = None

# Get secret values from AWS Secrets Manager
cassandra_username = secrets['cassandra_username']
cassandra_password = secrets['cassandra_password']

# Initialize CassandraUtils
cassandra_utils_instance = CassandraUtils(
    host=os.environ['CASSANDRA_HOST'],
    keyspace=os.environ['CASSANDRA_KEYSPACE'],
    username=cassandra_username,
    password=cassandra_password
)

# Connect to Cassandra database
session = 'xyz'
    # cassandra_utils_instance.connect_to_database())

# Perform Cassandra operations using the 'session' object

# Close the Cassandra connection when done
cassandra_utils_instance.close_connection()
