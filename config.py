import os

# Elasticsearch configuration
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))
ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX', 'system-stats')

# Collection interval in seconds
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', 30))

# System information
HOSTNAME = os.getenv('HOSTNAME', 'unknown-host')
IP_ADDRESS = os.getenv('IP_ADDRESS', 'unknown-ip')