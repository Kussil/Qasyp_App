export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <span className="text-xl font-bold text-primary-600">Qasyp</span>
        <nav className="flex gap-4 text-sm text-gray-600">
          <a href="/dashboard">Дашборд</a>
        </nav>
      </div>
    </header>
  );
}
