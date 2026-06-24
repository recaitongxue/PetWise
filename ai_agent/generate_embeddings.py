import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import KnowledgeBase

print("=" * 80)
print("批量生成嵌入向量")
print("=" * 80)

kb = KnowledgeBase()

conn = sqlite3.connect(kb.db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT id, title, full_text, embedding FROM knowledge WHERE embedding IS NULL OR embedding = "null" OR embedding = ""')
rows = cursor.fetchall()

print(f"需要生成嵌入的记录数: {len(rows)}")
print()

if not rows:
    print("所有记录都已有嵌入向量")
    sys.exit(0)

success_count = 0
fail_count = 0

for row in rows:
    knowledge_id = row['id']
    title = row['title']
    full_text = row['full_text']
    
    if not full_text or full_text.strip() == '':
        print(f"跳过 {knowledge_id}: {title} - 无文本内容")
        fail_count += 1
        continue
    
    try:
        embedding = kb._create_embedding(full_text)
        
        if embedding:
            embedding_json = json.dumps(embedding)
            cursor.execute('UPDATE knowledge SET embedding = ? WHERE id = ?', (embedding_json, knowledge_id))
            success_count += 1
            print(f"✓ {knowledge_id}: {title[:30]}... - 维度: {len(embedding)}")
        else:
            print(f"✗ {knowledge_id}: {title[:30]}... - 嵌入生成失败")
            fail_count += 1
            
    except Exception as e:
        print(f"✗ {knowledge_id}: {title[:30]}... - 错误: {str(e)[:50]}")
        fail_count += 1

conn.commit()
conn.close()

print()
print("=" * 80)
print(f"完成! 成功: {success_count}, 失败: {fail_count}")
print("=" * 80)
