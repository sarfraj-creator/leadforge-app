path = r'D:\ai-system-s\backend\app\schemas\common.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''class AIOutreachGenerateRequest(BaseModel):
    lead_id: int
    tone: Optional[str] = \"consultative\"
    offering: Optional[str] = \"Website Redesign\"'''

replacement = '''class AIOutreachGenerateRequest(BaseModel):
    lead_id: int
    tone: Optional[str] = \"consultative\"
    offering: Optional[str] = \"Website Redesign\"
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    opportunity_type: Optional[str] = None
    primary_issue: Optional[str] = None
    recommended_service: Optional[str] = None'''

if target in text:
    text = text.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully updated schemas/common.py!')
else:
    print('Target not matched exactly.')
