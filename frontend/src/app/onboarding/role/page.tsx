"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";

export default function RoleSelectionPage() {
  useRequireAuth();
  const router = useRouter();
  const [selected, setSelected] = useState<"BUYER" | "SUPPLIER" | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleContinue() {
    if (!selected) return;
    setLoading(true);
    setError("");
    try {
      await api.patch("/users/me/role", { role: selected.toLowerCase() });
      router.push(`/onboarding/survey?role=${selected}`);
    } catch {
      setError("Не удалось сохранить роль. Попробуйте ещё раз.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-lg w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Выберите роль</h1>
        <p className="text-gray-500 text-sm mb-6">
          Вы ищете поставщиков или являетесь поставщиком?
        </p>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => setSelected("BUYER")}
            className={`p-6 rounded-lg border-2 text-left transition-colors ${
              selected === "BUYER"
                ? "border-sky-600 bg-sky-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            <div className="text-2xl mb-2">🛒</div>
            <div className="font-semibold text-gray-900">Покупатель</div>
            <div className="text-sm text-gray-500 mt-1">
              Ищу поставщиков товаров и услуг
            </div>
          </button>
          <button
            onClick={() => setSelected("SUPPLIER")}
            className={`p-6 rounded-lg border-2 text-left transition-colors ${
              selected === "SUPPLIER"
                ? "border-sky-600 bg-sky-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            <div className="text-2xl mb-2">🏭</div>
            <div className="font-semibold text-gray-900">Поставщик</div>
            <div className="text-sm text-gray-500 mt-1">
              Предлагаю товары и услуги
            </div>
          </button>
        </div>
        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}
        <Button
          onClick={handleContinue}
          disabled={!selected || loading}
          className="w-full"
          size="lg"
        >
          {loading ? "Сохранение..." : "Продолжить"}
        </Button>
      </div>
    </div>
  );
}
