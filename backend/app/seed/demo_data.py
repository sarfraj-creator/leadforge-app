import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, Organization, OrganizationMember, OrgRole
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit, WebsiteAuditMetric, WebsiteIssue, WebsiteTechnology
from backend.app.models.contact import Contact, EmailVerificationRecord
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.campaign import Campaign, SequenceStep, CampaignLead
from backend.app.models.email import EmailThread, EmailMessage, EmailEvent
from backend.app.models.crm import CRMStage, Deal, Task, Activity, Note
from backend.app.models.discovery import LeadSourceConfig

DEMO_TAG = "DEMO DATA"

async def seed_demo_data(session: AsyncSession):
    # Check if demo data exists
    existing = await session.execute(select(User).where(User.email == "demo@leadforge.io"))
    if existing.scalar_one_or_none():
        return

    print("Seeding LeadForge DEMO DATA...")
    
    # 1. Organization & User
    org = Organization(name="Acme Growth Agency", slug="acme-agency")
    session.add(org)
    await session.flush()
    
    user = User(
        email="demo@leadforge.io",
        hashed_password=get_password_hash("password123"),
        full_name="Alex Mercer",
        is_active=True,
        is_superuser=True
    )
    session.add(user)
    await session.flush()
    
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=OrgRole.OWNER
    )
    session.add(member)
    
    # 2. CRM Stages
    default_stages = [
        ("New", 0, "#64748B"),
        ("Qualified", 1, "#3B82F6"),
        ("Contacted", 2, "#8B5CF6"),
        ("Follow-up", 3, "#EC4899"),
        ("Interested", 4, "#F59E0B"),
        ("Meeting", 5, "#10B981"),
        ("Proposal", 6, "#06B6D4"),
        ("Won", 7, "#22C55E"),
        ("Lost", 8, "#EF4444"),
    ]
    for name, order, color in default_stages:
        session.add(CRMStage(
            organization_id=org.id,
            name=name,
            order=order,
            color_code=color,
            is_won_stage=(name == "Won"),
            is_lost_stage=(name == "Lost")
        ))
        
    # 3. Lead Source Configs
    sources = [
        ("OpenStreetMap", "openstreetmap", True, True, "CONNECTED"),
        ("SearchEngine", "search", True, True, "CONNECTED"),
        ("PublicDirectory", "directory", True, False, "CONNECTED"),
        ("CSVImport", "csv", True, False, "CONNECTED"),
    ]
    for s_name, s_type, enabled, api_conf, status in sources:
        session.add(LeadSourceConfig(
            organization_id=org.id,
            name=s_name,
            source_type=s_type,
            is_enabled=enabled,
            api_key_configured=api_conf,
            status=status,
            total_discovered=120,
            total_new_records=95,
            total_duplicates=25
        ))
    await session.flush()

    # 4. Create 20 Companies with realistic audit deficiencies for agencies
    demo_companies_data = [
        ("Grand Bistro Mumbai", "Restaurants", "Mumbai", "https://grandbistromumbai.in", "grandbistromumbai.in", "+91 22 2495 1100", "contact@grandbistromumbai.in", 88, "Mobile Responsive Redesign", "Mobile score is 38/100; site lacks responsive viewport."),
        ("Aura Dental Care", "Healthcare / Dental", "Bangalore", "https://auradentalcare.org", "auradentalcare.org", "+91 80 4112 3344", "info@auradentalcare.org", 92, "Online Appointment Booking Funnel", "No visible booking form or call-to-action on mobile."),
        ("Apex Logistics India", "Logistics", "Delhi", "https://apexlogisticsindia.com", "apexlogisticsindia.com", "+91 11 2875 9900", "sales@apexlogisticsindia.com", 74, "Speed & Performance Tuning", "Page size is 4.8MB and server response time is 3800ms."),
        ("Luxe Living Interiors", "Interior Design", "Mumbai", "https://luxelivinginteriors.in", "luxelivinginteriors.in", "+91 22 2655 4422", "hello@luxelivinginteriors.in", 85, "Visual Portfolio Redesign", "High quality interior photos lack compression; slow page load."),
        ("Zenith Fitness Club", "Health & Fitness", "Bangalore", "https://zenithfitnessclub.com", "zenithfitnessclub.com", "+91 80 2555 8899", "members@zenithfitnessclub.com", 90, "Membership Funnel & CRO", "Missing prominent trial booking button on landing page."),
        ("Precision Tech Tools", "Manufacturing", "Pune", "https://precisiontechtools.co.in", "precisiontechtools.co.in", "+91 20 2712 3300", "inquiry@precisiontechtools.co.in", 68, "Modern CMS Migration", "Legacy PHP 5.6 site with outdated table layout."),
        ("Saffron Spice Kitchen", "Restaurants", "Delhi", "https://saffronspicekitchen.com", "saffronspicekitchen.com", "+91 11 4155 6677", "chef@saffronspicekitchen.com", 82, "Online Food Ordering Integration", "Menu is a static PDF download without online ordering."),
        ("Urban Legal Associates", "Legal Services", "Mumbai", "https://urbanlegalmumbai.com", "urbanlegalmumbai.com", "+91 22 2204 8811", "advocate@urbanlegalmumbai.com", 78, "SEO & Authority Architecture", "Missing H1 tags, empty meta descriptions across all pages."),
        ("Green Leaf Organics", "E-commerce / Retail", "Bangalore", "https://greenleaforganicstore.in", "greenleaforganicstore.in", "+91 80 2344 1122", "orders@greenleaforganicstore.in", 86, "Shopify E-commerce Redesign", "Legacy cart lacks one-click checkout and mobile optimization."),
        ("Skyline Real Estate Advisory", "Real Estate", "Hyderabad", "https://skylinerealtyindia.com", "skylinerealtyindia.com", "+91 40 6677 8899", "contact@skylinerealtyindia.com", 91, "Lead Capture & Property Search", "No interactive property filter or direct WhatsApp inquiry."),
        ("Nova Skin & Wellness Clinic", "Healthcare", "Mumbai", "https://novaskinwellness.in", "novaskinwellness.in", "+91 22 2611 7733", "care@novaskinwellness.in", 84, "Consultation Booking Flow", "Visitors cannot book consultation slots online."),
        ("Summit Financial Advisory", "Financial Services", "Delhi", "https://summitadvisors.in", "summitadvisors.in", "+91 11 2333 4455", "wealth@summitadvisors.in", 72, "Trust Signals & SSL Hardening", "Website has mixed HTTP content warnings."),
        ("Velocity Auto Spares", "Automotive", "Chennai", "https://velocityautospares.in", "velocityautospares.in", "+91 44 2855 6677", "support@velocityautospares.in", 79, "B2B Catalog Modernization", "Static HTML table catalog without search functionality."),
        ("Boutique Studio 9", "Fashion & Apparel", "Bangalore", "https://boutiquestudio9.com", "boutiquestudio9.com", "+91 80 4122 5566", "style@boutiquestudio9.com", 83, "Mobile Lookbook & Checkout", "Desktop layout overflows horizontally on iPhone viewports."),
        ("Cloud Nine Bakery & Cafe", "Food & Beverage", "Pune", "https://cloudninebakerypune.com", "cloudninebakerypune.com", "+91 20 2566 7788", "orders@cloudninebakerypune.com", 87, "Custom Cake Customizer Funnel", "No interactive ordering tool for custom cakes."),
        ("Horizon Architectural Group", "Architecture", "Mumbai", "https://horizonarchitects.in", "horizonarchitects.in", "+91 22 2433 1188", "projects@horizonarchitects.in", 76, "Interactive Project Showcase", "Heavy unoptimized 8K renders causing 6-second page load."),
        ("Pristine Dental Studio", "Healthcare / Dental", "Delhi", "https://pristinedentaldelhi.in", "pristinedentaldelhi.in", "+91 11 2688 9900", "appointments@pristinedentaldelhi.in", 89, "Emergency Dental Booking CTA", "Emergency phone number is not tap-to-call on mobile."),
        ("Elevate HR Solutions", "Staffing & HR", "Hyderabad", "https://elevatehrconsulting.in", "elevatehrconsulting.in", "+91 40 2311 4455", "talent@elevatehrconsulting.in", 65, "Careers Portal & Applicant Tracking", "No candidate submission form or responsive layout."),
        ("Quantum Robotics Labs", "Technology", "Bangalore", "https://quantumroboticslabs.com", "quantumroboticslabs.com", "+91 80 6788 1122", "tech@quantumroboticslabs.com", 70, "Modern Tech Branding & UI", "Generic template with broken social links and placeholder texts."),
        ("Metro Coworking Spaces", "Commercial Real Estate", "Mumbai", "https://metrocoworkmumbai.in", "metrocoworkmumbai.in", "+91 22 2899 3344", "desk@metrocoworkmumbai.in", 94, "Tour Scheduling & Instant Booking", "Missing day-pass checkout and virtual tour embed.")
    ]

    # Insert Companies, Audits, Leads, Contacts
    for i, (b_name, ind, city, web, dom, ph, em, score, opp, issue_text) in enumerate(demo_companies_data):
        comp = Company(
            organization_id=org.id,
            business_name=f"[DEMO] {b_name}",
            industry=ind,
            category=ind.split("/")[0].strip(),
            country="India",
            city=city,
            phone=ph,
            business_email=em,
            website=web,
            domain=dom,
            dedup_hash=f"demo:{dom}",
            source="OpenStreetMap",
            source_url=f"https://www.openstreetmap.org/node/{100000 + i}",
            confidence=0.95,
            discovered_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=i % 4),
            last_seen_at=datetime.datetime.now(datetime.timezone.utc),
            last_checked_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=i * 2)
        )
        session.add(comp)
        await session.flush()
        
        # Source record provenance
        session.add(LeadSourceRecord(
            company_id=comp.id,
            source_name="OpenStreetMap",
            source_url=comp.source_url,
            raw_data=json.dumps({"name": b_name, "city": city, "tag": DEMO_TAG}),
            confidence=0.95
        ))
        
        # Website & Audit
        website_obj = Website(
            company_id=comp.id,
            url=web,
            domain=dom,
            status="WEBSITE_FOUND",
            http_status=200,
            ssl_valid=True,
            html_hash=f"hash-{i}-demo",
            content_hash=f"content-{i}-demo",
            last_crawled_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
            last_audited_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        )
        session.add(website_obj)
        await session.flush()
        
        perf_s = max(35, 95 - (i * 3) % 55)
        mob_s = max(30, 90 - (i * 4) % 60)
        seo_s = max(40, 85 - (i * 2) % 45)
        sec_s = 85
        conv_s = max(25, 80 - (i * 5) % 55)
        overall = int((perf_s + mob_s + seo_s + sec_s + conv_s) / 5)
        
        audit = WebsiteAudit(
            website_id=website_obj.id,
            overall_score=overall,
            performance_score=perf_s,
            mobile_score=mob_s,
            seo_score=seo_s,
            accessibility_score=75,
            security_score=sec_s,
            ux_score=60,
            conversion_score=conv_s,
            summary=f"Technical audit revealed observable opportunities in {opp.lower()}."
        )
        session.add(audit)
        await session.flush()
        
        session.add(WebsiteIssue(
            audit_id=audit.id,
            category="mobile" if mob_s < 60 else "conversion",
            title=f"Observable deficiency: {opp}",
            severity="high" if score >= 85 else "medium",
            evidence=issue_text,
            recommendation=f"Implement {opp} to improve digital client acquisition."
        ))
        
        # Contacts
        contact_name = f"Rajesh {['Sharma', 'Verma', 'Patel', 'Mehta', 'Kapoor', 'Gupta', 'Iyer', 'Reddy'][i % 8]}"
        contact = Contact(
            company_id=comp.id,
            first_name=contact_name.split()[0],
            last_name=contact_name.split()[1],
            full_name=contact_name,
            job_title="Managing Director / Owner",
            is_decision_maker=True,
            email=em,
            phone=ph,
            source="Official Website Team",
            email_status="VALID",
            email_verified_at=datetime.datetime.now(datetime.timezone.utc),
            contact_checked_at=datetime.datetime.now(datetime.timezone.utc)
        )
        session.add(contact)
        await session.flush()
        
        session.add(EmailVerificationRecord(
            contact_id=contact.id,
            email=em,
            status="VALID",
            reason="Confirmed MX mailbox & syntax verified",
            confidence=0.95
        ))
        
        # Lead
        stage_names = ["Qualified", "Contacted", "Follow-up", "Interested", "Meeting", "Proposal", "Won"]
        stage = stage_names[i % len(stage_names)]
        lead = Lead(
            organization_id=org.id,
            company_id=comp.id,
            is_qualified=True,
            needs_review=(i < 3), # 3 leads in review queue
            stage=stage,
            primary_opportunity=opp,
            recommended_service=opp,
            freshness_state="FRESH" if i < 14 else "RECENT",
            assigned_to_user_id=user.id
        )
        session.add(lead)
        await session.flush()
        
        session.add(LeadScore(
            lead_id=lead.id,
            total_score=score,
            category="HOT" if score >= 90 else ("HIGH" if score >= 75 else "MEDIUM"),
            rules_applied=json.dumps([
                {"rule": "Mobile/Performance Deficiencies", "points": 25, "reason": issue_text},
                {"rule": "Valid Business Email Discovered", "points": 10, "reason": em},
                {"rule": "Freshness Verified", "points": 5, "reason": "Discovered within 4 days"}
            ]),
            explanation=f"• Website audit identified: {issue_text}\n• Direct decision maker contact available ({contact_name})\n• High potential for {opp}."
        ))
        
        session.add(LeadOpportunity(
            lead_id=lead.id,
            opportunity_type=opp,
            confidence=0.95,
            observed_evidence=issue_text,
            inferred_benefit=f"Investing in {opp} will substantially improve conversion from mobile search traffic."
        ))
        
        # Activity
        session.add(Activity(
            organization_id=org.id,
            lead_id=lead.id,
            activity_type="DISCOVERY",
            title="Lead Discovered & Qualified",
            description=f"Identified {opp} opportunity with Lead Score {score}/100."
        ))
        
        # Tasks for a few leads
        if i % 3 == 0:
            session.add(Task(
                organization_id=org.id,
                lead_id=lead.id,
                title=f"Schedule Discovery Call with {contact_name}",
                description=f"Walk through mobile audit findings for {comp.business_name}",
                task_type="Call",
                due_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2),
                priority="High" if score >= 90 else "Medium",
                status="Pending",
                assigned_to_user_id=user.id
            ))
            
        # Deals for leads in Meeting/Proposal/Won
        if stage in ["Meeting", "Proposal", "Won"]:
            session.add(Deal(
                organization_id=org.id,
                lead_id=lead.id,
                title=f"{comp.business_name} - {opp}",
                value=2500.0 + (i * 500),
                currency="USD",
                stage=stage,
                expected_close_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14),
                owner_user_id=user.id,
                notes=f"Discussing contract for {opp}."
            ))

    # 5. Create Demo Campaigns & Sequences
    camp = Campaign(
        organization_id=org.id,
        name="[DEMO] High-Value Mumbai & Bangalore Redesigns",
        description="Targeting local businesses with observable mobile and speed deficiencies.",
        status="RUNNING",
        daily_limit=50,
        hourly_limit=10,
        approval_mode="MANUAL"
    )
    session.add(camp)
    await session.flush()
    
    # Sequence Steps
    steps = [
        (1, 0, "Quick question regarding {{company_name}} mobile experience", "Hi {{first_name}},\n\nI was reviewing {{website}} and noticed {{website_issue}}.\n\nWe specialize in {{recommended_service}} for local businesses to increase online inquiries. Would you be open to a 10-minute chat this Thursday?"),
        (2, 3, "Idea for improving {{company_name}} website conversions", "Hi {{first_name}},\n\nFollowing up on my previous note. We created a quick mock-up addressing the mobile navigation on {{website}}.\n\nLet me know if you'd like me to send over the preview link."),
        (3, 7, "Final check-in regarding {{company_name}}", "Hi {{first_name}},\n\nI understand you're busy running {{company_name}}. If improving your online conversions becomes a priority later this quarter, feel free to reach out anytime.")
    ]
    for s_num, d_days, subj, body in steps:
        session.add(SequenceStep(
            campaign_id=camp.id,
            step_number=s_num,
            delay_days=d_days,
            subject_template=subj,
            body_template=body,
            use_ai_personalization=True,
            is_active=True
        ))
        
    # 6. Create Email Threads with realistic AI reply classifications
    thread1 = EmailThread(
        organization_id=org.id,
        subject="Quick question regarding Grand Bistro Mumbai mobile experience",
        recipient_email="contact@grandbistromumbai.in",
        status="REPLIED",
        reply_classification="Interested",
        reply_sentiment_score=0.92
    )
    session.add(thread1)
    await session.flush()
    
    session.add(EmailMessage(
        thread_id=thread1.id,
        direction="OUTBOUND",
        from_email="outreach@leadforge.io",
        to_email="contact@grandbistromumbai.in",
        subject=thread1.subject,
        body_text="Hi Rajesh,\n\nI noticed your mobile website lacks a responsive table reservation flow. We help Mumbai restaurants modernize their booking funnels.",
        status="DELIVERED",
        sent_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
    ))
    
    session.add(EmailMessage(
        thread_id=thread1.id,
        direction="INBOUND",
        from_email="contact@grandbistromumbai.in",
        to_email="outreach@leadforge.io",
        subject="Re: " + thread1.subject,
        body_text="Hi Alex, thanks for pointing this out. We are actually planning to revamp our website next month. Can we set up a call this Friday at 3 PM?",
        status="DELIVERED",
        sent_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)
    ))

    await session.commit()
    print("DEMO DATA successfully seeded!")
