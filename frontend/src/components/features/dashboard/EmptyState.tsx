export function EmptyState() {
  return (
    <div className="text-center py-16">
      <div className="text-5xl mb-4">📋</div>
      <h2 className="text-xl font-semibold text-gray-700 mb-2">Совпадений пока нет</h2>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">
        Заполните анкету компании, чтобы увидеть подходящих партнёров
      </p>
      <a
        href="/onboarding/survey"
        className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700"
      >
        Заполнить анкету
      </a>
    </div>
  );
}
