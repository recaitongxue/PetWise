"""
Custom Exceptions for AI Agent Module
"""
class AIAgentException(Exception):
    """Base exception for AI Agent"""
    pass

class APIException(AIAgentException):
    """Exception for API related errors"""
    pass

class KnowledgeBaseException(AIAgentException):
    """Exception for knowledge base errors"""
    pass

class PromptException(AIAgentException):
    """Exception for prompt related errors"""
    pass

class ConfigurationException(AIAgentException):
    """Exception for configuration errors"""
    pass

class ValidationException(AIAgentException):
    """Exception for validation errors"""
    pass