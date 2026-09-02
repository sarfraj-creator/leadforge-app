path = r'D:\ai-system-s\frontend\src\app\settings\page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''import React, { useState, useEffect } from "react";'''
replacement = '''import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";'''

if target in text and 'useSearchParams' not in text:
    text = text.replace(target, replacement)
    
target2 = '''  const [activeTab, setActiveTab] = useState<"ai" | "smtp" | "scoring" | "sources" | "admin">("ai");'''
replacement2 = '''  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as "ai" | "smtp" | "scoring" | "sources" | "admin" | null;
  const [activeTab, setActiveTab] = useState<"ai" | "smtp" | "scoring" | "sources" | "admin">(tabParam || "ai");

  useEffect(() => {
    if (tabParam && ["ai", "smtp", "scoring", "sources", "admin"].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);'''

if target2 in text:
    text = text.replace(target2, replacement2)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Added useSearchParams support to SettingsPage')
else:
    print('Target 2 not found')
