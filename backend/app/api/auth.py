import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token, security_bearer, decode_access_token
from backend.app.models.user import User, Organization, OrganizationMember, OrgRole
from backend.app.schemas.common import UserLogin, UserRegister, Token, UserOut
from backend.app.seed.demo_data import seed_demo_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_current_user(
    token_auth = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not token_auth:
        # Fallback to default user for development ease if no token passed
        stmt = select(User).limit(1)
        res = await db.execute(stmt)
        default_user = res.scalars().first()
        if default_user:
            return default_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing or invalid"
        )
        
    token = token_auth.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    user_id = payload.get("sub")
    stmt = select(User).where(User.id == int(user_id))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user

async def get_current_org(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    stmt = select(OrganizationMember).where(OrganizationMember.user_id == user.id)
    res = await db.execute(stmt)
    membership = res.scalar_one_or_none()
    if membership:
        stmt_org = select(Organization).where(Organization.id == membership.organization_id)
        res_org = await db.execute(stmt_org)
        org = res_org.scalar_one_or_none()
        if org:
            return org
            
    # Default fallback org
    stmt_org = select(Organization).limit(1)
    res_org = await db.execute(stmt_org)
    org = res_org.scalar_one_or_none()
    if org:
        return org
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active organization found")

@router.post("/register", response_model=Token)
async def register(req: UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    org = Organization(
        name=req.organization_name or "My Agency",
        slug=req.organization_name.lower().replace(" ", "-") if req.organization_name else "my-agency"
    )
    db.add(org)
    await db.flush()
    
    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        is_active=True
    )
    db.add(user)
    await db.flush()
    
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=OrgRole.OWNER
    )
    db.add(membership)
    await db.commit()
    
    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "organization_id": org.id,
            "organization_name": org.name,
            "role": "Owner"
        }
    }

@router.post("/login", response_model=Token)
async def login(req: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    stmt_mem = select(OrganizationMember).where(OrganizationMember.user_id == user.id)
    res_mem = await db.execute(stmt_mem)
    membership = res_mem.scalar_one_or_none()
    
    org_id = membership.organization_id if membership else 1
    org_name = "Acme Growth Agency"
    role = membership.role if membership else "Owner"
    
    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "organization_id": org_id,
            "organization_name": org_name,
            "role": str(role)
        }
    }

@router.get("/me")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt_mem = select(OrganizationMember).where(OrganizationMember.user_id == user.id)
    res_mem = await db.execute(stmt_mem)
    membership = res_mem.scalar_one_or_none()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "organization_id": membership.organization_id if membership else 1,
        "role": str(membership.role) if membership else "Owner"
    }

@router.post("/seed-demo")
async def seed_demo_endpoint(db: AsyncSession = Depends(get_db)):
    await seed_demo_data(db)
    return {"message": "Demo data successfully seeded"}
