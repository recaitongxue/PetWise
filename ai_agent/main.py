"""
Main entry point for PetWise AI Agent Service
"""
import sys
import argparse
from config import Config
from api import start_server
from ai_service import AIAgentService
from utils import setup_logging

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PetWise AI Agent Service")
    parser.add_argument("--host", type=str, default=Config.API_HOST, help="API server host")
    parser.add_argument("--port", type=int, default=Config.API_PORT, help="API server port")
    parser.add_argument("--test", action="store_true", help="Run service tests")
    parser.add_argument("--import-kb", type=str, help="Import knowledge from JSON file")
    parser.add_argument("--query-kb", type=str, help="Query knowledge base")
    
    args = parser.parse_args()
    
    logger = setup_logging(Config.LOG_LEVEL)
    
    try:
        if args.test:
            logger.info("Running service tests...")
            run_tests()
        elif args.import_kb:
            logger.info(f"Importing knowledge from {args.import_kb}...")
            import_knowledge(args.import_kb)
        elif args.query_kb:
            logger.info(f"Querying knowledge base: {args.query_kb}")
            query_knowledge(args.query_kb)
        else:
            logger.info("Starting AI Agent Service...")
            start_server(host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Service error: {e}")
        sys.exit(1)

def run_tests():
    """Run basic service tests"""
    try:
        logger.info("Initializing AI Service...")
        service = AIAgentService()
        
        logger.info("Testing health check...")
        health = service.health_check()
        print(f"Health Status: {health['status']}")
        
        logger.info("Testing knowledge base...")
        stats = service.knowledge_base_stats()
        print(f"Knowledge Base Entries: {stats['total_entries']}")
        
        logger.info("Testing prompt manager...")
        system_prompt = service.prompt_manager.get_system_prompt()
        print(f"System Prompt Length: {len(system_prompt)} characters")
        
        logger.info("Testing API connection...")
        api_test = service.api_client.test_connection()
        print(f"API Connection: {'Success' if api_test['success'] else 'Failed'}")
        
        logger.info("Testing basic chat...")
        chat_response = service.chat("你好，请介绍一下你的功能。", use_knowledge_base=False)
        print(f"Chat Response: {'Success' if chat_response.get('success') else 'Failed'}")
        
        logger.info("All tests completed successfully!")
        service.close()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

def import_knowledge(file_path: str):
    """Import knowledge from file"""
    try:
        service = AIAgentService()
        
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        result = service.knowledge_base_import(knowledge_data, category="imported")
        
        if result.get('success'):
            print(f"Knowledge imported successfully: {result['knowledge_id']}")
        else:
            print(f"Import failed: {result.get('error')}")
        
        service.close()
        
    except Exception as e:
        logger.error(f"Knowledge import failed: {e}")
        raise

def query_knowledge(query: str):
    """Query knowledge base"""
    try:
        service = AIAgentService()
        
        result = service.knowledge_base_query(query, limit=5)
        
        if result.get('success'):
            print(f"Found {result['count']} results:")
            for i, item in enumerate(result['results'], 1):
                print(f"{i}. Category: {item['category']}")
                print(f"   Relevance: {item['relevance']:.2f}")
                print(f"   Data: {str(item['data'])[:100]}...")
                print()
        else:
            print(f"Query failed: {result.get('error')}")
        
        service.close()
        
    except Exception as e:
        logger.error(f"Knowledge query failed: {e}")
        raise

if __name__ == "__main__":
    main()