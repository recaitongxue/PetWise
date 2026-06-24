"""
FastAPI Application for AI Agent Service
Provides RESTful API endpoints for frontend and backend integration
"""
from fastapi import FastAPI, HTTPException, Request, APIRouter, File, UploadFile
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

v1_router = APIRouter(prefix="/v1", tags=["v1"])

class ChatRequest(BaseModel):
    user_message: str = Field(..., description="User's message or question")
    use_knowledge_base: bool = Field(True, description="Whether to use knowledge base")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt name (use null or omit for default)")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="AI response temperature")
    model: Optional[str] = Field(None, description="AI model name to use (e.g., deepseek-ai/DeepSeek-V3)")
    pet_context: Optional[Dict[str, Any]] = Field(None, description="Pet context information for personalized responses")
    breed_context: Optional[str] = Field(None, description="Breed context for the conversation")
    api_key: Optional[str] = Field(None, description="API key for the AI service")
    base_url: Optional[str] = Field(None, description="Base URL for the AI service")

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

class StructuredConsultationRequest(BaseModel):
    pet_id: int = Field(..., description="Pet ID")
    symptoms: List[str] = Field(..., description="List of symptoms")
    duration: Optional[str] = Field(None, description="Duration of symptoms")
    severity: str = Field("medium", description="Severity level")
    additional_info: Optional[str] = Field(None, description="Additional information")
    pet_context: Optional[Dict[str, Any]] = Field(None, description="Pet context information")

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
    global ai_service, cache
    
    if ai_service:
        logger.info("Shutting down AI Agent API service")

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "PetWise AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/v1"
    }

