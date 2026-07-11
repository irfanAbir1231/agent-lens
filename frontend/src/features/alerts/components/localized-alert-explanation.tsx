"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface EvidenceItem {
  label: string;
  value: string;
}

export function LocalizedAlertExplanation({ evidence }: { evidence: EvidenceItem[] }) {
  const [language, setLanguage] = useState<"BN" | "EN">("BN");
  const primary = evidence[0];
  const secondary = evidence[1];

  return (
    <div>
      <div className="mb-5 flex flex-wrap gap-2" aria-label="Alert explanation language">
        <Button variant={language === "BN" ? "secondary" : "outline"} onClick={() => setLanguage("BN")}>বাংলা</Button>
        <Button variant={language === "EN" ? "secondary" : "outline"} onClick={() => setLanguage("EN")}>English</Button>
      </div>
      {language === "BN" ? (
        <div lang="bn" className="grid gap-4 md:grid-cols-2">
          <Explanation title="পরিস্থিতি">সাম্প্রতিক লেনদেনের ধরন এই আউটলেটের স্বাভাবিক কৃত্রিম baseline থেকে আলাদা। তাই বিষয়টি মানুষের পর্যালোচনা প্রয়োজন।</Explanation>
          <Explanation title="প্রমাণ">{primary ? `${primary.label}: ${primary.value}.` : "পরিমাপযোগ্য প্রমাণ সীমিত; আরও তথ্য যাচাই প্রয়োজন।"}{secondary ? ` ${secondary.label}: ${secondary.value}.` : ""}</Explanation>
          <Explanation title="অনিশ্চয়তা">ঈদ, বেতন দিবস, কাছের আউটলেট বন্ধ থাকা, অথবা বিলম্বিত posting এই ধরনের pattern-এর বৈধ কারণ হতে পারে। সিস্টেমটি উদ্দেশ্য নির্ধারণ করতে পারে না।</Explanation>
          <Explanation title="নিরাপদ পরবর্তী পদক্ষেপ">এজেন্টের সঙ্গে প্রত্যাশিত চাহিদা যাচাই করুন, সাম্প্রতিক sequence তুলনা করুন এবং ব্যাখ্যা না পাওয়া গেলে অনুমোদিত risk review-এ পাঠান। কোনো অর্থ স্থানান্তর বা account action স্বয়ংক্রিয়ভাবে করবেন না।</Explanation>
          <p className="md:col-span-2 rounded-md border border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-4 text-sm font-bold text-[var(--color-text-primary)]">এই signal fraud-এর প্রমাণ নয়। বাস্তব কোনো পদক্ষেপের আগে অনুমোদিত human review আবশ্যক।</p>
        </div>
      ) : (
        <div lang="en" className="grid gap-4 md:grid-cols-2">
          <Explanation title="Situation">Recent activity differs from this outlet&apos;s normal synthetic baseline and requires human review.</Explanation>
          <Explanation title="Evidence">{primary ? `${primary.label}: ${primary.value}.` : "Measured evidence is limited and requires verification."}{secondary ? ` ${secondary.label}: ${secondary.value}.` : ""}</Explanation>
          <Explanation title="Uncertainty">Eid, salary-day demand, a nearby outlet closure, or delayed posting may legitimately explain the pattern. The system cannot determine intent.</Explanation>
          <Explanation title="Safe next step">Verify expected demand with the agent, compare the recent sequence, and use authorized risk review only if the pattern remains unexplained. Do not initiate financial or account action.</Explanation>
          <p className="md:col-span-2 rounded-md border border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-4 text-sm font-bold text-[var(--color-text-primary)]">This signal is not proof of fraud. Authorized human review is required before any real-world action.</p>
        </div>
      )}
    </div>
  );
}

function Explanation({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><h3 className="font-semibold text-[var(--color-text-primary)]">{title}</h3><p className="mt-2 text-sm leading-7 text-[var(--color-text-secondary)]">{children}</p></section>;
}
