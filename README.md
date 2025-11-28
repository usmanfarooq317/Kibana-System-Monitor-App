# System Monitoring Dashboard

A comprehensive system monitoring solution that collects machine statistics and displays them in a Kibana dashboard with matrix-style tables for clear data visualization.

## 🚀 Features

- **Real-time System Monitoring**: Collects CPU, memory, disk, network, and process metrics
- **Matrix Display**: Shows exact numerical values in organized tables (not bar charts)
- **Multi-host Support**: Monitor multiple machines simultaneously
- **Dockerized**: Easy deployment with Docker Compose
- **Elasticsearch Backend**: Scalable data storage and retrieval
- **Kibana Dashboard**: Beautiful, customizable visualizations
- **Auto-refresh**: Real-time data updates

## 📊 Monitored Metrics

### System Overview
- Hostname and IP address
- System uptime
- CPU cores count
- Boot time

### CPU Metrics
- CPU usage percentage
- User CPU time
- System CPU time
- Idle CPU time
- I/O wait time

### Memory Metrics
- Total memory (GB)
- Used memory (GB)
- Free memory (GB)
- Memory usage percentage
- Available memory (GB)

### Load & Performance
- Load average (1, 5, 15 minutes)
- Load per core
- Process count
- Running processes
- Sleeping processes

### Disk & Storage
- Total disk space (GB)
- Used disk space (GB)
- Free disk space (GB)
- Disk usage percentage

### Network Activity
- Bytes sent (MB)
- Bytes received (MB)
- Packets sent
- Packets received

## 🛠️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Stats         │    │   Elasticsearch  │    │   Kibana        │
│   Collector     │───▶│   (Data Store)   │◀───│   (Dashboard)   │
│   (Python App)  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
monitoring-app/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Stats collector container setup
├── requirements.txt            # Python dependencies
├── config.py                   # Application configuration
├── stats_collector.py          # Main monitoring application
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose
- 4GB RAM minimum (8GB recommended)

### Installation & Deployment

1. **Clone or create the project directory:**
```bash
mkdir monitoring-app
cd monitoring-app
```

2. **Create all the required files** (copy the content from the provided files)

3. **Deploy the stack:**
```bash
docker-compose up -d
```

4. **Verify services are running:**
```bash
docker-compose ps
```

5. **Check application logs:**
```bash
docker-compose logs -f stats-collector
```

### Access the Dashboard

1. **Open Kibana in your browser:**
```
http://localhost:5601
```

2. **Create index pattern:**
   - Go to **Management** → **Stack Management** → **Index Patterns**
   - Create pattern: `system-stats*`
   - Time field: `timestamp`

3. **Create dashboard:**
   - Go to **Analytics** → **Dashboard**
   - Create new dashboard
   - Add **Data Table** visualizations for matrix display

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ELASTICSEARCH_HOST` | `elasticsearch` | Elasticsearch hostname |
| `ELASTICSEARCH_PORT` | `9200` | Elasticsearch port |
| `ELASTICSEARCH_INDEX` | `system-stats` | Index name for system stats |
| `COLLECTION_INTERVAL` | `30` | Stats collection interval in seconds |
| `HOSTNAME` | auto-detected | System hostname |
| `IP_ADDRESS` | auto-detected | System IP address |

### Customizing Collection Interval

```bash
# Collect stats every 10 seconds
COLLECTION_INTERVAL=10 docker-compose up -d stats-collector
```

### Monitoring Multiple Hosts

Deploy the stats collector on multiple machines by updating the `ELASTICSEARCH_HOST` to point to your central Elasticsearch instance.

## 📈 Kibana Dashboard Setup

### Recommended Table Visualizations

1. **System Overview Table**
   - Hostname, IP address, uptime, CPU cores

2. **Performance Metrics Table**
   - CPU %, Memory %, Load averages (1, 5, 15 min)

3. **Memory Details Table**
   - Memory usage in GB (used/total/free/available)

4. **Storage & Network Table**
   - Disk usage %, Network traffic (sent/received in MB)

### Creating Matrix Tables

1. **Go to Analytics → Dashboard → Create visualization**
2. **Choose "Data Table" visualization type**
3. **Configure metrics and buckets for tabular display**
4. **Set auto-refresh to 5-10 seconds for real-time updates**

## 🐛 Troubleshooting

### Common Issues

1. **Stats collector container exits:**
   ```bash
   docker logs stats-collector
   ```
   Check for Python dependency issues or Elasticsearch connection problems.

2. **No data in Kibana:**
   ```bash
   # Check if Elasticsearch has data
   curl http://localhost:9200/system-stats/_search?pretty
   ```

3. **High resource usage:**
   - Adjust `COLLECTION_INTERVAL` to reduce frequency
   - Modify Elasticsearch heap size in `docker-compose.yml`

### Service Health Checks

```bash
# Check Elasticsearch
curl http://localhost:9200/

# Check if data is being indexed
curl -X GET "http://localhost:9200/system-stats/_search?size=1&pretty"

# View container logs
docker-compose logs elasticsearch
docker-compose logs kibana
docker-compose logs stats-collector
```

## 🔄 Maintenance

### Stopping Services
```bash
docker-compose down
```

### Updating Services
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

### Data Persistence
Elasticsearch data is persisted in a Docker volume. To remove all data:
```bash
docker-compose down -v
```

### Backup and Restore
```bash
# Backup Elasticsearch data
docker run --rm -v elasticsearch_data:/source -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /source .

# Restore Elasticsearch data
docker run --rm -v elasticsearch_data:/target -v $(pwd):/backup alpine sh -c "rm -rf /target/* && tar xzf /backup/backup.tar.gz -C /target"
```

## 📊 Sample Output

The dashboard displays data in clear matrix format:

| Hostname | CPU % | Memory % | Load 1min | Memory Used/Total | Disk % |
|----------|-------|----------|-----------|-------------------|--------|
| server-01 | 12.5% | 45.2% | 1.25 | 3.2 GB / 8.0 GB | 67.8% |
| server-02 | 8.2% | 32.1% | 0.89 | 2.1 GB / 8.0 GB | 45.3% |

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## 🙏 Acknowledgments

- Built with Python, Elasticsearch, and Kibana
- Uses psutil for system metrics collection
- Containerized with Docker for easy deployment

---
