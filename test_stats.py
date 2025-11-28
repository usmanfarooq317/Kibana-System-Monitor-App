import psutil
import time
import socket
from datetime import datetime
import json

def get_system_stats():
    """Get basic system stats for testing"""
    try:
        # Get CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory
        memory = psutil.virtual_memory()
        
        # Get load average
        load_avg = psutil.getloadavg()
        
        # Get host info
        hostname = socket.gethostname()
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'hostname': hostname,
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_used': memory.used,
            'memory_percent': memory.percent,
            'load_avg_1min': load_avg[0],
            'load_avg_5min': load_avg[1],
            'load_avg_15min': load_avg[2]
        }
        
        print("Stats collected successfully:")
        print(json.dumps(stats, indent=2))
        return True
        
    except Exception as e:
        print(f"Error collecting stats: {e}")
        return False

if __name__ == "__main__":
    print("Testing system stats collection...")
    success = get_system_stats()
    if success:
        print("Test passed! Stats collection is working.")
        # Keep running to test continuous collection
        while True:
            get_system_stats()
            time.sleep(5)
    else:
        print("Test failed! Check the error above.")