import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.user import Organization, User, OrganizationMember, OrgRole
from backend.app.models.crm import CRMStage
from backend.app.models.discovery import LeadSourceConfig
from backend.app.core.security import get_password_hash

logger = logging.getLogger("leadforge.bootstrap")

async def ensure_bootstrap_defaults(session: AsyncSession):
    """
    Initializes default Organization, Admin User, CRM Stages, and Lead Sources.
    NEVER creates demo leads, mock companies, or sample audits.
    """
    # 1. Organization
    org_res = await session.execute(select(Organization).limit(1))
    org = org_res.scalars().first()
    if not org:
        org = Organization(name="Acme Growth Agency", slug="acme-growth-agency")
        session.add(org)
        await session.flush()
        logger.info("Created default organization: %s", org.name)

    # 2. Admin User
    user_res = await session.execute(select(User).limit(1))
    user = user_res.scalars().first()
    if not user:
        user = User(
            email="admin@leadforge.local",
            hashed_password=get_password_hash("password123"),
            full_name="Alex Mercer",
            is_superuser=True
        )
        session.add(user)
        await session.flush()

        membership = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role=OrgRole.OWNER
        )
        session.add(membership)
        await session.flush()
        logger.info("Created default admin user: %s", user.email)

    # 3. CRM Stages
    stages_res = await session.execute(select(CRMStage).limit(1))
    if not stages_res.scalars().first():
        default_stages = [
            ("New", "#94A3B8", 1),
            ("Qualified", "#3B82F6", 2),
            ("Contacted", "#8B5CF6", 3),
            ("Follow-up", "#F59E0B", 4),
            ("Interested", "#10B981", 5),
            ("Meeting", "#06B6D4", 6),
            ("Proposal", "#EC4899", 7),
            ("Won", "#059669", 8),
            ("Lost", "#EF4444", 9),
        ]
        for name, color, order in default_stages:
            st = CRMStage(
                organization_id=org.id,
                name=name,
                color_code=color,
                order=order,
                is_won_stage=(name == "Won"),
                is_lost_stage=(name == "Lost")
            )
            session.add(st)
        logger.info("Initialized default CRM pipeline stages.")

    # 4. Default Lead Source Configs
    sources_res = await session.execute(select(LeadSourceConfig).limit(1))
    if not sources_res.scalars().first():
        default_sources = [
            ("OpenStreetMap Overpass API", "OpenStreetMap", 30),
            ("Google Maps & Places", "GoogleMaps", 30),
            ("AI Search & Decision Maker Agent", "AISearch", 30),
            ("Social & LinkedIn Intent Hunter", "SocialIntent", 35),
            ("Search Engine Discovery", "SearchEngine", 20),
            ("Public Business Registries", "PublicDirectory", 15),
            ("CSV Dataset Adapter", "CSVImport", 60),
        ]
        for name, stype, rlimit in default_sources:
            cfg = LeadSourceConfig(
                organization_id=org.id,
                name=name,
                source_type=stype,
                is_enabled=True,
                rate_limit_per_min=rlimit
            )
            session.add(cfg)
        logger.info("Initialized default lead source configurations.")

    await session.commit()