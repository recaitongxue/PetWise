"""
测试各个本地模块功能（不需要真实API密钥）
"""
import sys
import os
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("PetWise AI Agent - 本地模块测试")
print("=" * 60)

test_results = []

def test_config():
    """测试配置模块"""
    print("\n【测试 1】配置模块 (config.py)")
    try:
        from config import Config
        print("✓ 成功导入 Config")
        print(f"  - API Host: {Config.API_HOST}")
        print(f"  - API Port: {Config.API_PORT}")
        print(f"  - Model: {Config.SILICONFLOW_MODEL}")
        print(f"  - Knowledge DB: {Config.KNOWLEDGE_DB_PATH}")
        test_results.append(("Config", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 配置模块测试失败: {e}")
        test_results.append(("Config", f"FAIL: {e}"))
        return False

def test_utils():
    """测试工具模块"""
    print("\n【测试 2】工具模块 (utils.py)")
    try:
        from utils import (
            setup_logging, ensure_directory, load_json_file, 
            save_json_file, format_timestamp, sanitize_text
        )
        print("✓ 成功导入 utils")
        
        # 测试时间戳
        ts = format_timestamp()
        print(f"  - 时间戳格式: {ts}")
        
        # 测试文本清理
        clean_text = sanitize_text("  Hello World!  ")
        print(f"  - 文本清理: '{clean_text}'")
        
        test_results.append(("Utils", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 工具模块测试失败: {e}")
        test_results.append(("Utils", f"FAIL: {e}"))
        return False

def test_prompt_manager():
    """测试提示词管理模块"""
    print("\n【测试 3】提示词管理模块 (prompt_manager.py)")
    try:
        from prompt_manager import PromptManager
        print("✓ 成功导入 PromptManager")
        
        pm = PromptManager()
        print("✓ PromptManager 初始化成功")
        
        # 获取系统提示词
        system_prompt = pm.get_system_prompt()
        print(f"  - 系统提示词长度: {len(system_prompt)} 字符")
        print(f"  - 系统提示词前50字符: {system_prompt[:50]}...")
        
        test_results.append(("PromptManager", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 提示词管理模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("PromptManager", f"FAIL: {e}"))
        return False

def test_knowledge_base():
    """测试知识库模块"""
    print("\n【测试 4】知识库模块 (knowledge_base.py)")
    try:
        from knowledge_base import KnowledgeBase
        print("✓ 成功导入 KnowledgeBase")
        
        # 使用临时数据库文件
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "test_kb.db")
        
        kb = KnowledgeBase(db_path=temp_db)
        print("✓ KnowledgeBase 初始化成功")
        
        # 测试添加知识
        test_knowledge = {
            "title": "测试宠物知识",
            "content": "这是一条测试知识，关于狗狗护理",
            "category": "dogs"
        }
        
        result = kb.import_knowledge(test_knowledge, category="dogs")
        print(f"✓ 知识导入: {result['success']}, ID: {result.get('knowledge_id')}")
        
        # 测试获取统计
        stats = kb.get_statistics()
        print(f"✓ 知识库统计: {stats['total_entries']} 条记录")
        
        # 测试查询
        results = kb.query_knowledge("狗狗", limit=5)
        print(f"✓ 知识查询: 找到 {len(results)} 条结果")
        
        # 测试获取分类
        categories = kb.get_all_categories()
        print(f"✓ 知识分类: {categories}")
        
        test_results.append(("KnowledgeBase", "PASS"))
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ 知识库模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("KnowledgeBase", f"FAIL: {e}"))
        return False

def test_exceptions():
    """测试异常模块"""
    print("\n【测试 5】异常模块 (exceptions.py)")
    try:
        from exceptions import (
            AIAgentException, KnowledgeBaseException, 
            PromptException, APIException
        )
        print("✓ 成功导入异常类")
        
        # 测试异常
        exc1 = KnowledgeBaseException("测试知识库异常")
        exc2 = APIException("测试API异常")
        print(f"✓ 异常创建: {type(exc1)}, {type(exc2)}")
        
        test_results.append(("Exceptions", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 异常模块测试失败: {e}")
        test_results.append(("Exceptions", f"FAIL: {e}"))
        return False

def test_cache_module():
    """测试缓存模块"""
    print("\n【测试 6】缓存模块 (cache.py)")
    try:
        from cache import Cache, get_cache, init_cache
        print("✓ 成功导入 Cache")
        
        init_cache()
        cache = get_cache()
        print("✓ 缓存初始化成功")
        
        # 测试缓存操作
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")
        print(f"✓ 缓存读写: test_key = '{value}'")
        
        # 测试统计
        stats = cache.get_stats()
        print(f"✓ 缓存统计: {stats}")
        
        test_results.append(("Cache", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 缓存模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("Cache", f"FAIL: {e}"))
        return False

def test_structured_logger():
    """测试结构化日志模块"""
    print("\n【测试 7】结构化日志模块 (structured_logger.py)")
    try:
        from structured_logger import setup_structured_logging, get_logger
        print("✓ 成功导入 structured_logger")
        
        setup_structured_logging()
        logger = get_logger("test")
        print("✓ 日志初始化成功")
        
        logger.info("测试日志消息")
        print("✓ 日志记录成功")
        
        test_results.append(("StructuredLogger", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 结构化日志模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("StructuredLogger", f"FAIL: {e}"))
        return False

def test_error_handlers():
    """测试错误处理模块"""
    print("\n【测试 8】错误处理模块 (error_handlers.py)")
    try:
        from error_handlers import setup_error_handlers
        print("✓ 成功导入 error_handlers")
        
        # 简单测试导入和函数存在性
        print("✓ 错误处理模块加载成功")
        
        test_results.append(("ErrorHandlers", "PASS"))
        return True
    except Exception as e:
        print(f"✗ 错误处理模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("ErrorHandlers", f"FAIL: {e}"))
        return False

def test_api_routes():
    """测试API路由定义（不启动服务器）"""
    print("\n【测试 9】API路由模块 (api.py)")
    try:
        from api import app
        print("✓ 成功导入 FastAPI app")
        
        # 获取路由信息
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else ''
                routes.append(f"{methods} {route.path}")
        
        print(f"✓ API 路由数量: {len(routes)}")
        print("  主要路由:")
        for route in routes[:10]:  # 只显示前10个
            print(f"    - {route}")
        
        test_results.append(("APIRoutes", "PASS"))
        return True
    except Exception as e:
        print(f"✗ API路由模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("APIRoutes", f"FAIL: {e}"))
        return False

def print_summary():
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in test_results:
        if result == "PASS":
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = f"✗ {result}"
        print(f"{name:20s} : {status}")
    
    print("\n" + "-" * 60)
    print(f"总计: {len(test_results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    # 运行所有测试
    test_config()
    test_utils()
    test_exceptions()
    test_prompt_manager()
    test_knowledge_base()
    test_cache_module()
    test_structured_logger()
    test_error_handlers()
    test_api_routes()
    
    # 打印总结
    success = print_summary()
    
    sys.exit(0 if success else 1)
