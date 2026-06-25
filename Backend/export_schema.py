import sqlite3
import json

conn = sqlite3.connect('petwise.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 获取所有表名
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in c.fetchall()]

schema_info = {}

for table in tables:
    # 获取表结构
    c.execute(f"PRAGMA table_info({table})")
    columns = c.fetchall()
    schema_info[table] = {
        'columns': [dict(col) for col in columns],
        'foreign_keys': [],
        'indexes': [],
        'count': c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    }
    
    # 获取外键信息
    c.execute(f"PRAGMA foreign_key_list({table})")
    fks = c.fetchall()
    schema_info[table]['foreign_keys'] = [dict(fk) for fk in fks]
    
    # 获取索引信息
    c.execute(f"PRAGMA index_list({table})")
    indexes = c.fetchall()
    for idx in indexes:
        c.execute(f"PRAGMA index_info({idx['name']})")
        idx_cols = c.fetchall()
        schema_info[table]['indexes'].append({
            'name': idx['name'],
            'columns': [col['name'] for col in idx_cols],
            'unique': bool(idx['unique'])
        })

# 输出JSON格式供后续使用
with open('db_schema.json', 'w', encoding='utf-8') as f:
    json.dump(schema_info, f, ensure_ascii=False, indent=2)

conn.close()
print("Schema exported to db_schema.json")
