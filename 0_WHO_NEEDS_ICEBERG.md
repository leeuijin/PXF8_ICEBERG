# 프로젝트 요구사항 
- 데이터 쓰기/읽기가 동시에 가능해야 한다.
-  데이터 쓰기/읽기가 발생하는 상황에서 동시에 스키마 변경이 가능해야 한다.
- 단일 테이블로 페타바이트 규모의 데이터를 저장할 수 있어야 한다.
- 수십만 개의 테이블 운영이 가능해야 한다.
- 데이터 포맷으로 인한 쿼리 엔진 제한이 없어야 한다.
- 데이터 저장소와 쿼리 컴퓨팅 노드가 분리되어 있어야 한다.
- 데이터 압축 효율이 우수해야 한다.

# Greenplum & Iceberg Architecture
<img width="1024" height="559" alt="GPDB_PXF_ICEBERG" src="https://github.com/user-attachments/assets/8acd2610-fcd3-4a03-8520-ced114e20037" />
- Iceberg 카탈로그 데이터베이스는 TanzuSQL(PostgreSQL) 에도 구축 가능하고 Greenplum 에도 구축이 가능합니다. 그러나 PostgreSQL에 별도 데이터베이스로 관리하는것을 권장합니다.


