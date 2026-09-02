path = r'D:\ai-system-s\frontend\src\app\discovery\page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

bad1 = 'className={px-2 py-0.5 rounded text-[10px] font-mono font-bold }'
good1 = 'className=\"px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700\"'

bad2 = 'className={px-2 py-0.5 rounded text-[10px] uppercase font-bold }'
good2 = 'className=\"px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700\"'

text = text.replace(bad1, good1)
text = text.replace(bad2, good2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully cleaned up discovery/page.tsx syntax!')
