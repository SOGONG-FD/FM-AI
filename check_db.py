from sqlalchemy import create_engine, inspect
from database import DB_URL

engine = create_engine(DB_URL)
inspector = inspect(engine)

# 테이블 목록 확인
tables = inspector.get_table_names()
print("\n=== 테이블 목록 ===")
for table in tables:
    print(f"\n테이블명: {table}")

    # 컬럼 정보 확인
    columns = inspector.get_columns(table)
    print("\n컬럼 정보:")
    for column in columns:
        print(f"- {column['name']}: {column['type']}")

    # 인덱스 정보 확인
    indexes = inspector.get_indexes(table)
    if indexes:
        print("\n인덱스 정보:")
        for index in indexes:
            print(f"- {index['name']}: {index['column_names']}")
