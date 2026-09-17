# ICEBERG

<img width="753" height="780" alt="metadata aver" src="https://github.com/user-attachments/assets/c8e83147-248e-4770-9964-818f9b35919b" />

# ICEBERG 특징
1. 완벽한 ACID 트랜잭션 지원
기존 데이터 레이크에서는 데이터 파일이 덮어써지는 중간에 다른 사람이 쿼리를 돌리면 깨진 데이터를 보게 되는 문제가 있었습니다.
Iceberg는 스냅샷 격리(Snapshot Isolation) 방식을 사용하여 여러 사용자가 동시에 데이터를 읽고 쓰더라도 데이터 정합성이 완벽하게 유지됩니다. 객체 스토리지 위에서도 RDB처럼 안전하게 INSERT, UPDATE, DELETE, MERGE 연산이 가능합니다.

2. 타임 트래블 (Time Travel) 및 롤백
데이터가 변경될 때마다 기존 데이터를 지우지 않고 새로운 상태의 스냅샷(Snapshot)을 생성하여 버전을 관리합니다.
타임 트래블: "어제 오후 3시 시점의 테이블 상태"를 그대로 쿼리할 수 있습니다.
롤백: 배치 작업에 실패하거나 데이터를 실수로 지웠을 때, 특정 스냅샷 시점으로 테이블을 즉각 되돌릴 수 있습니다.
3. 유연한 스키마 진화 (Schema Evolution)
컬럼 추가, 삭제, 이름 변경, 데이터 타입 변경, 순서 변경 시 전체 데이터를 다시 쓸(Rewrite) 필요가 없습니다.
메타데이터만 업데이트하는 방식으로 처리되므로 스키마 변경이 빠르고 안전하며, 과거 데이터와 새로운 데이터가 충돌하지 않고 자연스럽게 호환됩니다.

4. 숨겨진 파티셔닝 (Hidden Partitioning)
기존 Hive 포맷에서는 쿼리 속도를 높이려면 사용자가 반드시 쿼리 조건절에 파티션 컬럼(예: ymd='2023-10-01')을 명시해야 했고, 누락하면 전체 데이터를 뒤지는 참사가 발생했습니다.
Iceberg는 원본 Timestamp 데이터만 있어도 내부 메타데이터를 통해 엔진이 알아서 일/월/년 단위 파티션을 유추하고 필터링합니다. 쿼리 작성자의 실수로 인한 성능 저하를 방지합니다.

5. 파일 단위의 메타데이터 관리 (고성능)
디렉토리(폴더) 단위로 파일을 관리하던 기존 방식은 파일 수가 많아지면 목록을 불러오는(List) 작업 자체가 엄청난 병목이었습니다.
Iceberg는 트리에 가까운 메타데이터 구조를 가집니다. 파일 레벨에서 통계 정보(Min/Max 값, Null 개수 등)를 기록해 두기 때문에, 쿼리 실행 시 실제로 읽어볼 필요가 없는 파일들을 디스크 스캔 전에 획기적으로 걸러냅니다(Data Skipping).

6. 특정 엔진에 종속되지 않음 (Engine Agnostic)
Spark, Trino, Flink, Presto 등 다양한 오픈소스 분산 처리 엔진에서 동일한 Iceberg 테이블을 동시에 읽고 쓸 수 있습니다. 최근에는 Snowflake, BigQuery, AWS Redshift 같은 상용 데이터 웨어하우스들도 Iceberg 포맷을 네이티브로 지원하며 업계 표준으로 자리 잡고 있습니다.

7.컴퓨팅-스토리지 구조적인 완벽한 분리: 
기존 구조의 한계 (컴퓨팅-스토리지 결합): 기존 MPP DW(그린플럼 등)나 하둡은 CPU/메모리와 디스크가 하나의 세그먼트(노드)에 단단히 묶여 있습니다(Shared-Nothing). 
단순히 데이터를 저장할 공간(디스크)이 부족해졌을 뿐인데, 굳이 필요 없는 비싼 CPU와 메모리까지 포함된 서버 장비를 통째로 추가해야 합니다. 또한 노드 추가 시 데이터 재분배(Redistribute)에 엄청난 시간과 부하가 걸리는 것은 덤입니다.
컴퓨팅-스토리지 구조적인 완벽한 분리를 통한 스토리지 저비용 독립 확장: 데이터는 AWS S3, GCS 같은 클라우드 객체 저장소에 보관합니다. 저장 공간이 부족하면 스토리지 용량만 아주 저렴하게 무한대로 늘리면 끝입니다.
컴퓨팅 탄력적 독립 확장: 쿼리 성능이 더 필요하면 데이터를 옮기거나 재분배할 필요 없이 컴퓨팅 클러스터(Spark, Trino 등)만 순간적으로 병렬로 늘렸다가(Scale-out), 야간에 사용자가 없으면 0으로 줄여버릴 수 있습니다.
엔진 간 성능 간섭 제로: 하나의 Iceberg 데이터를 두고, 데이터 엔지니어는 Spark 클러스터로 무거운 ETL 배치를 돌리고 비즈니스 분석가는 별도의 Trino 클러스터로 대시보드를 띄울 수 있습니다. 스토리지만 공유할 뿐 컴퓨팅 노드가 분리되어 있어 서로 쿼리 속도를 깎아먹지 않습니다.

