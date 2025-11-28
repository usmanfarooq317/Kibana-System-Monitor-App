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
        
        self.test_elasticsearch_connection()
        
    def test_elasticsearch_connection(self):
        try:
            if self.es.ping():
                print("✅ Successfully connected to Elasticsearch")
            else:
                print("❌ Cannot connect to Elasticsearch")
        except Exception as e:
            print(f"❌ Error connecting to Elasticsearch: {e}")
            sys.exit(1)

    def setup_index(self):
        try:
            if not self.es.indices.exists(index=self.es_index):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "hostname": {"type": "keyword"},
                            "ip_address": {"type": "ip"},
                            
                            # CPU Metrics
                            "cpu_percent": {"type": "float"},
                            "cpu_cores": {"type": "integer"},
                            "cpu_user": {"type": "float"},
                            "cpu_system": {"type": "float"},
                            "cpu_idle": {"type": "float"},
                            "cpu_iowait": {"type": "float"},
                            
                            # Memory Metrics
                            "memory_total_gb": {"type": "float"},
                            "memory_used_gb": {"type": "float"},
                            "memory_free_gb": {"type": "float"},
                            "memory_percent": {"type": "float"},
                            "memory_available_gb": {"type": "float"},
                            "memory_cached_gb": {"type": "float"},
                            
                            # Load Average
                            "load_avg_1min": {"type": "float"},
                            "load_avg_5min": {"type": "float"},
                            "load_avg_15min": {"type": "float"},
                            "load_per_core": {"type": "float"},
                            
                            # Disk Metrics
                            "disk_total_gb": {"type": "float"},
                            "disk_used_gb": {"type": "float"},
                            "disk_free_gb": {"type": "float"},
                            "disk_percent": {"type": "float"},
                            
                            # Network Metrics
                            "network_bytes_sent_mb": {"type": "float"},
                            "network_bytes_recv_mb": {"type": "float"},
                            "network_packets_sent": {"type": "long"},
                            "network_packets_recv": {"type": "long"},
                            
                            # Process Metrics
                            "process_count": {"type": "integer"},
                            "process_running": {"type": "integer"},
                            "process_sleeping": {"type": "integer"},
                            
                            # System Info
                            "boot_time": {"type": "date"},
                            "uptime_hours": {"type": "float"}
                        }
                    }
                }
                self.es.indices.create(index=self.es_index, body=mapping)
                print(f"✅ Created index: {self.es_index}")
        except Exception as e:
            print(f"❌ Error creating index: {e}")

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"

    def bytes_to_gb(self, bytes_value):
        return round(bytes_value / (1024 ** 3), 2)

    def bytes_to_mb(self, bytes_value):
        return round(bytes_value / (1024 ** 2), 2)

    def collect_stats(self):
        try:
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_times = psutil.cpu_times_percent()
            cpu_cores = psutil.cpu_count()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Load Average
            load_avg = psutil.getloadavg()
            load_per_core = load_avg[0] / cpu_cores if cpu_cores > 0 else 0
            
            # Disk Information
            disk = psutil.disk_usage('/')
            
            # Network Information
            net_io = psutil.net_io_counters()
            
            # Process Information
            processes = []
            running = 0
            sleeping = 0
            for proc in psutil.process_iter(['status']):
                try:
                    status = proc.info['status']
                    if status == psutil.STATUS_RUNNING:
                        running += 1
                    elif status == psutil.STATUS_SLEEPING:
                        sleeping += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # System Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = round(uptime_seconds / 3600, 2)
            
            stats = {
                'timestamp': datetime.utcnow(),
                'hostname': self.hostname,
                'ip_address': self.get_ip_address(),
                
                # CPU Metrics
                'cpu_percent': cpu_percent,
                'cpu_cores': cpu_cores,
                'cpu_user': getattr(cpu_times, 'user', 0),
                'cpu_system': getattr(cpu_times, 'system', 0),
                'cpu_idle': getattr(cpu_times, 'idle', 0),
                'cpu_iowait': getattr(cpu_times, 'iowait', 0),
                
                # Memory Metrics (in GB)
                'memory_total_gb': self.bytes_to_gb(memory.total),
                'memory_used_gb': self.bytes_to_gb(memory.used),
                'memory_free_gb': self.bytes_to_gb(memory.free),
                'memory_percent': memory.percent,
                'memory_available_gb': self.bytes_to_gb(getattr(memory, 'available', memory.free)),
                
                # Load Average
                'load_avg_1min': load_avg[0],
                'load_avg_5min': load_avg[1],
                'load_avg_15min': load_avg[2],
                'load_per_core': load_per_core,
                
                # Disk Metrics (in GB)
                'disk_total_gb': self.bytes_to_gb(disk.total),
                'disk_used_gb': self.bytes_to_gb(disk.used),
                'disk_free_gb': self.bytes_to_gb(disk.free),
                'disk_percent': disk.percent,
                
                # Network Metrics
                'network_bytes_sent_mb': self.bytes_to_mb(net_io.bytes_sent),
                'network_bytes_recv_mb': self.bytes_to_mb(net_io.bytes_recv),
                'network_packets_sent': net_io.packets_sent,
                'network_packets_recv': net_io.packets_recv,
                
                # Process Metrics
                'process_count': len(psutil.pids()),
                'process_running': running,
                'process_sleeping': sleeping,
                
                # System Info
                'boot_time': boot_time,
                'uptime_hours': uptime_hours
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error collecting stats: {e}")
            return None

    def send_to_elasticsearch(self, stats):
        try:
            # Convert datetime objects to strings for JSON serialization
            es_stats = stats.copy()
            if 'boot_time' in es_stats and isinstance(es_stats['boot_time'], datetime):
                es_stats['boot_time'] = es_stats['boot_time'].isoformat()
            if 'timestamp' in es_stats and isinstance(es_stats['timestamp'], datetime):
                es_stats['timestamp'] = es_stats['timestamp'].isoformat()
                
            self.es.index(
                index=self.es_index,
                body=es_stats
            )
            print(f"✅ Stats sent - CPU: {stats['cpu_percent']}%, Memory: {stats['memory_percent']}%")
            return True
        except Exception as e:
            print(f"❌ Error sending to Elasticsearch: {e}")
            return False

    def run(self):
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