@app.get("/health", tags=["General"])
async def health_check():
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
    return {
        "name": "PetWise AI Agent API",
        "version": "1.0.0",
        "description": "AI-powered pet recognition and service system",
        "endpoints": {
            "chat": "/v1/chat",
            "stream": "/v1/stream",
            "models": "/v1/models",
            "knowledge_base": "/v1/knowledge/*",
            "prompts": "/v1/prompts/*",
            "cache": "/v1/cache/*"
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

@v1_router.get("/models", tags=["Models"])
async def get_models():
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

@v1_router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, http_request: Request):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    request_id = getattr(http_request.state, "request_id", "")
    
    try:
        response = ai_service.chat(
            user_message=request.user_message,
            use_knowledge_base=request.use_knowledge_base,
            custom_prompt=request.custom_prompt if request.custom_prompt and request.custom_prompt != "string" else None,
            temperature=request.temperature,
            model=request.model if request.model and request.model != "string" else None,
            pet_context=request.pet_context,
            breed_context=request.breed_context,
            api_key=request.api_key,
            base_url=request.base_url
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

@v1_router.post("/stream", tags=["Chat"])
async def stream_chat(request: ChatRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    async def generate():
        try:
            for chunk in ai_service.stream_chat(
                user_message=request.user_message,
                use_knowledge_base=request.use_knowledge_base,
                custom_prompt=request.custom_prompt if request.custom_prompt and request.custom_prompt != "string" else None,
                temperature=request.temperature,
                model=request.model if request.model and request.model != "string" else None,
                api_key=request.api_key,
                base_url=request.base_url
            ):
                yield f"data: {chunk}\n\n"
                import asyncio
                await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: Error: {str(e)}\n\n"
    
    from fastapi.responses import StreamingResponse
    response = StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
    return response

@v1_router.post("/analyze-image", tags=["Image Analysis"])
async def analyze_image(request: ImageAnalysisRequest):
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

@v1_router.post("/upload-image", tags=["Image Analysis"])
async def upload_image(file: UploadFile = File(...)):
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

@v1_router.post("/advice", tags=["Pet Care"])
async def get_pet_advice(request: PetAdviceRequest):
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

@v1_router.post("/emergency", tags=["Emergency"])
async def handle_emergency(request: EmergencyRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.emergency_consultation(
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

@v1_router.post("/structured-consultation", tags=["Structured Consultation"])
async def handle_structured_consultation(request: StructuredConsultationRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.structured_consultation(
            pet_id=request.pet_id,
            symptoms=request.symptoms,
            duration=request.duration,
            severity=request.severity,
            additional_info=request.additional_info,
            pet_context=request.pet_context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Structured consultation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@v1_router.post("/knowledge/import", tags=["Knowledge Base"])
async def import_knowledge(request: KnowledgeImportRequest):
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

@v1_router.post("/knowledge/query", tags=["Knowledge Base"])
async def query_knowledge(request: KnowledgeQueryRequest):
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

@v1_router.get("/knowledge/stats", tags=["Knowledge Base"])
async def get_knowledge_stats():
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

@v1_router.get("/knowledge/list", tags=["Knowledge Base"])
async def get_knowledge_list(
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = ai_service.knowledge_base.get_all_knowledge(
            category=category,
            page=page,
            per_page=per_page
        )
        result["timestamp"] = format_timestamp()
        return result
        
    except Exception as e:
        logger.error(f"Get knowledge list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@v1_router.get("/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def get_knowledge_by_id(knowledge_id: str):
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

@v1_router.put("/knowledge", tags=["Knowledge Base"])
async def update_knowledge(request: KnowledgeUpdateRequest):
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

@v1_router.delete("/knowledge/{knowledge_id}", tags=["Knowledge Base"])
async def delete_knowledge(knowledge_id: str):
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

@v1_router.get("/knowledge/categories", tags=["Knowledge Base"])
async def get_knowledge_categories():
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

@v1_router.post("/knowledge/upload", tags=["Knowledge Base"])
async def upload_knowledge_file(
    file: UploadFile = File(...),
    category: str = "general"
):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        import tempfile
        import os
        
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        
        allowed_extensions = ['.md', '.docx', '.doc', '.pdf', '.txt', '.json']
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Supported formats: {', '.join(allowed_extensions)}")
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix=ext, delete=False) as f:
            contents = await file.read()
            f.write(contents)
            temp_path = f.name
        
        try:
            result = ai_service.knowledge_base.import_from_file(temp_path, category)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("message", "File import failed"))
            
            return {
                "success": True,
                "file_name": file.filename,
                "file_format": ext[1:],
                "category": category,
                "imported": result.get("imported", 0),
                "skipped": result.get("skipped", 0),
                "message": result.get("message", "File uploaded successfully"),
                "timestamp": format_timestamp()
            }
        finally:
            os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@v1_router.get("/knowledge/supported-formats", tags=["Knowledge Base"])
async def get_supported_formats():
    try:
        from file_parser import FileParser
        formats = FileParser.get_supported_formats()
    except ImportError:
        formats = ['.md', '.txt', '.json']
    
    return {
        "success": True,
        "formats": formats,
        "description": {
            ".md": "Markdown文件",
            ".docx": "Word文档(DOCX)",
            ".doc": "Word文档(DOC)",
            ".pdf": "PDF文档",
            ".txt": "纯文本文件",
            ".json": "JSON数据文件"
        },
        "timestamp": format_timestamp()
    }

class EmbeddingConfigRequest(BaseModel):
    api_key: Optional[str] = Field(None, description="API key for embedding service")
    base_url: Optional[str] = Field(None, description="Base URL for embedding service")
    model_name: Optional[str] = Field(None, description="Embedding model name")
    embedding_dim: int = Field(0, description="Expected embedding dimension")

@v1_router.post("/embedding/config", tags=["Embedding"])
async def configure_embedding(request: EmbeddingConfigRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        ai_service.knowledge_base.configure_embedding(
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model_name,
            embedding_dim=request.embedding_dim
        )
        
        return {
            "success": True,
            "message": "Embedding configuration updated",
            "config": {
                "model_name": request.model_name,
                "base_url": request.base_url,
                "embedding_dim": request.embedding_dim
            },
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Configure embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@v1_router.get("/embedding/config", tags=["Embedding"])
async def get_embedding_config():
    if not ai_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        kb = ai_service.knowledge_base
        config = {
            "embedding_available": kb._embedding_client is not None,
            "model_name": kb._embedding_client.model if kb._embedding_client else None,
            "base_url": kb._embedding_client.base_url if kb._embedding_client else None,
            "embedding_dim": kb._embedding_dim
        }
        
        return {
            "success": True,
            "config": config,
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Get embedding config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@v1_router.post("/prompts/system", tags=["Prompts"])
async def get_system_prompt():
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

@v1_router.post("/prompts/custom", tags=["Prompts"])
async def create_custom_prompt(request: PromptCreateRequest):
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

@v1_router.get("/prompts/custom", tags=["Prompts"])
async def list_custom_prompts():
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

@v1_router.get("/prompts/custom/{prompt_name}", tags=["Prompts"])
async def get_custom_prompt(prompt_name: str):
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

@v1_router.get("/cache/stats", tags=["System"])
async def get_cache_stats():
    if not cache:
        return {"message": "Cache not enabled"}
    
    return cache.get_stats()

@v1_router.post("/cache/clear", tags=["System"])
async def clear_cache():
    if not cache:
        return {"message": "Cache not enabled"}
    
    cache.clear()
    model_cache.invalidate_models()
    
    return {"success": True, "message": "Cache cleared"}

app.include_router(v1_router)

def start_server(host: str = None, port: int = None):
    uvicorn.run(
        "api:app",
        host=host or Config.API_HOST,
        port=port or Config.API_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    start_server()
