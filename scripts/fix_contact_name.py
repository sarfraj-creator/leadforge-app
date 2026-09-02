path = r'D:\ai-system-s\backend\app\api\emails.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'contact_name = contact.full_name if contact else \"Business Owner\"'
replacement = 'contact_name = (contact.full_name if (contact and contact.full_name) else None) or getattr(req, \"contact_name\", None) or \"Business Owner\"'

if target in text:
    text = text.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed contact_name NoneType handling in emails.py')
else:
    print('Target not matched.')