# 파일 구조 및 역활

1. JSON 파일 (최상위 메타데이터)
* 역할: 테이블의 진입점(Entry Point)이자 설계도 역할을 합니다. 
* 하는 일: 테이블의 스키마(컬럼 구조), 파티션 설정 방식, 테이블의 전체 히스토리, 그리고 테이블의 현재 상태를 나타내는 최신 스냅샷(Snapshot) 정보 등을 담고 있습니다. 
* 동작 방식: 쿼리가 들어오면 카탈로그(예: PostgreSQL)는 가장 먼저 최신 JSON 파일을 읽어 테이블의 구조를 파악하고, 데이터를 찾기 위한 다음 단계(Avro 파일 위치)의 포인터를 얻습니다. 


2. AVRO 파일 (매니페스트 / 인덱스)
* 역할: 실제 데이터 파일들의 목록과 통계를 관리하는 인덱스(Index) 역할을 합니다. (Iceberg에서는 이를 Manifest List와 Manifest File이라고 부릅니다.) 
* 하는 일: S3에 흩어진 실제 데이터 파일들의 정확한 경로, 파티션 값, 그리고 가장 중요한 데이터 통계(각 컬럼의 최댓값, 최솟값, Null 개수 등)를 저장합니다. 
* 왜 Avro 포맷을 쓸까요?: 쿼리 엔진은 파일을 무작정 다 읽지 않고, 이 통계 정보를 먼저 확인하여 쿼리 조건(WHERE 절)에 맞지 않는 파일은 통째로 스킵(Data Skipping)합니다. 이런 메타데이터 레코드들을 순차적으로 아주 빠르게 읽어내는 데에는 로우(Row) 기반 포맷인 Avro가 유리하기 때문입니다. 
* 
3. PARQUET 파일 (실제 데이터)
* 역할: 테이블의 실제 데이터(레코드)가 담겨 있는 파일입니다. 
* 하는 일: 사용자가 저장한 실제 클릭스트림이나 트랜잭션 데이터를 압축하여 보관합니다. (Iceberg는 ORC 파일도 지원하지만 보통 Parquet을 표준으로 사용합니다.) 
* 왜 Parquet 포맷을 쓸까요?: 컬럼형(Columnar) 압축 포맷이므로 집계나 분석 쿼리를 돌릴 때 필요한 특정 컬럼만 쏙쏙 뽑아서 빠르게 읽어올 수 있어 디스크 I/O 비용을 크게 아껴줍니다. 
💡 Greenplum FDW의 쿼리 실행 흐름 앞서 성공하신 SELECT 쿼리를 실행했을 때, 내부적으로는 JSON (테이블 구조와 최신 상태 확인)
  ->  AVRO (통계값을 보고 읽을 필요가 없는 파일 걸러내기)
  -> PARQUET (조건을 통과한 최소한의 실제 데이터만 S3에서 다운로드) 순서로 파일들을 추적하여 대용량 데이터를 효율적으로 조회)

# 기존 데이터를 UPDATE 하거나 DELETE 하면 Parquet 데이터 파일이나 Avro 파일들은 내부적으로 어떻게 처리될까?

Apache Iceberg의 가장 핵심적인 설계 철학은 "기존 데이터 파일(Parquet)은 절대로 직접 수정하지 않는다(Immutable)"는 것입니다.
UPDATE나 DELETE 명령이 실행되면 기존 파일을 덮어쓰는 대신 새로운 파일을 생성하며, 테이블 설정에 따라 두 가지 방식 중 하나로 동작합니다.

<img width="639" height="638" alt="Copy-on-Write (CoW)" src="https://github.com/user-attachments/assets/0e5384fd-4c7e-482a-b2d2-7000ee18807c" />

Copy-on-Write (CoW) 	: 변경 대상이 포함된 기존 Parquet 파일을 메모리로 읽어온 뒤,수정/삭제를 반영하여 완전히 새로운 Parquet 파일을 통째로 다시 작성, 조회(Read) 시 바로 새 파일만 읽으면 되므로 쿼리 속도 빠름, 쓸 때(Write)마다 파일 전체를 다시 쓰므로 쓰기 비용 증가
Merge- on-Read (MoR) 	: 기존 원본 Parquet 파일은 그대로 둡니다. 대신 어떤 행(Row)이 지워졌거나 수정되었는지만 기록하는 **작은 삭제 파일(Delete File)**을 새로 생성, 쓰기 속도가 매우 빠르고 효율적입니다. 조회할 때 원본 파일과 삭제 파일을 실시간으로 병합(Merge)해야 하므로 쿼리 속도가 다소 느려짐
참고) 기본값(Default)은 일반적으로 Copy-on-Write로 설정

