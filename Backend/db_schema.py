import sqlite3

conn = sqlite3.connect('petwise.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 获取所有表名
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in c.fetchall()]

print("=" * 80)
print("PetWise 数据库表结构详细文档")
print("=" * 80)

for table in tables:
    print(f"\n\n{'=' * 80}")
    print(f"表名: {table}")
    print("=" * 80)
    
    # 获取表结构
    c.execute(f"PRAGMA table_info({table})")
    columns = c.fetchall()
    
    print("\n【字段信息】")
    print("-" * 80)
    print(f"{'序号':<5} {'字段名':<25} {'数据类型':<20} {'非空':<8} {'主键':<8} {'默认值':<15}")
    print("-" * 80)
    for i, col in enumerate(columns, 1):
        print(f"{i:<5} {col['name']:<25} {col['type']:<20} {'是' if col['notnull'] else '否':<8} {'是' if col['pk'] else '否':<8} {col['dflt_value'] if col['dflt_value'] else 'NULL':<15}")
    
    # 获取外键信息
    c.execute(f"PRAGMA foreign_key_list({table})")
    fks = c.fetchall()
    
    if fks:
        print("\n【外键信息】")
        print("-" * 80)
        print(f"{'字段名':<25} {'引用表':<20} {'引用字段':<15}")
        print("-" * 80)
        for fk in fks:
            print(f"{fk['from']:<25} {fk['table']:<20} {fk['to']:<15}")
    
    # 获取索引信息
    c.execute(f"PRAGMA index_list({table})")
    indexes = c.fetchall()
    
    if indexes:
        print("\n【索引信息】")
        print("-" * 40)
        for idx in indexes:
            c.execute(f"PRAGMA index_info({idx['name']})")
            idx_cols = c.fetchall()
            cols = ', '.join([col['name'] for col in idx_cols])
            unique = "UNIQUE" if idx['unique'] else ""
            print(f"{idx['name']}: {cols} {unique}")
    
    # 获取表数据统计
    c.execute(f"SELECT COUNT(*) as cnt FROM {table}")
    count = c.fetchone()[0]
    print(f"\n【数据统计】当前记录数: {count}")

conn.close()
print("\n\n" + "=" * 80)
print("数据库表结构文档生成完毕")
print("=" * 80)
