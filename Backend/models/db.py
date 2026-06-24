import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'petwise.db')

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT DEFAULT 'user',
            avatar TEXT,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            breed TEXT,
            category TEXT,
            age INTEGER,
            gender TEXT,
            avatar TEXT,
            bio TEXT,
            birthday DATE,
            weight REAL,
            color TEXT,
            neutered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS recognitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            image_path TEXT,
            result TEXT,
            confidence REAL,
            breed TEXT,
            top5 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            breed_context TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            breed TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, breed)
        );

        CREATE TABLE IF NOT EXISTS breed_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            breed TEXT UNIQUE NOT NULL,
            category TEXT,
            origin TEXT,
            personality TEXT,
            lifespan TEXT,
            feeding TEXT,
            care TEXT,
            common_issues TEXT,
            suitable_for TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            breed TEXT NOT NULL,
            content TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            is_pinned INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            admin_reply TEXT,
            replied_by INTEGER,
            replied_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_recognitions_user ON recognitions(user_id);
        CREATE INDEX IF NOT EXISTS idx_recognitions_created ON recognitions(created_at);
        CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);
        CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
        CREATE INDEX IF NOT EXISTS idx_comments_breed ON comments(breed);

        CREATE TABLE IF NOT EXISTS llm_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            provider TEXT NOT NULL,
            api_key TEXT,
            base_url TEXT,
            model_name TEXT NOT NULL,
            max_tokens INTEGER DEFAULT 2048,
            temperature REAL DEFAULT 0.7,
            top_p REAL DEFAULT 0.9,
            is_active INTEGER DEFAULT 1,
            is_default INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tags TEXT,
            source TEXT,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_llm_models_active ON llm_models(is_active);

        CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
        CREATE INDEX IF NOT EXISTS idx_knowledge_active ON knowledge_base(is_active);

        -- 新增表：用户纠错记录
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recognition_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            original_breed TEXT NOT NULL,
            corrected_breed TEXT NOT NULL,
            confidence REAL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            reviewed_by INTEGER,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recognition_id) REFERENCES recognitions(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        );

        -- 新增表：难样本收集
        CREATE TABLE IF NOT EXISTS hard_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recognition_id INTEGER,
            user_id INTEGER,
            image_path TEXT NOT NULL,
            predicted_breed TEXT NOT NULL,
            confidence REAL,
            is_low_confidence INTEGER DEFAULT 0,
            is_user_corrected INTEGER DEFAULT 0,
            corrected_breed TEXT,
            collected_reason TEXT,
            status TEXT DEFAULT 'pending',
            reviewed_by INTEGER,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recognition_id) REFERENCES recognitions(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        );

        -- 新增表：模型版本管理
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            model_path TEXT NOT NULL,
            framework TEXT DEFAULT 'PyTorch',
            num_classes INTEGER DEFAULT 23,
            training_accuracy REAL,
            validation_accuracy REAL,
            top1_accuracy REAL,
            top5_accuracy REAL,
            is_active INTEGER DEFAULT 0,
            is_loaded INTEGER DEFAULT 0,
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        -- 新增表：宠物健康记录
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            record_type TEXT NOT NULL,
            record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            weight REAL,
            food_amount REAL,
            food_type TEXT,
            stool_status TEXT,
            activity_level TEXT,
            mood TEXT,
            notes TEXT,
            consultation_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        );

        -- 新增表：智能日程提醒
        CREATE TABLE IF NOT EXISTS schedule_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            scheduled_date DATE NOT NULL,
            is_completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        );

        -- 新增表：Prompt版本管理
        CREATE TABLE IF NOT EXISTS prompt_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_type TEXT NOT NULL,
            version TEXT NOT NULL,
            content TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id),
            UNIQUE(prompt_type, version)
        );

        -- 新增表：用户限流记录
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL,
            request_count INTEGER DEFAULT 0,
            reset_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, endpoint)
        );

        -- 新增表：系统监控指标
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_type TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            unit TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 新增表：评论点赞
        CREATE TABLE IF NOT EXISTS comment_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES comments(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(comment_id, user_id)
        );

        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_corrections_user ON corrections(user_id);
        CREATE INDEX IF NOT EXISTS idx_corrections_status ON corrections(status);
        CREATE INDEX IF NOT EXISTS idx_hard_examples_status ON hard_examples(status);
        CREATE INDEX IF NOT EXISTS idx_hard_examples_collected ON hard_examples(is_low_confidence, is_user_corrected);
        CREATE INDEX IF NOT EXISTS idx_model_versions_active ON model_versions(is_active);
        CREATE INDEX IF NOT EXISTS idx_health_records_pet ON health_records(pet_id);
        CREATE INDEX IF NOT EXISTS idx_health_records_date ON health_records(record_date);
        CREATE INDEX IF NOT EXISTS idx_schedule_reminders_pet ON schedule_reminders(pet_id);
        CREATE INDEX IF NOT EXISTS idx_schedule_reminders_date ON schedule_reminders(scheduled_date);
        CREATE INDEX IF NOT EXISTS idx_prompt_versions_active ON prompt_versions(prompt_type, is_active);
        CREATE INDEX IF NOT EXISTS idx_rate_limits_user ON rate_limits(user_id, endpoint);
        CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics(metric_type, recorded_at);
        
        -- 新增表：限流配置
        CREATE TABLE IF NOT EXISTS rate_limit_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL UNIQUE,
            daily_limit INTEGER DEFAULT 100,
            hourly_limit INTEGER DEFAULT 20,
            per_minute_limit INTEGER DEFAULT 5,
            is_enabled INTEGER DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 新增表：敏感词过滤规则
        CREATE TABLE IF NOT EXISTS sensitive_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            category TEXT DEFAULT 'medical',
            severity TEXT DEFAULT 'medium',
            is_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 新增表：敏感内容阻断日志
        CREATE TABLE IF NOT EXISTS sensitive_content_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            blocked_content TEXT,
            trigger_word TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- 新增表：Prompt提示词模板
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            prompt_type TEXT NOT NULL,
            content TEXT NOT NULL,
            variables TEXT,
            version INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
    ''')

    # 添加缺失的字段（用于问诊记录）
    try:
        cursor.execute('ALTER TABLE health_records ADD COLUMN consultation_data TEXT')
        db.commit()
    except sqlite3.OperationalError:
        pass  # 字段已存在

    # 添加嵌入模型相关字段
    try:
        cursor.execute('ALTER TABLE llm_models ADD COLUMN is_embedding INTEGER DEFAULT 0')
        db.commit()
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE llm_models ADD COLUMN embedding_dim INTEGER DEFAULT 0')
        db.commit()
    except sqlite3.OperationalError:
        pass

    if cursor.execute('SELECT COUNT(*) FROM breed_info').fetchone()[0] == 0:
        init_breed_info(cursor)

    db.commit()
    db.close()

def init_breed_info(cursor):
    breeds_data = [
        ("中华田园犬", "dog", "中国", "忠诚、聪明、活泼", "12-15年", "适量运动，均衡饮食", "定期体检，注意毛发护理", "皮肤病、关节问题", "有经验的主人"),
        ("吉娃娃", "dog", "墨西哥", "活泼、警觉、粘人", "12-20年", "少量多餐，避免剧烈运动", "注意保暖，定期检查牙齿", "心脏疾病、牙齿问题", "老年人、公寓住户"),
        ("哈士奇", "dog", "西伯利亚", "友善、活泼、好奇心强", "12-14年", "高蛋白饮食，大量饮水", "定期运动，注意降温", "髋关节发育不良、眼部疾病", "户外爱好者"),
        ("德牧", "dog", "德国", "忠诚、勇敢、聪明", "9-13年", "适量蛋白质，注意关节", "定期训练和社交", "髋关节发育不良、胃扭转", "有训练经验的主人"),
        ("拉布拉多", "dog", "加拿大", "友善、活泼、聪明", "10-12年", "控制饮食，防止肥胖", "每天适量运动", "肥胖症、关节问题", "家庭、有孩子的用户"),
        ("杜宾", "dog", "德国", "忠诚、勇敢、警觉", "10-13年", "高质量蛋白，均衡营养", "早期社会化训练", "心脏疾病、血凝障碍", "有经验的主人"),
        ("柴犬", "dog", "日本", "独立、忠诚、活泼", "12-15年", "适量喂食，控制热量", "毛发护理，定期体检", "皮肤问题、膝关节脱位", "有耐心的主人"),
        ("法国斗牛", "dog", "法国", "友善、活泼、粘人", "10-12年", "少量多餐，避免高温", "注意呼吸系统护理", "呼吸系统疾病、脊椎问题", "城市公寓住户"),
        ("萨摩耶", "dog", "西伯利亚", "友善、活泼、忠诚", "12-14年", "定期毛发护理", "适量运动，心脏监测", "糖尿病、皮肤问题", "有时间陪伴的主人"),
        ("藏獒", "dog", "中国西藏", "独立、忠诚、勇敢", "10-16年", "大量蛋白质，大活动空间", "早期社会化训练", "关节问题、皮肤疾病", "有大型犬饲养经验者"),
        ("金毛", "dog", "英国", "友善、聪明、活泼", "10-12年", "控制饮食，定期毛发护理", "适量运动", "肿瘤、关节问题", "家庭、有孩子的用户"),
        ("阿比西尼亚猫", "cat", "埃塞俄比亚", "好奇、活泼、聪明", "12-15年", "高质量猫粮", "提供攀爬设施，定期互动", "心脏病、肾脏疾病", "有时间陪伴的主人"),
        ("埃及猫", "cat", "埃及", "聪明、活泼、亲人", "12-15年", "均衡营养", "关注肾脏健康", "肾脏疾病、牙齿问题", "喜欢互动的主人"),
        ("豹猫", "cat", "美国", "活泼、好奇、亲人", "12-16年", "高蛋白饮食", "提供玩具和攀爬设施", "关节问题、心脏疾病", "活跃的主人"),
        ("布偶猫", "cat", "美国", "温顺、安静、亲人", "12-17年", "定期毛发护理", "注意心脏肾脏健康", "心脏病、肾脏疾病", "喜欢安静猫咪的主人"),
        ("波斯猫", "cat", "伊朗", "安静、温柔、亲人", "12-17年", "每天梳理毛发", "注意泪痕清洁", "呼吸道问题、泪痕", "有时间打理毛发的主人"),
        ("缅甸猫", "cat", "缅甸", "活泼、好奇、亲人", "12-16年", "控制体重", "需要陪伴和互动", "糖尿病、肥胖", "在家办公的主人"),
        ("俄罗斯蓝猫", "cat", "俄罗斯", "安静、害羞、忠诚", "15-20年", "提供安静环境", "定期毛发护理", "膀胱结石", "喜欢安静环境的主人"),
        ("孟买猫", "cat", "美国", "好奇、活泼、亲人", "12-16年", "定期互动", "注意心脏健康", "心脏疾病、呼吸问题", "喜欢互动的主人"),
        ("缅因猫", "cat", "美国", "温顺、友好、聪明", "12-15年", "大型活动空间", "定期毛发护理", "心脏病、髋关节问题", "有大空间的主人"),
        ("无毛猫", "cat", "加拿大", "活泼、好奇、亲人", "12-16年", "皮肤护理", "注意保暖和防晒", "皮肤问题、体温调节问题", "对猫毛过敏的主人"),
        ("暹罗猫", "cat", "泰国", "活泼、好奇、亲人", "12-15年", "陪伴和互动", "注意呼吸系统健康", "呼吸道疾病、牙齿问题", "喜欢叫猫咪的主人"),
        ("英国短毛猫", "cat", "英国", "安静、温和、亲人", "12-17年", "控制饮食避免肥胖", "定期毛发护理", "心脏病、肥胖、肾脏疾病", "新手铲屎官")
    ]

    for breed in breeds_data:
        cursor.execute('''
            INSERT INTO breed_info (breed, category, origin, personality, lifespan, feeding, care, common_issues, suitable_for)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', breed)