with open(r'D:\ai-system-s\backend\app\api\leads.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))\n            aud_obj = aud_res.scalar_one_or_none()',
    'aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))\n            aud_obj = aud_res.scalars().first()'
)

text = text.replace(
    'aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))\n        aud_obj = aud_res.scalar_one_or_none()',
    'aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))\n        aud_obj = aud_res.scalars().first()'
)

with open(r'D:\ai-system-s\backend\app\api\leads.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open(r'D:\ai-system-s\backend\app\api\emails.py', 'r', encoding='utf-8') as f:
    text_e = f.read()

text_e = text_e.replace(
    'aud_obj = aud_res.scalar_one_or_none()',
    'aud_obj = aud_res.scalars().first()'
)

with open(r'D:\ai-system-s\backend\app\api\emails.py', 'w', encoding='utf-8') as f:
    f.write(text_e)

print('Successfully updated WebsiteAudit queries to .scalars().first()')
