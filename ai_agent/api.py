"""
FastAPI Application for AI Agent Service
Provides RESTful API endpoints for frontend and backend integration
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import io

from config import Config
from ai_service import AIAgentService
from utils import setup_logging, format_timestamp
from exceptions import AIAgentException

logger = setup_logging(Config.LOG_LEVEL)

app = FastAPI(
    title="PetWise AI Agent API",
    description="AI-powered pet recognition and service system API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = None

class ChatRequest(BaseModel):
    user_message: str = Field(..., description="User's message or question")
    use_knowledge_base: bool = Field(True, description="Whether to use knowledge base")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="AI response temperature")
    model: Optional[str] = Field(None, description="AI model name to use")

class ChatResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    timestamp: str

class ImageAnalysisRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data or URL")
    analysis_type: str = Field("general", description="Type of analysis")

class PetAdviceRequest(BaseModel):
    topic: str = Field(..., description="Advice topic")
    pet_type: Optional[str] = Field(None, description="Type of pet")
    specific_issue: Optional[str] = Field(None, description="Specific issue")

class EmergencyRequest(BaseModel):
    symptoms: str = Field(..., description="Pet symptoms description")
    pet_type: str = Field(..., description="Type of pet")
    severity: str = Field("medium", description="Severity level")

class KnowledgeImportRequest(BaseModel):
    knowledge_data: Dict[str, Any] = Field(..., description="Knowledge data")
    category: str = Field("general", description="Knowledge category")

class KnowledgeQueryRequest(BaseModel):
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: int = Field(5, ge=1, le=20, description="Maximum results")

class KnowledgeUpdateRequest(BaseModel):
    knowledge_id: str = Field(..., description="Knowledge entry ID")
    knowledge_data: Dict[str, Any] = Field(..., description="Updated knowledge data")

class KnowledgeDeleteRequest(BaseModel):
    knowledge_id: str = Field(..., description="Knowledge entry ID")

class PromptCreateRequest(BaseModel):
    name: str = Field(..., description="Prompt name")
    content: str = Field(..., description="Prompt content")
    description: Optional[str] = Field("", description="Prompt description")

@app.on_event("startup")
async def startup_event():
    """Initialize AI service on startup"""
    global ai_service
    try:
        ai_service = AIAgentService()
        logger.info("AI Agent API service started successfully")
    except Exception as e:
        logger.error(f"Failed to start AI service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global ai_service
    if ai_service:
        ai_service.close()
        logger.info("AI Agent API service shutdown completed")

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "service": "PetWise AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": format_timestamp()
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    health_status = ai_service.health_check()
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@app.get("/info", tags=["General"])
async def service_info():
    """Get service information and capabilities"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return ai_service.get_service_info()

