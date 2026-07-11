export function HumanVerificationQuestions({ questions }: { questions: string[] }) {
  return (
    <ul className="space-y-2">
      {questions.map((question) => (
        <li key={question} className="flex gap-3 text-sm leading-6 text-[var(--color-text-primary)]">
          <span className="mt-0.5 shrink-0 rounded border border-[var(--color-border-strong)] px-1.5 py-0.5 text-[10px] font-bold uppercase text-[var(--color-text-muted)]" aria-hidden="true">Q</span>
          <span>{question}</span>
        </li>
      ))}
    </ul>
  );
}
