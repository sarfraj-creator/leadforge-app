export interface Company {
  id: number;
  business_name: string;
  legal_name?: string;
  industry?: string;
  category?: string;
  description?: string;
  country?: string;
  state?: string;
  city?: string;
  address?: string;
  postal_code?: string;
  phone?: string;
  business_email?: string;
  website?: string;
  domain?: string;
  source: string;
  source_url?: string;
  confidence: number;
  discovered_at: string;
  last_seen_at?: string;
  last_checked_at?: string;
  source_records?: Array<{
    source_name: string;
    source_url?: string;
    confidence: number;
    collected_at: string;
  }>;
  website_reachable?: boolean;
  website_official_verified?: boolean;
}

export interface Contact {
  id: number;
  company_id?: number;
  full_name: string;
  job_title?: string;
  is_decision_maker: boolean;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  email_status: "UNKNOWN" | "VALID" | "INVALID" | "RISKY" | "ROLE_BASED" | string;
  source?: string;
}

export interface WebsiteMetric {
  category: string;
  metric_name: string;
  value: string;
  score?: number;
}

export interface WebsiteIssue {
  category: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  evidence: string;
  recommendation: string;
}

export interface WebsiteTech {
  name: string;
  category: string;
  version?: string;
  confidence: number;
}

export interface WebsiteAudit {
  id: number;
  overall_score: number;
  performance_score: number;
  mobile_score: number;
  seo_score: number;
  accessibility_score: number;
  security_score: number;
  ux_score: number;
  conversion_score: number;
  summary?: string;
  created_at: string;
  metrics?: WebsiteMetric[];
  issues?: WebsiteIssue[];
  technologies?: WebsiteTech[];
}

export interface LeadScore {
  total_score: number;
  category: "HOT" | "HIGH" | "MEDIUM" | "LOW" | string;
  data_confidence_score?: number;
  business_fit_score?: number;
  opportunity_score?: number;
  buying_intent_score?: number;
  buying_intent?: string;
  contactability_score?: number;
  explanation?: string;
  rules_applied?: Array<{ rule: string; points: number; reason: string }>;
}

export interface LeadOpportunity {
  opportunity_type: string;
  confidence: number;
  observed_evidence: string;
  inferred_benefit: string;
}

export interface TechnicalAuditReport {
  report_id: string;
  generated_at: string;
  lead_id: number;
  category: "HAS_WEBSITE_REDESIGN" | "NO_WEBSITE_NEW_BUILD" | "BUYER_INTENT_POST" | string;
  category_label: string;
  company: {
    id: number;
    business_name: string;
    domain: string;
    website: string;
    industry?: string;
    city?: string;
    state?: string;
    country?: string;
    phone?: string;
    business_email?: string;
  };
  contact: {
    name: string;
    title: string;
    email?: string;
    linkedin?: string;
  };
  scores: {
    overall_score: number;
    performance_score: number;
    mobile_score: number;
    seo_score: number;
    accessibility_score: number;
    security_score: number;
    ux_score: number;
    conversion_score: number;
  };
  primary_pitch: string;
  metrics: Array<{
    category: string;
    metric_name: string;
    value: string;
    score?: number;
  }>;
  issues: Array<{
    category: string;
    title: string;
    severity: string;
    evidence: string;
    recommendation: string;
  }>;
  technologies: Array<{
    name: string;
    category: string;
    version?: string;
    confidence: number;
  }>;
  action_plan: Array<{
    phase: string;
    action: string;
    impact: string;
  }>;
  agency_recommendation: {
    service: string;
    estimated_timeline: string;
    projected_roi: string;
  };
}

export interface Lead {
  id: number;
  organization_id: number;
  company_id: number;
  lead_category?: "HAS_WEBSITE_REDESIGN" | "NO_WEBSITE_NEW_BUILD" | "BUYER_INTENT_POST" | string;
  pipeline_stage?: string;
  is_qualified: boolean;
  is_sales_ready?: boolean;
  review_status?: string;
  data_quality_score?: number;
  needs_review: boolean;
  is_do_not_contact: boolean;
  stage: string;
  primary_opportunity?: string;
  recommended_service?: string;
  freshness_state: "FRESH" | "RECENT" | "STALE" | "NEEDS_RECHECK" | string;
  created_at: string;
  company: Company;
  score?: LeadScore;
  opportunities?: LeadOpportunity[];
  contacts?: Contact[];
  audit?: WebsiteAudit;
  activities?: Array<{
    id: number;
    activity_type: string;
    title: string;
    description?: string;
    created_at: string;
  }>;
  tasks?: Array<{
    id: number;
    title: string;
    description?: string;
    task_type: string;
    priority: string;
    status: string;
    due_date?: string;
  }>;
  notes?: Array<{
    id: number;
    content: string;
    created_at: string;
  }>;
}

export interface DiscoveryJob {
  id: number;
  name: string;
  status: "QUEUED" | "RUNNING" | "PAUSED" | "COMPLETED" | "FAILED" | "CANCELLED";
  location: string;
  industry: string;
  freshness_days: number;
  min_lead_score: number;
  max_leads: number;
  sources_used: string;
  discovered_count: number;
  new_businesses_count: number;
  duplicates_count: number;
  websites_found_count: number;
  websites_reachable_count?: number;
  websites_verified_count?: number;
  websites_crawled_count: number;
  audits_completed_count: number;
  audits_incomplete_count?: number;
  qualified_leads_count: number;
  sales_ready_count?: number;
  contacts_found_count: number;
  verified_emails_count: number;
  progress_percent: number;
  error_message?: string;
  rejection_reasons_json?: string;
  geographic_coverage_json?: string;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  status: string;
  daily_limit: number;
  hourly_limit: number;
  approval_mode: string;
  enrolled_leads_count: number;
  created_at: string;
  sequence_steps?: Array<{
    id: number;
    step_number: number;
    delay_days: number;
    subject_template: string;
    body_template: string;
    use_ai_personalization: boolean;
  }>;
}

export interface EmailThread {
  id: number;
  lead_id?: number;
  company_name?: string;
  subject: string;
  recipient_email: string;
  status: string;
  reply_classification?: string;
  reply_sentiment_score?: number;
  last_message_at: string;
  messages: Array<{
    id: number;
    direction: "OUTBOUND" | "INBOUND";
    from_email: string;
    to_email: string;
    subject: string;
    body_text: string;
    status: string;
    sent_at?: string;
  }>;
}

export interface DashboardStats {
  fresh_leads_count: number;
  qualified_leads_count: number;
  hot_leads_count: number;
  websites_audited_count: number;
  emails_sent_count: number;
  replies_count: number;
  positive_replies_count: number;
  meetings_count: number;
  proposals_count: number;
  won_deals_count: number;
  pipeline_value: number;
  recent_activities: Array<{
    id: number;
    activity_type: string;
    title: string;
    description?: string;
    created_at: string;
  }>;
}
