import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from backend.app.core.config import settings
from backend.app.services.ai.factory import ai_factory
from backend.app.services.ai.perplexity import PerplexityProvider
from backend.app.services.ai.gemini import GeminiProvider
from backend.app.services.ai.huggingface import HuggingFaceProvider
from backend.app.schemas.common import AISettingsUpdate, SMTPSettingsUpdate
from backend.app.services.email.sender import email_sender

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/ai")
async def get_ai_settings():
    """Returns AI configuration overview with masked credentials."""
    all_health = await ai_factory.get_all_providers_health()
    return {
        "active_ai_provider": settings.ACTIVE_AI_PROVIDER,
        "ai_search_provider": settings.AI_SEARCH_PROVIDER,
        "active_ai_provider_resolved": all_health["active_ai_provider"],
        "active_search_provider_resolved": all_health["active_search_provider"],
        
        # Perplexity AI
        "perplexity_configured": bool(settings.PERPLEXITY_API_KEY and len(settings.PERPLEXITY_API_KEY) > 5),
        "perplexity_model": settings.PERPLEXITY_MODEL,
        
        # Google Gemini
        "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5),
        "gemini_model": settings.GEMINI_MODEL,
        
        # Hugging Face Multi-Model Suite
        "hf_configured": bool(settings.HF_TOKEN and len(settings.HF_TOKEN) > 5),
        "hf_model": settings.HF_MODEL,
        "hf_outreach_model": settings.HF_OUTREACH_MODEL,
        "hf_audit_model": settings.HF_AUDIT_MODEL,
        "hf_classification_model": settings.HF_CLASSIFICATION_MODEL,
        "hf_extraction_model": settings.HF_EXTRACTION_MODEL,
        "hf_provider": settings.HF_PROVIDER,
        
        # Parameters
        "temperature": settings.AI_TEMPERATURE,
        "max_tokens": settings.AI_MAX_TOKENS,
        "enable_ai_analysis": settings.ENABLE_AI_ANALYSIS,
        "enable_ai_email_gen": settings.ENABLE_AI_EMAIL_GEN,
        "enable_ai_reply_classification": settings.ENABLE_AI_REPLY_CLASSIFICATION,
        "enable_ai_search_discovery": settings.ENABLE_AI_SEARCH_DISCOVERY,
        
        # Provider Health Snapshot
        "provider_health": all_health["providers"]
    }

@router.post("/ai")
async def update_ai_settings(req: AISettingsUpdate):
    """Updates AI inference and search provider configuration."""
    if req.active_ai_provider:
        settings.ACTIVE_AI_PROVIDER = req.active_ai_provider
    if req.ai_search_provider:
        settings.AI_SEARCH_PROVIDER = req.ai_search_provider

    if req.perplexity_api_key is not None and req.perplexity_api_key.strip():
        settings.PERPLEXITY_API_KEY = req.perplexity_api_key.strip()
    if req.perplexity_model:
        settings.PERPLEXITY_MODEL = req.perplexity_model

    if req.gemini_api_key is not None and req.gemini_api_key.strip():
        settings.GEMINI_API_KEY = req.gemini_api_key.strip()
    if req.gemini_model:
        settings.GEMINI_MODEL = req.gemini_model

    if req.hf_token is not None and req.hf_token.strip():
        settings.HF_TOKEN = req.hf_token.strip()
    if req.hf_model:
        settings.HF_MODEL = req.hf_model
    if req.hf_outreach_model:
        settings.HF_OUTREACH_MODEL = req.hf_outreach_model
    if req.hf_audit_model:
        settings.HF_AUDIT_MODEL = req.hf_audit_model
    if req.hf_classification_model:
        settings.HF_CLASSIFICATION_MODEL = req.hf_classification_model
    if req.hf_extraction_model:
        settings.HF_EXTRACTION_MODEL = req.hf_extraction_model
    if req.hf_provider:
        settings.HF_PROVIDER = req.hf_provider

    settings.AI_TEMPERATURE = req.temperature
    settings.AI_MAX_TOKENS = req.max_tokens
    settings.ENABLE_AI_ANALYSIS = req.enable_ai_analysis
    settings.ENABLE_AI_EMAIL_GEN = req.enable_ai_email_gen
    settings.ENABLE_AI_REPLY_CLASSIFICATION = req.enable_ai_reply_classification
    settings.ENABLE_AI_SEARCH_DISCOVERY = req.enable_ai_search_discovery

    # Re-instantiate factory providers with updated keys & models
    ai_factory.perplexity = PerplexityProvider(api_key=settings.PERPLEXITY_API_KEY, model=settings.PERPLEXITY_MODEL)
    ai_factory.gemini = GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    ai_factory.huggingface = HuggingFaceProvider(
        token=settings.HF_TOKEN,
        model=settings.HF_MODEL,
        outreach_model=settings.HF_OUTREACH_MODEL,
        audit_model=settings.HF_AUDIT_MODEL,
        classification_model=settings.HF_CLASSIFICATION_MODEL,
        extraction_model=settings.HF_EXTRACTION_MODEL
    )

    return {"message": "AI multi-model configuration updated successfully."}

