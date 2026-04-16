interface MatchScoreBadgeProps {
  score: number | null;
}

export function MatchScoreBadge({ score }: MatchScoreBadgeProps) {
  if (score === null) return null;

  const pct = Math.round(score * 100);
  let colorClass = "bg-gray-100 text-gray-600";
  let label = "Potential match";

  if (pct > 80) {
    colorClass = "bg-green-100 text-green-700";
    label = "Excellent match";
  } else if (pct > 60) {
    colorClass = "bg-amber-100 text-amber-700";
    label = "Good match";
  }

  return (
    <div
      className={`inline-flex flex-col items-center justify-center w-14 h-14 rounded-full text-xs font-bold ${colorClass}`}
      title={label}
    >
      <span className="text-base font-bold">{pct}%</span>
    </div>
  );
}
