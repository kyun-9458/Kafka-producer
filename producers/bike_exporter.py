# bike_exporter.py
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Gauge, Counter
import json
import time

# Kafka 설정
KAFKA_BROKER = 'kafka01:9092,kafka02:9092,kafka03:9092'
TOPIC_NAME = 'seoul-bicycle-status'

# Prometheus 메트릭 정의
bike_count_metric = Gauge(
    'bike_available_count',
    '주차된 자전거 수',
    ['station_id', 'station_name']
)

rack_total_metric = Gauge(
    'rack_total_count',
    '대여소 총 거치대 수',
    ['station_id', 'station_name']
)

rack_util_metric = Gauge(
    'rack_utilization_ratio',
    '거치대 대비 자전거 비율 (%)',
    ['station_id', 'station_name']
)

latitude_metric = Gauge(
    'station_latitude',
    '대여소 위도 정보',
    ['station_id', 'station_name']
)

longitude_metric = Gauge(
    'station_longitude',
    '대여소 경도 정보',
    ['station_id', 'station_name']
)

bike_rent_counter = Counter(
    'bike_rent_count_total',
    '누적 자전거 대여 횟수 (자전거 수 감소 추정)',
    ['station_id', 'station_name']
)

previous_bike_counts = {}

def start_exporter():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='bike-exporter-group-test2'
    )

    print("Exporter is running on http://kafka03:9310/metrics")
    start_http_server(9310)

    for message in consumer:
        try:
            data = message.value

            station_id = str(data.get("STT_ID"))
            station_name = str(data.get("STT_NM"))

            bike_count = int(data.get("TOT_PRK_CNT", 0))
            rack_total = int(data.get("TOT_RACK_CNT", 0))
            utilization = float(data.get("RATIO_PRK_RACK", 0))
            latitude = float(data.get("STT_LTTD", 0))
            longitude = float(data.get("STT_LGTD", 0))

            # Update gauges
            bike_count_metric.labels(station_id, station_name).set(bike_count)
            rack_total_metric.labels(station_id, station_name).set(rack_total)
            rack_util_metric.labels(station_id, station_name).set(utilization)
            latitude_metric.labels(station_id, station_name).set(latitude)
            longitude_metric.labels(station_id, station_name).set(longitude)

            # Rental counter logic
            key = (station_id, station_name)
            prev_count = previous_bike_counts.get(key)

            if prev_count is not None and bike_count < prev_count:
                diff = prev_count - bike_count
                bike_rent_counter.labels(station_id, station_name).inc(diff)

            # Update previous count
            previous_bike_counts[key] = bike_count

        except Exception as e:
            print(f"Error processing message: {e}")
            continue

    print("✅ Exported metrics:", {
        "bike_count": bike_count,
        "rack_total": rack_total,
        "ratio": utilization
    })

if __name__ == "__main__":
    while True:
        try:
            start_exporter()
        except Exception as e:
            print(f"Exporter crashed with error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
