path = r'D:\ai-system-s\backend\app\api\crm.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'stage_leads = [l for l in leads if l.stage == stage.name]'
replacement = 'stage_leads = [l for l in leads if l.stage == stage.name or (stage.name == \"Qualified\" and l.stage in [\"Qualified\", \"Sales Ready\"])]'

if target in text:
    text = text.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated CRM stage matching for Sales Ready leads')
else:
    print('Target not matched.')
