import psutil
import time
import socket
import json
from datetime import datetime
from elasticsearch import Elasticsearch
import os
import sys

class SystemStatsCollector:
    def __init__(self):
        self.es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
        self.es_port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        self.collection_interval = int(os.getenv('COLLECTION_INTERVAL', 30))
        self.es_index = 'system-stats'
        
        print(f"Connecting to Elasticsearch at {self.es_host}:{self.es_port}")
        self.es = Elasticsearch([f'http://{self.es_host}:{self.es_port}'])
        self.hostname = socket.gethostname()
        
        # Test Elasticsearch connection
        self.test_elasticsearch_connection()
        
    def test_elasticsearch_connection(self):
        """Test if we can connect to Elasticsearch"""
        try:
            if self.es.ping():
                print("✅ Successfully connected to Elasticsearch")
            else:
                print("❌ Cannot connect to Elasticsearch")
        except Exception as e:
            print(f"❌ Error connecting to Elasticsearch: {e}")
            sys.exit(1)

    def setup_index(self):
        """Create Elasticsearch index with proper mapping"""
        try:
            if not self.es.indices.exists(index=self.es_index):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "hostname": {"type": "keyword"},
                            "cpu_percent": {"type": "float"},
                            "memory_percent": {"type": "float"},
                            "load_avg_1min": {"type": "float"},
                            "load_avg_5min": {"type": "float"},
                            "load_avg_15min": {"type": "float"}
                        }
                    }
                }
                self.es.indices.create(index=self.es_index, body=mapping)
                print(f"✅ Created index: {self.es_index}")
        except Exception as e:
            print(f"❌ Error creating index: {e}")

    def get_ip_address(self):
        """Get primary IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"

    def collect_stats(self):
        """Collect all system statistics"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            
            # Get load average
            load_avg = psutil.getloadavg()
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            
            stats = {
                'timestamp': datetime.utcnow(),
                'hostname': self.hostname,
                'ip_address': self.get_ip_address(),
                'cpu_percent': cpu_percent,
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'load_avg_1min': load_avg[0],
                'load_avg_5min': load_avg[1],
                'load_avg_15min': load_avg[2],
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': disk.percent
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error collecting stats: {e}")
            return None

    def send_to_elasticsearch(self, stats):
        """Send statistics to Elasticsearch"""
        try:
            self.es.index(
                index=self.es_index,
                body=stats
            )
            print(f"✅ Stats sent to Elasticsearch - CPU: {stats['cpu_percent']}%, Memory: {stats['memory_percent']}%")
            return True
        except Exception as e:
            print(f"❌ Error sending to Elasticsearch: {e}")
            return False

    def run(self):
        """Main loop to collect and send statistics"""
        print("🚀 Starting system stats collector...")
        print(f"📊 Collection interval: {self.collection_interval} seconds")
        
        self.setup_index()
        
        while True:
            try:
                stats = self.collect_stats()
                if stats:
                    self.send_to_elasticsearch(stats)
                time.sleep(self.collection_interval)
            except KeyboardInterrupt:
                print("🛑 Stopping stats collector...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(self.collection_interval)

if __name__ == "__main__":
    collector = SystemStatsCollector()
    collector.run()