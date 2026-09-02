path = r'D:\ai-system-s\backend\app\api\leads.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

bad = 'elif (comp.business_email or len(await db.scalars(select(Contact.id).where(Contact.company_id == comp.id)).all()) > 0) and score_info[\"contactability_score\"] >= 50:'
good = 'elif (comp.business_email or len((await db.scalars(select(Contact.id).where(Contact.company_id == comp.id))).all()) > 0) and score_info[\"contactability_score\"] >= 50:'

content = content.replace(bad, good)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed parenthesis around await in leads.py')
