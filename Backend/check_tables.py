import sqlite3

conn = sqlite3.connect('petwise.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('=' * 60)
print('数据库中的所有表:')
print('=' * 60)
for i, table in enumerate(tables, 1):
    table_name = table[0]
    # 获取表行数
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'{i}. {table_name} ({count} 条记录)')

print('=' * 60)
print(f'总计: {len(tables)} 个表')
print('=' * 60)

conn.close()
