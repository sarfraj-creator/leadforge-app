from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import datetime

# --- Auth Schemas ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime.datetime

class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime.datetime

# --- Discovery Schemas ---
class NLPQueryRequest(BaseModel):
    query: str

class DiscoveryJobCreate(BaseModel):
    name: str
    location: str = "WORLDWIDE"
    industry: str = "restaurant"
    keywords: Optional[str] = None
    freshness_days: int = 7
    min_lead_score: int = 60
    max_leads: int = 50
    sources_used: Optional[List[str]] = ["OpenStreetMap"]
    natural_language_query: Optional[str] = None

class DiscoveryJobOut(BaseModel):
    id: int
    organization_id: int
    name: str
    status: str
    location: str
    industry: str
    keywords: Optional[str] = None
    freshness_days: int
    min_lead_score: int
    max_leads: int
    sources_used: str
    natural_language_query: Optional[str] = None
    discovered_count: int = 0
    new_businesses_count: int = 0
    duplicates_count: int = 0
    websites_found_count: int = 0
    websites_reachable_count: int = 0
    websites_verified_count: int = 0
    websites_crawled_count: int = 0
    audits_completed_count: int = 0
    audits_incomplete_count: int = 0
    qualified_leads_count: int = 0
    sales_ready_count: int = 0
    contacts_found_count: int = 0
    verified_emails_count: int = 0
    error_message: Optional[str] = None
    progress_percent: int = 0
    rejection_reasons_json: Optional[str] = None
    geographic_coverage_json: Optional[str] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Company Schemas ---
class LeadSourceRecordOut(BaseModel):
    id: int
    source_name: str
    source_record_id: Optional[str] = None
    source_url: Optional[str] = None
    confidence: Optional[float] = 1.0
    discovered_at: Optional[datetime.datetime] = None
    collected_at: Optional[datetime.datetime] = None

class CompanyOut(BaseModel):
    id: int
    business_name: str
    legal_name: Optional[str]
    industry: str
    category: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    phone: Optional[str]
    business_email: Optional[str]
    website: Optional[str]
    domain: Optional[str]
    source: str
    source_url: Optional[str]
    confidence: float
    discovered_at: datetime.datetime
    last_seen_at: datetime.datetime
    last_checked_at: datetime.datetime
    website_reachable: Optional[bool] = None
    website_official_verified: Optional[bool] = None
    source_records: Optional[List[LeadSourceRecordOut]] = []

# --- Contact Schemas ---
class EmailVerificationOut(BaseModel):
    syntax_valid: bool = True
    domain_valid: bool = True
    mx_valid: bool = True
    mailbox_verified: bool = False
    status: str
    reason: Optional[str]
    confidence: float
    verified_at: datetime.datetime

class ContactOut(BaseModel):
    id: int
    company_id: int
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    is_decision_maker: bool = False
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: str = "Official Website"
    email_status: str = "UNKNOWN"
    email_verified_at: Optional[datetime.datetime] = None
    contact_checked_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    company_id: int
    full_name: str
    job_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_decision_maker: bool = False

# --- Website Audit Schemas ---
class WebsiteMetricOut(BaseModel):
    category: str
    metric_name: str
    value: str
    score: Optional[int]

class WebsiteIssueOut(BaseModel):
    category: str
    title: str
    severity: str
    evidence: str
    recommendation: str

class WebsiteTechOut(BaseModel):
    name: str
    category: str
    version: Optional[str]
    confidence: float

class WebsiteAuditOut(BaseModel):
    id: int
    audit_status: str = "AUDIT_COMPLETE"
    overall_score: int
    performance_score: int
    mobile_score: int
    seo_score: int
    accessibility_score: int
    security_score: int
    ux_score: int
    conversion_score: int
    summary: Optional[str]
    created_at: datetime.datetime
    metrics: List[WebsiteMetricOut] = []
    issues: List[WebsiteIssueOut] = []
    technologies: List[WebsiteTechOut] = []