@router.post("/ai/test")
async def test_ai_connection(payload: Optional[Dict[str, Any]] = Body(default=None)):
    """Tests live connection for a specific provider or returns all health states."""
    target_provider = (payload or {}).get("provider", "auto").lower()

    if target_provider == "perplexity":
        provider = PerplexityProvider(api_key=settings.PERPLEXITY_API_KEY, model=settings.PERPLEXITY_MODEL)
        return await provider.health_check()
    elif target_provider == "gemini":
        provider = GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
        return await provider.health_check()
    elif target_provider == "huggingface":
        provider = HuggingFaceProvider(token=settings.HF_TOKEN, model=settings.HF_MODEL)
        return await provider.health_check()
    else:
        return await ai_factory.get_all_providers_health()

@router.get("/smtp")
async def get_smtp_settings():
    return {
        "smtp_host": settings.SMTP_HOST or "smtp.gmail.com (Demo mode active)",
        "smtp_port": settings.SMTP_PORT,
        "smtp_from_email": settings.SMTP_FROM_EMAIL,
        "smtp_from_name": settings.SMTP_FROM_NAME,
        "use_tls": settings.SMTP_USE_TLS,
        "is_configured": bool(settings.SMTP_HOST and settings.SMTP_USER)
    }

@router.post("/smtp")
async def update_smtp_settings(req: SMTPSettingsUpdate):
    """Updates SMTP outbound mail configuration."""
    if req.smtp_host is not None:
        settings.SMTP_HOST = req.smtp_host
    if req.smtp_port is not None:
        settings.SMTP_PORT = req.smtp_port
    if req.smtp_user is not None:
        settings.SMTP_USER = req.smtp_user
    if req.smtp_password is not None:
        settings.SMTP_PASSWORD = req.smtp_password
    if req.smtp_from_email is not None:
        settings.SMTP_FROM_EMAIL = req.smtp_from_email
    if req.smtp_from_name is not None:
        settings.SMTP_FROM_NAME = req.smtp_from_name
    settings.SMTP_USE_TLS = req.use_tls

    return {"message": "SMTP configuration updated successfully."}

@router.post("/smtp/test")
async def test_smtp_connection(payload: Optional[Dict[str, Any]] = Body(default=None)):
    data = payload or {}
    success, msg = await email_sender.test_connection(
        host=data.get("smtp_host"),
        port=int(data.get("smtp_port")) if data.get("smtp_port") else None,
        user=data.get("smtp_user"),
        password=data.get("smtp_password"),
        use_tls=data.get("use_tls")
    )
    return {
        "status": "SUCCESS" if success else "ERROR",
        "message": msg
    }