@app.get("/models", tags=["Models"])
async def get_available_models():
    """Get list of available AI models"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # 硅基流动支持的模型列表（示例）
        models = [
            {
                "name": "deepseek-ai/DeepSeek-V3",
                "description": "DeepSeek-V3大语言模型，适用于通用对话任务",
                "context_window": "128K",
                "recommended": True
            },
            {
                "name": "Qwen/Qwen2-7B-Instruct",
                "description": "Qwen2-7B指令微调模型，性能优秀",
                "context_window": "32K",
                "recommended": False
            },
            {
                "name": "Qwen/Qwen2-14B-Instruct",
                "description": "Qwen2-14B指令微调模型，更强大的推理能力",
                "context_window": "32K",
                "recommended": False
            },
            {
                "name": "Llama-3-8B-Instruct",
                "description": "Meta Llama 3 8B指令模型",
                "context_window": "8K",
                "recommended": False
            },
            {
                "name": "Llama-3-70B-Instruct",
                "description": "Meta Llama 3 70B指令模型，最强性能",
                "context_window": "8K",
                "recommended": False
            }
        ]
        
        return {
            "success": True,
            "models": models,
            "default_model": ai_service.api_client.model,
            "count": len(models),
            "timestamp": format_timestamp()
        }
    except Exception as e:
        logger.error(f"Get models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint for pet-related queries
    
    - **user_message**: User's question or message
    - **use_knowledge_base**: Whether to search knowledge base
    - **custom_prompt**: Optional custom prompt name
    - **temperature**: AI creativity level (0-2)
    - **model**: Optional AI model name to use
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.chat(
            user_message=request.user_message,
            use_knowledge_base=request.use_knowledge_base,
            custom_prompt=request.custom_prompt,
            temperature=request.temperature,
            model=request.model
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return ChatResponse(
            success=True,
            content=response.get("content"),
            usage=response.get("usage"),
            timestamp=response.get("timestamp")
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream", tags=["Chat"])
async def stream_chat(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses
    
    Returns Server-Sent Events (SSE) stream
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    async def generate():
        try:
            for chunk in ai_service.stream_chat(
                user_message=request.user_message,
                use_knowledge_base=request.use_knowledge_base,
                custom_prompt=request.custom_prompt,
                temperature=request.temperature,
                model=request.model
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Stream chat error: {e}")
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/analyze-image", tags=["Image Analysis"])
async def analyze_pet_image(request: ImageAnalysisRequest):
    """
    Analyze pet image
    
    - **image_data**: Base64 encoded image or image URL
    - **analysis_type**: Type of analysis (general, health, behavior, breed)
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.analyze_pet_image(
            image_data=request.image_data,
            analysis_type=request.analysis_type
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-image", tags=["Image Analysis"])
async def upload_and_analyze_image(file: UploadFile = File(...)):
    """
    Upload and analyze pet image
    
    - **file**: Image file to upload
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        contents = await file.read()
        import base64
        image_data = base64.b64encode(contents).decode('utf-8')
        
        response = ai_service.analyze_pet_image(
            image_data=image_data,
            analysis_type="general"
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Image upload analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/advice", tags=["Pet Care"])
async def get_pet_advice(request: PetAdviceRequest):
    """
    Get pet care advice
    
    - **topic**: Advice topic (diet, health, training, behavior, etc.)
    - **pet_type**: Type of pet (dog, cat, bird, etc.)
    - **specific_issue**: Specific issue or question
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.get_pet_advice(
            topic=request.topic,
            pet_type=request.pet_type,
            specific_issue=request.specific_issue
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Pet advice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emergency", tags=["Emergency"])
async def emergency_consultation(request: EmergencyRequest):
    """
    Emergency consultation for pet health issues
    
    - **symptoms**: Pet symptoms description
    - **pet_type**: Type of pet
    - **severity**: Severity level (low, medium, high, critical)
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.emergency_consultation(
            symptoms=request.symptoms,
            pet_type=request.pet_type,
            severity=request.severity
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Emergency consultation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/import", tags=["Knowledge Base"])
async def import_knowledge(request: KnowledgeImportRequest):
    """
    Import knowledge into knowledge base
    
    - **knowledge_data**: Knowledge data dictionary
    - **category**: Knowledge category
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.knowledge_base_import(
            knowledge_data=request.knowledge_data,
            category=request.category
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Knowledge import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/query", tags=["Knowledge Base"])
async def query_knowledge(request: KnowledgeQueryRequest):
    """
    Query knowledge base
    
    - **query**: Search query
    - **category**: Filter by category (optional)
    - **limit**: Maximum number of results
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.knowledge_base_query(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Knowledge query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/stats", tags=["Knowledge Base"])
async def knowledge_base_stats():
    """Get knowledge base statistics"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        return ai_service.knowledge_base_stats()
    except Exception as e:
        logger.error(f"Knowledge stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def get_knowledge_by_id(knowledge_id: str):
    """
    Get knowledge entry by ID
    
    - **knowledge_id**: Knowledge entry ID
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.knowledge_base.get_knowledge_by_id(knowledge_id)
        if result:
            return {
                "success": True,
                "data": result,
                "timestamp": format_timestamp()
            }
        else:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/knowledge", tags=["Knowledge Base"])
async def update_knowledge(request: KnowledgeUpdateRequest):
    """
    Update knowledge entry
    
    - **knowledge_id**: Knowledge entry ID to update
    - **knowledge_data**: New knowledge data
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.knowledge_base.update_knowledge(
            knowledge_id=request.knowledge_id,
            new_data=request.knowledge_data
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def delete_knowledge(knowledge_id: str):
    """
    Delete knowledge entry
    
    - **knowledge_id**: Knowledge entry ID to delete
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.knowledge_base.delete_knowledge(knowledge_id)
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/categories", tags=["Knowledge Base"])
async def get_knowledge_categories():
    """Get all knowledge categories"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        categories = ai_service.knowledge_base.get_all_categories()
        return {
            "success": True,
            "categories": categories,
            "count": len(categories),
            "timestamp": format_timestamp()
        }
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts/system", tags=["Prompts"])
async def get_system_prompt():
    """Get current system prompt"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        return ai_service.prompt_management("get_system")
    except Exception as e:
        logger.error(f"Get system prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompts/custom", tags=["Prompts"])
async def create_custom_prompt(request: PromptCreateRequest):
    """
    Create custom prompt
    
    - **name**: Prompt name
    - **content**: Prompt content
    - **description**: Prompt description
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.prompt_management(
            action="create_custom",
            prompt_name=request.name,
            prompt_content=request.content,
            description=request.description
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
        
    except Exception as e:
        logger.error(f"Create custom prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts/custom", tags=["Prompts"])
async def list_custom_prompts():
    """List all custom prompts"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        return ai_service.prompt_management("list_custom")
    except Exception as e:
        logger.error(f"List custom prompts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts/custom/{prompt_name}", tags=["Prompts"])
async def get_custom_prompt(prompt_name: str):
    """Get specific custom prompt"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = ai_service.prompt_management(
            action="get_custom",
            prompt_name=prompt_name
        )
        
        if not response.get("success"):
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return response
        
    except Exception as e:
        logger.error(f"Get custom prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def start_server(host: str = None, port: int = None):
    """Start the FastAPI server"""
    host = host or Config.API_HOST
    port = port or Config.API_PORT
    
    logger.info(f"Starting AI Agent API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()