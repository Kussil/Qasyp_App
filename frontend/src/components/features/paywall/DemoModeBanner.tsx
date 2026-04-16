export function DemoModeBanner() {
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
  if (!isDemoMode) return null;
  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center">
      <span className="text-sm text-amber-800 font-medium">
        ⚠️ Demo Mode — платежи не требуются / Демо режим
      </span>
    </div>
  );
}