CREATE TABLE analytics.clickstream_events ( 
event_id BIGINT,
event_type STRING,
event_time TIMESTAMP )
	USING iceberg TBLPROPERTIES ( 
	'write.delete.mode' = 'merge-on-read',
	'write.update.mode' = 'merge-on-read',
	'write.merge.mode' = 'merge-on-read' 
);  

ALTER TABLE analytics.clickstream_events 
SET TBLPROPERTIES (
    'write.delete.mode'='merge-on-read',
    'write.update.mode'='merge-on-read'
);

Greenplum(PXF)은 데이터를 읽을(Read) 때 Iceberg의 메타데이터를 확인하여 테이블이 CoW로 쓰였는지, MoR(Delete File 포함)로 쓰였는지 자동으로 파악하고 처리합니다. 따라서 데이터를 읽어오는 Greenplum 쪽에서는 별도의 CoW/MoR 관련 설정을 해줄 필요가 없음
단지 PXF 외의 연결의 데이터 변경 및 수정에 대해서만 다음과 같이 진행

# UPDATE와 DELETE를 반복하면 S3 용량이 계속 늘어날 텐데, 사용하지 않는 오래된 스냅샷과 과거 Parquet 파일들은 어떻게 물리적으로 관리 할까?

Apache Iceberg는 '시간 여행(Time Travel)' 기능을 제공하기 위해 과거 스냅샷과 구버전 Parquet 파일들을 기본적으로 무한정 보관합니다.  S3 저장소 용량 낭비를 막으려면, 데이터를 관리하는 쪽 엔진(주로 Apache Spark)에서 시스템 프로시저(CALL 명령어)를 통해 정기적인 청소 작업을 수행

핵심 유지보수 작업은 크게 두 가지
 1. 스냅샷 만료 (Expire Snapshots) 기준 삭제 
 ex)Spark SQL
-- 지정한 시간 이전의 스냅샷을 지우고, 연관된 쓰레기 데이터를 S3에서 물리적 삭제
CALL spark_catalog.system.expire_snapshots(
  table => 'analytics.clickstream_events',
  older_than => TIMESTAMP '2026-09-10 00:00:00',
  retain_last => 5 -- (선택사항) 최소 5개의 최신 스냅샷은 무조건 남겨둠
);
 2. 고아 파일 제거 (Remove Orphan Files) 기준 삭제 
 ex)Spark SQL -- 메타데이터에 추적되지 않는 잉여 파일을 찾아 S3에서 삭제
CALL spark_catalog.system.remove_orphan_files(
  table => 'analytics.clickstream_events'
);

# 데이터 레이크 실무 권장 파이프라인

실무에서는 S3 용량과 쿼리 성능을 모두 최적화하기 위해 Airflow 등을 사용하여 다음 3단계 파이프라인을 주기적(예: 매일 새벽)으로 스케줄링
Compaction 작업 (2가지 종류) ->  expire_snapshots 작업 -> remove_orphan_files 작업

# 1-1.일반 Compaction  
CALL spark_catalog.system.rewrite_data_files(
  table => 'analytics.clickstream_events'
);

# 1-2.Sorting Compaction  
CALL spark_catalog.system.rewrite_data_files(
  table => 'analytics.clickstream_events',
  strategy => 'sort',
  sort_order => 'event_time DESC, event_type ASC', -- 날짜 및 타입 기준으로 정렬하여 병합
  options => map('target-file-size-bytes', '536870912') -- 타겟 파일 크기를 512MB로 지정
);
# 2.스냅샷 만료 (Expire Snapshots) 기준 삭제 
 ex)Spark SQL
-- 지정한 시간 이전의 스냅샷을 지우고, 연관된 쓰레기 데이터를 S3에서 물리적 삭제
CALL spark_catalog.system.expire_snapshots(
  table => 'analytics.clickstream_events',
  older_than => TIMESTAMP '2026-09-10 00:00:00',
  retain_last => 5 -- (선택사항) 최소 5개의 최신 스냅샷은 무조건 남겨둠
);
# 3.고아 파일 제거 (Remove Orphan Files) 기준 삭제 
 ex)Spark SQL -- 메타데이터에 추적되지 않는 잉여 파일을 찾아 S3에서 삭제
CALL spark_catalog.system.remove_orphan_files(
  table => 'analytics.clickstream_events'
);


