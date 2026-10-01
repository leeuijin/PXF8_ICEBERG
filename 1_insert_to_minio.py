import datetime
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    IntegerType,
    StringType,
    TimestampType,
    LongType,
    NestedField,
)
from pyiceberg.exceptions import NoSuchTableError

# 1. MinIO 환경에 맞춘 Catalog 설정
# (주의) AWS Glue 대신 로컬/사내 메타스토어를 연결해야 합니다. 여기서는 테스트용 SQLite를 사용합니다.
catalog = load_catalog(
    "default",
    **{
        "type": "sql",
        "uri": "postgresql://gpadmin:changeme@100.107.233.76:5432/iceberg_catalog",
        "s3.endpoint": "http://0.0.0.0:9005",             # MinIO 서버 주소 및 포트
        "s3.access-key-id": "Access_Key",                # MinIO Access Key
        "s3.secret-access-key": "Secret_Key",            # MinIO Secret Key
        "s3.path-style-access": "true",                  # MinIO 사용 시 필수 설정 (버킷명을 경로처럼 취급)
        "s3.region": "ap-northeast-2",                   # MinIO 기본 리전
	"downcast-ns-timestamp-to-us-on-write": "true"
    }
)

# 2. Iceberg 테이블 스키마 정의
schema = Schema(
    NestedField(field_id=1, name="event_id", field_type=IntegerType(), required=False),
    NestedField(field_id=2, name="event_type", field_type=StringType(), required=False),
    NestedField(field_id=3, name="event_time", field_type=TimestampType(), required=False),
    NestedField(field_id=4, name="user_id", field_type=LongType(), required=False),
    NestedField(field_id=5, name="payload", field_type=StringType(), required=False),
)

namespace = "analytics"
table_name = "clickstream_events"
identifier = f"{namespace}.{table_name}"

# MinIO에 생성해둔 버킷 이름 설정 (예: my-minio-bucket)
minio_bucket = "iceberg"
s3_location = f"s3://{minio_bucket}/{namespace}.db/{table_name}"

# 3. 테이블 생성 또는 로드
try:
    table = catalog.load_table(identifier)
    print(f"Table '{identifier}' loaded successfully.")
except NoSuchTableError:
    print(f"Table '{identifier}' not found. Creating a new table...")

    if namespace not in [ns[0] for ns in catalog.list_namespaces()]:
        catalog.create_namespace(namespace)

    table = catalog.create_table(
        identifier=identifier,
        schema=schema,
        location=s3_location
    )
    print("Table created successfully.")

# 4. 삽입할 데이터 생성
now = datetime.datetime.now()
data = {
    "event_id": [101, 102, 103],
    "event_type": ["lee", "uijin", "aiden"],
    "event_time": [now, now, now],
    "user_id": [5001, 5002, 5001],
    "payload": [
        '{"device": "mobile", "ip": "192.168.1.1"}',
        '{"item_id": 998, "button": "add_to_cart"}',
        '{"order_id": "ORD-1234", "amount": 25000}'
    ]
}

df = pd.DataFrame(data)

# timezone 제거 (timestamp without time zone)
df['event_time'] = pd.to_datetime(df['event_time']).dt.tz_localize(None)
df['event_time'] = df['event_time'].astype('datetime64[us]')
df['event_id'] = df['event_id'].astype('int32')

# 5. Pandas DF -> PyArrow Table 변환
arrow_table = pa.Table.from_pandas(df)

# 6. MinIO에 데이터 Append
table.append(arrow_table)
print(f"Successfully appended {len(df)} rows to {identifier} in MinIO.")

# 실행 예
# (venv) [hadoop@vm2-hdfs python]$ python insert_to_minio.py
# Table 'analytics.clickstream_events' loaded successfully.
#Successfully appended 3 rows to analytics.clickstream_events in MinIO.
