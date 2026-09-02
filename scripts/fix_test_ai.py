path = r'D:\ai-system-s\scripts\test_ai_systems.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(\"dummy_provider = HuggingFaceProvider(api_key='')\", \"dummy_provider = HuggingFaceProvider()\")
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed test_ai_systems.py provider init.')
