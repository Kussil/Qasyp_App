export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-6 hidden md:block">
      <div className="text-xl font-bold text-primary-600 mb-8">Qasyp</div>
      <nav className="flex flex-col gap-2">
        <a
          href="/dashboard"
          className="text-sm text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
        >
          Мои совпадения
        </a>
        <a
          href="/onboarding/survey"
          className="text-sm text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
        >
          Анкета
        </a>
      </nav>
    </aside>
  );
}
