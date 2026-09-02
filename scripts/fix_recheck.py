path = r'D:\ai-system-s\backend\app\api\leads.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'elif (comp.business_email or len(comp.contacts) > 0) and score_info[\"contactability_score\"] >= 50:'
replacement = '''contacts_res = await db.execute(select(Contact).where(Contact.company_id == comp.id))
    has_contacts = len(contacts_res.scalars().all()) > 0
    elif (comp.business_email or has_contacts) and score_info[\"contactability_score\"] >= 50:'''

if target in content:
    content = content.replace(target, 'elif (comp.business_email or len(await db.scalars(select(Contact.id).where(Contact.company_id == comp.id)).all()) > 0) and score_info[\"contactability_score\"] >= 50:')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced target with async scalar query.')
else:
    print('Target not directly found, searching...')