# --- Lead Schemas ---
class LeadScoreOut(BaseModel):
    total_score: int
    category: str
    data_confidence_score: int = 0
    business_fit_score: int = 0
    opportunity_score: int = 0
    intent_score: int = 0
    buying_intent: str = "UNKNOWN"
    contactability_score: int = 0
    rules_applied: Optional[str]
    explanation: Optional[str]
    calculated_at: datetime.datetime

class LeadOpportunityOut(BaseModel):
    opportunity_type: str
    confidence: float
    observed_evidence: str
    inferred_benefit: str

class LeadOut(BaseModel):
    id: int
    organization_id: int
    company_id: int
    lead_category: Optional[str] = "HAS_WEBSITE_REDESIGN" # HAS_WEBSITE_REDESIGN | NO_WEBSITE_NEW_BUILD | BUYER_INTENT_POST
    pipeline_stage: str = "DISCOVERED"
    is_qualified: bool
    is_sales_ready: bool = False
    needs_review: bool
    is_do_not_contact: bool
    stage: str
    primary_opportunity: Optional[str]
    recommended_service: Optional[str]
    freshness_state: str
    created_at: datetime.datetime
    company: CompanyOut
    score: Optional[LeadScoreOut]
    opportunities: List[LeadOpportunityOut] = []
    contacts: List[ContactOut] = []
    audit: Optional[WebsiteAuditOut] = None

class LeadFilterParams(BaseModel):
    search: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    lead_category: Optional[str] = None # HAS_WEBSITE_REDESIGN | NO_WEBSITE_NEW_BUILD | BUYER_INTENT_POST
    pipeline_stage: Optional[str] = None
    stage: Optional[str] = None
    min_score: Optional[int] = None
    opportunity_type: Optional[str] = None
    freshness: Optional[str] = None # FRESH | RECENT | STALE | NEEDS_RECHECK
    has_email: Optional[bool] = None
    is_qualified: Optional[bool] = None
    is_sales_ready: Optional[bool] = None
    needs_review: Optional[bool] = None
    limit: int = 50
    offset: int = 0

class LeadBulkAction(BaseModel):
    lead_ids: List[int]
    action: str # "add_to_campaign", "change_stage", "mark_dnc", "recheck", "approve", "archive"
    target_stage: Optional[str] = None
    campaign_id: Optional[int] = None

# --- Discovery Schemas ---
class DiscoveryJobCreate(BaseModel):
    name: str
    location: str
    industry: str
    keywords: Optional[str] = None
    freshness_days: int = 7
    min_lead_score: int = 60
    max_leads: int = 50
    sources_used: List[str] = ["OpenStreetMap"]
    natural_language_query: Optional[str] = None

class DiscoveryJobOut(BaseModel):
    id: int
    name: str
    status: str
    location: str
    industry: str
    freshness_days: int
    min_lead_score: int
    max_leads: int
    sources_used: str
    discovered_count: int
    new_businesses_count: int
    duplicates_count: int
    websites_found_count: int
    websites_reachable_count: int = 0
    websites_verified_count: int = 0
    websites_crawled_count: int
    audits_completed_count: int
    audits_incomplete_count: int = 0
    qualified_leads_count: int
    sales_ready_count: int = 0
    contacts_found_count: int
    verified_emails_count: int
    progress_percent: int
    error_message: Optional[str]
    started_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    created_at: datetime.datetime

# --- Source Config Schemas ---
class LeadSourceConfigOut(BaseModel):
    id: int
    name: str
    source_type: str
    is_enabled: bool
    api_key_configured: bool
    status: str
    last_run_at: Optional[datetime.datetime]
    total_discovered: int
    total_new_records: int
    total_duplicates: int
    total_errors: int

class LeadSourceConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    rate_limit_per_min: Optional[int] = None
    config_json: Optional[str] = None

# --- Outreach Schemas ---
class SequenceStepCreate(BaseModel):
    step_number: int
    delay_days: int = 0
    subject_template: str
    body_template: str
    use_ai_personalization: bool = True

class SequenceStepOut(BaseModel):
    id: int
    step_number: int
    delay_days: int
    subject_template: str
    body_template: str
    use_ai_personalization: bool
    is_active: bool

class EmailTemplateCreate(BaseModel):
    name: str
    subject_template: str
    body_template: str
    tone: str = "consultative"

