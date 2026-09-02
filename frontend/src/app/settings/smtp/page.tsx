"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SMTPSettingsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/settings?tab=smtp");
  }, [router]);

  return (
    <div className="p-8 text-slate-500 text-sm flex items-center justify-center min-h-[400px]">
      Loading SMTP Settings...
    </div>
  );
}
