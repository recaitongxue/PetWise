"""
FastAPI Application for AI Agent Service
Provides RESTful API endpoints for frontend and backend integration
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import io
import time
import uuid

from config import Config
from ai_service import AIAgentService
from utils import setup_logging, format_timestamp
from exceptions import AIAgentException
from cache import get_cache, get_model_cache, init_cache
from structured_logger import setup_structured_logging, get_logger, APILogger, set_request_context, clear_request_context
from error_handlers import setup_error_handlers

setup_structured_logging()
logger = get_logger("api")
api_logger = APILogger()

app = FastAPI(
    title="PetWise AI Agent API",
    description="AI-powered pet recognition and service system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get_cors_origins(),
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

setup_error_handlers(app)

ai_service = None
cache = None
model_cache = None

class ChatRequest(BaseModel):
    user_message: str = Field(..., description="User's message or question")
    use_knowledge_base: bool = Field(True, description="Whether to use knowledge base")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt name (use null or omit for default)")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="AI response temperature")
    model: Optional[str] = Field(None, description="AI model name to use (e.g., deepseek-ai/DeepSeek-V3)")

class ChatResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
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

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware for logging and request tracking"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    set_request_context(request_id)
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        
        api_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        api_logger.log_error(
            method=request.method,
            path=request.url.path,
            error=e
        )
        raise
    finally:
        clear_request_context()

@app.on_event("startup")
async def startup_event():
    """Initialize AI service on startup"""
    global ai_service, cache, model_cache
    
    try:
        init_cache()
        cache = get_cache()
        model_cache = get_model_cache()
        
        ai_service = AIAgentService()
        logger.info("AI Agent API service started successfully")
    except Exception as e:
        logger.error(f"Failed to start AI service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global ai_service, cache
    
    if ai_service:
        logger.info("Shutting down AI Agent API service")

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "PetWise AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    health_status = ai_service.health_check()
    
    cache_stats = cache.get_stats() if cache else {}
    
    return {
        "status": "healthy",
        "service": health_status,
        "cache": cache_stats,
        "timestamp": format_timestamp()
    }

@app.get("/info", tags=["General"])
async def get_info():
    """Get API information"""
    return {
        "name": "PetWise AI Agent API",
        "version": "1.0.0",
        "description": "AI-powered pet recognition and service system",
        "endpoints": {
            "chat": "/v1/chat",
            "stream": "/v1/stream",
            "models": "/v1/models",
            "knowledge_base": "/v1/knowledge/*",
            "prompts": "/v1/prompts/*"
        },
        "features": [
            "Pet recognition",
            "Health consultation",
            "Knowledge base",
            "Multi-model support",
            "Streaming responses"
        ],
        "timestamp": format_timestamp()
    }

@app.get("/v1/models", tags=["Models"])
async def get_models():
    """Get list of available AI models"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        cached_models = model_cache.get_models()
        
        if cached_models:
            logger.info("Returning cached models list")
            return cached_models
        
        logger.info("Fetching models from API")
        models_data = ai_service.api_client.get_available_models()
        
        model_cache.set_models(models_data)
        
        return models_data
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.post("/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint for pet-related queries
    
    - **user_message**: User's question or message
    - **use_knowledge_base**: Whether to search knowledge base
    - **custom_prompt**: Optional custom prompt name (use null or omit for default)
    - **temperature**: AI creativity level (0-2)
    - **model**: Optional AI model name (e.g., "deepseek-ai/DeepSeek-V3")
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    request_id = getattr(http_request.state, "request_id", "")
    
    try:
        response = ai_service.chat(
            user_message=request.user_message,
            use_knowledge_base=request.use_knowledge_base,
            custom_prompt=request.custom_prompt if request.custom_prompt and request.custom_prompt != "string" else None,
            temperature=request.temperature,
            model=request.model if request.model and request.model != "string" else None
        )
        
        if not response.get("success"):
            error_msg = response.get("error", "Unknown error")
            logger.error(f"Chat request failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        return ChatResponse(
            success=True,
            content=response.get("content"),
            usage=response.get("usage"),
            timestamp=response.get("timestamp")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/v1/stream", tags=["Chat"])
async def stream_chat(request: ChatRequest):
    """Streaming chat endpoint"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        async def generate():
            try:
                for chunk in ai_service.stream_chat(
                    user_message=request.user_message,
                    use_knowledge_base=request.use_knowledge_base,
                    custom_prompt=request.custom_prompt if request.custom_prompt and request.custom_prompt != "string" else None,
                    temperature=request.temperature,
                    model=request.model if request.model and request.model != "string" else None
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Stream endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/analyze-image", tags=["Image Analysis"])
async def analyze_image(request: ImageAnalysisRequest):
    """Analyze pet image"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.analyze_image(
            image_data=request.image_data,
            analysis_type=request.analysis_type
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/upload-image", tags=["Image Analysis"])
async def upload_image(file: UploadFile = File(...)):
    """Upload and analyze pet image"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        contents = await file.read()
        import base64
        image_data = base64.b64encode(contents).decode()
        
        result = ai_service.analyze_image(image_data=image_data, analysis_type="general")
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/advice", tags=["Pet Care"])
async def get_pet_advice(request: PetAdviceRequest):
    """Get pet care advice"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.get_pet_advice(
            topic=request.topic,
            pet_type=request.pet_type,
            specific_issue=request.specific_issue
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Pet advice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/emergency", tags=["Emergency"])
async def handle_emergency(request: EmergencyRequest):
    """Handle pet emergency situation"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.handle_emergency(
            symptoms=request.symptoms,
            pet_type=request.pet_type,
            severity=request.severity
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Emergency handling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/knowledge/import", tags=["Knowledge Base"])
async def import_knowledge(request: KnowledgeImportRequest):
    """Import knowledge into knowledge base"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.knowledge_base.import_knowledge(
            knowledge_data=request.knowledge_data,
            category=request.category
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Knowledge import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/knowledge/query", tags=["Knowledge Base"])
async def query_knowledge(request: KnowledgeQueryRequest):
    """Query knowledge base"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        cache_key = f"kb_query:{request.query}:{request.category}:{request.limit}"
        
        if cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for knowledge query: {request.query}")
                return cached_result
        
        results = ai_service.knowledge_base.query_knowledge(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        if cache:
            cache.set(cache_key, results)
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Knowledge query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/knowledge/stats", tags=["Knowledge Base"])
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        cache_key = "kb_stats"
        
        if cache:
            cached_stats = cache.get(cache_key)
            if cached_stats:
                return cached_stats
        
        stats = ai_service.knowledge_base.get_statistics()
        
        if cache:
            cache.set(cache_key, stats, ttl=60)
        
        return stats
        
    except Exception as e:
        logger.error(f"Knowledge stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def get_knowledge_by_id(knowledge_id: str):
    """Get knowledge entry by ID"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        entry = ai_service.knowledge_base.get_knowledge_by_id(knowledge_id)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        
        return {
            "success": True,
            "entry": entry,
            "timestamp": format_timestamp()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/v1/knowledge", tags=["Knowledge Base"])
async def update_knowledge(request: KnowledgeUpdateRequest):
    """Update knowledge entry"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.knowledge_base.update_knowledge(
            knowledge_id=request.knowledge_id,
            new_data=request.knowledge_data
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        if cache:
            cache.clear()
        
        return result
        
    except Exception as e:
        logger.error(f"Knowledge update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/v1/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def delete_knowledge(knowledge_id: str):
    """Delete knowledge entry"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.knowledge_base.delete_knowledge(knowledge_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        if cache:
            cache.clear()
        
        return result
        
    except Exception as e:
        logger.error(f"Knowledge delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/knowledge/categories", tags=["Knowledge Base"])
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

@app.get("/v1/prompts/system", tags=["Prompts"])
async def get_system_prompt():
    """Get system prompt"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        prompt = ai_service.prompt_manager.get_system_prompt()
        
        return {
            "success": True,
            "prompt": prompt,
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Get system prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/prompts/custom", tags=["Prompts"])
async def create_custom_prompt(request: PromptCreateRequest):
    """Create custom prompt"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.prompt_manager.save_custom_prompt(
            name=request.name,
            content=request.content,
            description=request.description
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Create custom prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/prompts/custom", tags=["Prompts"])
async def list_custom_prompts():
    """List all custom prompts"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        prompts = ai_service.prompt_manager.list_custom_prompts()
        
        return {
            "success": True,
            "prompts": prompts,
            "count": len(prompts),
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"List custom prompts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/prompts/custom/{prompt_name}", tags=["Prompts"])
async def get_custom_prompt(prompt_name: str):
    """Get custom prompt by name"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        prompt = ai_service.prompt_manager.get_custom_prompt(prompt_name)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return {
            "success": True,
            "prompt": prompt,
            "timestamp": format_timestamp()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get custom prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/cache/stats", tags=["System"])
async def get_cache_stats():
    """Get cache statistics"""
    if not cache:
        return {"message": "Cache not enabled"}
    
    return cache.get_stats()

@app.post("/v1/cache/clear", tags=["System"])
async def clear_cache():
    """Clear all cache"""
    if not cache:
        return {"message": "Cache not enabled"}
    
    cache.clear()
    model_cache.invalidate_models()
    
    return {"success": True, "message": "Cache cleared"}

def start_server(host: str = None, port: int = None):
    """Start the FastAPI server"""
    uvicorn.run(
        "api:app",
        host=host or Config.API_HOST,
        port=port or Config.API_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    start_server()