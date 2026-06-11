import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'petwise.db')

def migrate():
    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()
    
    # 检查并添加新字段
    columns_to_add = [
        ('birthday', 'DATE'),
        ('weight', 'REAL'),
        ('color', 'TEXT'),
        ('neutered', 'INTEGER DEFAULT 0')
    ]
    
    # 获取现有列
    cursor.execute("PRAGMA table_info(pets)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE pets ADD COLUMN {column_name} {column_type}')
                print(f'Added column {column_name} to pets table')
            except Exception as e:
                print(f'Error adding column {column_name}: {e}')
    
    db.commit()
    db.close()
    print('Migration completed!')

if __name__ == '__main__':
    migrate()