class EmailTemplateOut(BaseModel):
    id: int
    name: str
    subject_template: str
    body_template: str
    tone: str
    created_at: datetime.datetime

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    daily_limit: int = 50
    hourly_limit: int = 10
    approval_mode: str = "MANUAL"
    steps: Optional[List[SequenceStepCreate]] = None
    lead_ids: Optional[List[int]] = []

class CampaignOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    daily_limit: int = 50
    hourly_limit: int = 10
    approval_mode: str = "MANUAL"
    enrolled_leads_count: int = 0
    created_at: datetime.datetime
    sequence_steps: List[SequenceStepOut] = []

class EmailSendRequest(BaseModel):
    lead_id: int
    to_email: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    attach_report: Optional[bool] = True

class AIOutreachGenerateRequest(BaseModel):
    lead_id: int
    tone: Optional[str] = "consultative"
    offering: Optional[str] = "Website Redesign"
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    opportunity_type: Optional[str] = None
    primary_issue: Optional[str] = None
    recommended_service: Optional[str] = None

class AISettingsUpdate(BaseModel):
    active_ai_provider: Optional[str] = "auto"
    ai_search_provider: Optional[str] = "auto"
    
    # Perplexity AI
    perplexity_api_key: Optional[str] = None
    perplexity_model: Optional[str] = "sonar"
    
    # Google Gemini
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = "gemini-2.0-flash"
    
    # Hugging Face Multi-Model Suite
    hf_token: Optional[str] = None
    hf_model: Optional[str] = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_outreach_model: Optional[str] = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_audit_model: Optional[str] = "Qwen/Qwen2.5-Coder-7B-Instruct"
    hf_classification_model: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    hf_extraction_model: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    hf_provider: Optional[str] = "huggingface"
    
    # Model parameters & feature flags
    temperature: float = 0.3
    max_tokens: int = 1024
    enable_ai_analysis: bool = True
    enable_ai_email_gen: bool = True
    enable_ai_reply_classification: bool = True
    enable_ai_search_discovery: bool = True

class SMTPSettingsUpdate(BaseModel):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "prospecting@leadforge.io"
    smtp_from_name: str = "LeadForge Outreach"
    use_tls: bool = True

class SMTPTestRequest(BaseModel):
    test_recipient: Optional[EmailStr] = None

class EmailThreadOut(BaseModel):
    id: int
    lead_id: int
    recipient_email: str
    subject: str
    status: str
    last_message_preview: Optional[str]
    total_messages: int
    latest_event_at: datetime.datetime
    created_at: datetime.datetime

# --- CRM Pipeline Schemas ---
class DealCreate(BaseModel):
    lead_id: int
    deal_title: str
    deal_value: float
    stage: str = "Qualified"
    probability: int = 50
    expected_close_date: Optional[datetime.datetime] = None

class DealOut(BaseModel):
    id: int
    lead_id: int
    deal_title: str
    deal_value: float
    stage: str
    probability: int
    expected_close_date: Optional[datetime.datetime]
    company_name: str
    primary_contact_name: Optional[str]
    created_at: datetime.datetime

class CRMDealOut(DealOut):
    pass

class TaskCreate(BaseModel):
    lead_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None

class TaskOut(BaseModel):
    id: int
    lead_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime.datetime]
    is_completed: bool
    created_at: datetime.datetime

class NoteCreate(BaseModel):
    lead_id: int
    content: str

class NoteOut(BaseModel):
    id: int
    lead_id: int
    content: str
    created_at: datetime.datetime

class ActivityOut(BaseModel):
    id: int
    lead_id: Optional[int]
    activity_type: str
    description: str
    created_at: datetime.datetime

# --- Analytics Schemas ---
class DashboardMetricsOut(BaseModel):
    total_leads: int
    fresh_leads_count: int
    qualified_leads_count: int
    sales_ready_count: int = 0
    hot_leads_count: int
    websites_audited_count: int
    active_campaigns_count: int
    pipeline_value: float
    average_lead_score: float
    website_discovery_rate: float = 0.0
    website_reachable_rate: float = 0.0
    website_verification_rate: float = 0.0
    email_verification_rate: float = 0.0
