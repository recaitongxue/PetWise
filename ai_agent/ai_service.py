"""
AI Agent Service Module
Main service interface for AI functionality with backend/frontend integration points
"""
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime

from config import Config
from knowledge_base import KnowledgeBase
from prompt_manager import PromptManager
from siliconflow_client import SiliconFlowClient
from utils import setup_logging, format_timestamp
from exceptions import AIAgentException, KnowledgeBaseException, PromptException, APIException

logger = setup_logging(Config.LOG_LEVEL)

class AIAgentService:
    """Main AI Agent Service for PetWise System"""
    
    def __init__(self):
        """Initialize AI Agent Service"""
        try:
            Config.validate()
            
            self.knowledge_base = KnowledgeBase()
            self.prompt_manager = PromptManager()
            self.api_client = SiliconFlowClient()
            
            logger.info("AI Agent Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent Service: {e}")
            raise AIAgentException(f"Service initialization failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint for monitoring
        
        Returns:
            Health status dictionary
        """
        try:
            api_status = self.api_client.test_connection()
            kb_stats = self.knowledge_base.get_statistics()
            
            return {
                "status": "healthy",
                "service": "AI Agent Service",
                "timestamp": format_timestamp(),
                "components": {
                    "api_client": {
                        "status": "operational" if api_status["success"] else "degraded",
                        "model": self.api_client.model
                    },
                    "knowledge_base": {
                        "status": "operational",
                        "total_entries": kb_stats["total_entries"]
                    },
                    "prompt_manager": {
                        "status": "operational"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def chat(self, user_message: str,
             use_knowledge_base: bool = True,
             custom_prompt: Optional[str] = None,
             temperature: float = 0.7,
             model: Optional[str] = None,
             pet_context: Optional[Dict[str, Any]] = None,
             breed_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Main chat interface for pet-related queries
        
        Args:
            user_message: User's message/question
            use_knowledge_base: Whether to use knowledge base
            custom_prompt: Optional custom prompt name
            temperature: AI response temperature
            model: Optional AI model name to use
            pet_context: Pet context information for personalized responses
            breed_context: Breed context for the conversation
            
        Returns:
            Response dictionary with AI response
        """
        try:
            logger.info(f"Processing chat request: {user_message[:50]}...")
            
            # 构建上下文提示词
            context_prompt = user_message
            if pet_context:
                context_prompt = f"""宠物档案信息：
- 姓名: {pet_context.get('name', '未知')}
- 品种: {pet_context.get('breed', '未知')}
- 年龄: {pet_context.get('age', '未知')}岁
- 性别: {pet_context.get('gender', '未知')}
- 绝育状态: {'已绝育' if pet_context.get('is_neutered') else '未绝育'}
- 过敏史: {pet_context.get('allergies', '无')}

用户问题: {user_message}

请根据以上宠物档案信息，提供专业的建议和回答。"""
            
            system_prompt = self.prompt_manager.get_combined_prompt(custom_prompt)
            
            if use_knowledge_base:
                query_for_kb = context_prompt if pet_context else user_message
                knowledge_results = self.knowledge_base.query_knowledge(
                    query_for_kb, limit=3
                )
                
                if knowledge_results:
                    knowledge_context = "\n".join([
                        f"- {result['data']}" for result in knowledge_results
                    ])
                    response = self.api_client.chat_with_knowledge(
                        context_prompt, knowledge_context, system_prompt, temperature, model
                    )
                else:
                    response = self.api_client.simple_chat(
                        context_prompt, system_prompt, temperature, model
                    )
            else:
                response = self.api_client.simple_chat(
                    context_prompt, system_prompt, temperature, model
                )
            
            logger.info("Chat request processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def stream_chat(self, user_message: str,
                   use_knowledge_base: bool = True,
                   custom_prompt: Optional[str] = None,
                   temperature: float = 0.7,
                   model: Optional[str] = None) -> Generator[str, None, None]:
        """
        Streaming chat interface for real-time responses
        
        Args:
            user_message: User's message/question
            use_knowledge_base: Whether to use knowledge base
            custom_prompt: Optional custom prompt name
            temperature: AI response temperature
            model: Optional AI model name to use
            
        Yields:
            Response chunks
        """
        try:
            logger.info(f"Processing streaming chat request: {user_message[:50]}...")
            
            system_prompt = self.prompt_manager.get_combined_prompt(custom_prompt)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if use_knowledge_base:
                knowledge_results = self.knowledge_base.query_knowledge(
                    user_message, limit=3
                )
                
                if knowledge_results:
                    knowledge_context = "\n".join([
                        f"- {result['data']}" for result in knowledge_results
                    ])
                    enhanced_message = f"""基于以下知识库信息回答用户的问题：

知识库内容：
{knowledge_context}

用户问题：
{user_message}"""
                    messages.append({"role": "user", "content": enhanced_message})
                else:
                    messages.append({"role": "user", "content": user_message})
            else:
                messages.append({"role": "user", "content": user_message})
            
            # 使用指定的模型或默认模型
            selected_model = model or self.api_client.model
            
            for chunk in self.api_client._stream_chat_completion(
                f"{self.api_client.base_url}/chat/completions",
                {
                    "model": selected_model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": True
                }
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}")
            yield f"Error: {str(e)}"
    
    def analyze_pet_image(self, image_data: str,
                         analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze pet image (placeholder for future image recognition integration)
        
        Args:
            image_data: Base64 encoded image data or image URL
            analysis_type: Type of analysis (general, health, behavior, breed)
            
        Returns:
            Analysis results dictionary
        """
        try:
            logger.info(f"Analyzing pet image, type: {analysis_type}")
            
            analysis_prompt = f"""请分析这张宠物的图片，提供以下信息：
1. 宠物品种识别
2. 大致年龄估计
3. 健康状况观察
4. 行为特征分析
5. 需要关注的健康要点

请以专业但易懂的方式提供详细分析。"""
            
            system_prompt = self.prompt_manager.get_system_prompt()
            
            response = self.api_client.simple_chat(
                f"{analysis_prompt}\n\n图片数据: {image_data[:100]}...",
                system_prompt
            )
            
            logger.info("Pet image analysis completed")
            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": response.get("content", ""),
                "timestamp": format_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Pet image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def get_pet_advice(self, topic: str,
                      pet_type: Optional[str] = None,
                      specific_issue: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pet care advice
        
        Args:
            topic: Advice topic (diet, health, training, behavior, etc.)
            pet_type: Type of pet (dog, cat, bird, etc.)
            specific_issue: Specific issue or question
            
        Returns:
            Advice dictionary
        """
        try:
            logger.info(f"Getting pet advice, topic: {topic}, pet_type: {pet_type}")
            
            advice_prompt = f"""请提供关于{topic}的专业建议"""
            
            if pet_type:
                advice_prompt += f"，针对{pet_type}"
            
            if specific_issue:
                advice_prompt += f"，具体问题：{specific_issue}"
            
            system_prompt = self.prompt_manager.get_system_prompt()
            
            response = self.api_client.simple_chat(advice_prompt, system_prompt)
            
            logger.info("Pet advice generated successfully")
            return {
                "success": True,
                "topic": topic,
                "pet_type": pet_type,
                "advice": response.get("content", ""),
                "timestamp": format_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Failed to get pet advice: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def emergency_consultation(self, symptoms: str,
                              pet_type: str,
                              severity: str = "medium") -> Dict[str, Any]:
        """
        Emergency consultation for pet health issues
        
        Args:
            symptoms: Pet symptoms description
            pet_type: Type of pet
            severity: Severity level (low, medium, high, critical)
            
        Returns:
            Emergency consultation result
        """
        try:
            logger.warning(f"Emergency consultation - severity: {severity}, pet_type: {pet_type}")
            
            emergency_prompt = f"""紧急情况咨询！

宠物类型：{pet_type}
严重程度：{severity}
症状描述：{symptoms}

请立即提供：
1. 初步判断和建议
2. 紧急处理措施
3. 是否需要立即就医
4. 在送医途中的注意事项

如果情况危急，请明确建议立即就医！"""
            
            system_prompt = self.prompt_manager.get_system_prompt()
            
            response = self.api_client.simple_chat(emergency_prompt, system_prompt, temperature=0.3)
            
            logger.info("Emergency consultation completed")
            return {
                "success": True,
                "severity": severity,
                "pet_type": pet_type,
                "consultation": response.get("content", ""),
                "recommendation": self._extract_recommendation(response.get("content", "")),
                "timestamp": format_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Emergency consultation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def _extract_recommendation(self, content: str) -> str:
        """Extract recommendation from consultation content"""
        if "立即就医" in content or "紧急" in content:
            return "seek_immediate_medical_attention"
        elif "观察" in content or "监测" in content:
            return "monitor_and_observe"
        else:
            return "general_advice"

    def structured_consultation(self,
                              pet_id: int,
                              symptoms: List[str],
                              duration: Optional[str] = None,
                              severity: str = "medium",
                              additional_info: Optional[str] = None,
                              pet_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Structured consultation for pet health issues
        
        Args:
            pet_id: Pet ID
            symptoms: List of symptoms
            duration: Duration of symptoms
            severity: Severity level
            additional_info: Additional information
            pet_context: Pet context information
            
        Returns:
            Consultation result
        """
        try:
            logger.info(f"Structured consultation - pet_id: {pet_id}, symptoms: {symptoms}")

            consultation_prompt = f"""结构化问诊信息：

宠物基本信息："""

            if pet_context:
                consultation_prompt += f"""
- 姓名: {pet_context.get('name', '未知')}
- 品种: {pet_context.get('breed', '未知')}
- 年龄: {pet_context.get('age', '未知')}岁
- 性别: {pet_context.get('gender', '未知')}
- 体重: {pet_context.get('weight', '未知')}kg
- 绝育状态: {'已绝育' if pet_context.get('is_neutered') else '未绝育'}
- 过敏史: {pet_context.get('allergies', '无')}"""

            consultation_prompt += f"""
症状信息：
- 主要症状: {', '.join(symptoms)}
- 发病时长: {duration or '未知'}
- 严重程度: {severity}
- 补充信息: {additional_info or '无'}

请根据以上结构化信息，提供：
1. 专业的医疗建议和初步诊断意见
2. 可能的原因分析
3. 建议的检查项目（如需要）
4. 日常护理建议"""

            system_prompt = self.prompt_manager.get_system_prompt()

            response = self.api_client.simple_chat(consultation_prompt, system_prompt, temperature=0.5)

            logger.info("Structured consultation completed")
            return {
                "success": True,
                "consultation": response.get("content", ""),
                "recommendation": "建议尽快联系宠物医院进行专业诊断",
                "timestamp": format_timestamp()
            }

        except Exception as e:
            logger.error(f"Structured consultation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }

    def knowledge_base_import(self, knowledge_data: Dict[str, Any],
                             category: str = "general") -> Dict[str, Any]:
        """
        Import knowledge into knowledge base
        
        Args:
            knowledge_data: Knowledge data dictionary
            category: Knowledge category
            
        Returns:
            Import result
        """
        try:
            return self.knowledge_base.import_knowledge(knowledge_data, category)
        except KnowledgeBaseException as e:
            logger.error(f"Knowledge base import failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def knowledge_base_query(self, query: str,
                            category: Optional[str] = None,
                            limit: int = 5) -> Dict[str, Any]:
        """
        Query knowledge base
        
        Args:
            query: Search query
            category: Filter by category
            limit: Maximum results
            
        Returns:
            Query results
        """
        try:
            results = self.knowledge_base.query_knowledge(query, category, limit)
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "timestamp": format_timestamp()
            }
        except KnowledgeBaseException as e:
            logger.error(f"Knowledge base query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def knowledge_base_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            return self.knowledge_base.get_statistics()
        except Exception as e:
            logger.error(f"Failed to get knowledge base stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def prompt_management(self, action: str,
                         prompt_name: Optional[str] = None,
                         prompt_content: Optional[str] = None,
                         description: Optional[str] = None) -> Dict[str, Any]:
        """
        Manage system prompts
        
        Args:
            action: Action to perform (get_system, create_custom, list_custom, etc.)
            prompt_name: Prompt name (for custom prompts)
            prompt_content: Prompt content
            description: Prompt description
            
        Returns:
            Action result
        """
        try:
            if action == "get_system":
                return {
                    "success": True,
                    "prompt": self.prompt_manager.get_system_prompt(),
                    "timestamp": format_timestamp()
                }
            
            elif action == "create_custom":
                if not prompt_name or not prompt_content:
                    raise ValueError("prompt_name and prompt_content are required")
                return self.prompt_manager.create_custom_prompt(
                    prompt_name, prompt_content, description or ""
                )
            
            elif action == "list_custom":
                return {
                    "success": True,
                    "prompts": self.prompt_manager.list_custom_prompts(),
                    "timestamp": format_timestamp()
                }
            
            elif action == "get_custom":
                if not prompt_name:
                    raise ValueError("prompt_name is required")
                prompt = self.prompt_manager.get_custom_prompt(prompt_name)
                if prompt:
                    return {
                        "success": True,
                        "prompt": prompt,
                        "timestamp": format_timestamp()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Prompt not found",
                        "timestamp": format_timestamp()
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "timestamp": format_timestamp()
                }
                
        except PromptException as e:
            logger.error(f"Prompt management failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": format_timestamp()
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and capabilities
        
        Returns:
            Service information dictionary
        """
        return {
            "service_name": "PetWise AI Agent Service",
            "version": "1.0.0",
            "description": "AI-powered pet recognition and service system",
            "capabilities": [
                "chat_conversation",
                "streaming_chat",
                "pet_image_analysis",
                "pet_care_advice",
                "emergency_consultation",
                "knowledge_base_management",
                "prompt_management"
            ],
            "api_provider": "SiliconFlow",
            "model": self.api_client.model,
            "endpoints": {
                "health_check": "/health",
                "chat": "/chat",
                "stream_chat": "/stream",
                "image_analysis": "/analyze-image",
                "pet_advice": "/advice",
                "emergency": "/emergency",
                "knowledge_import": "/knowledge/import",
                "knowledge_query": "/knowledge/query",
                "knowledge_stats": "/knowledge/stats",
                "prompt_manage": "/prompts"
            },
            "timestamp": format_timestamp()
        }
    
    def close(self):
        """Close service and cleanup resources"""
        try:
            self.api_client.close()
            logger.info("AI Agent Service closed successfully")
        except Exception as e:
            logger.error(f"Error closing service: {e}")