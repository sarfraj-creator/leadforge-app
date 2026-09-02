path = r'D:\ai-system-s\backend\app\api\emails.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'opp_type = req.opportunity_type or lead.primary_opportunity or \"Website Redesign\"'
replacement = 'opp_type = getattr(req, \"opportunity_type\", None) or lead.primary_opportunity or \"Website Redesign\"'

text = text.replace(target, replacement)
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated emails.py with getattr fallback.')
