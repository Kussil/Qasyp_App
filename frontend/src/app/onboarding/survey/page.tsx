"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { INDUSTRIES, REGIONS } from "@/lib/constants";
import type { LegalEntityType, RevenueRange } from "@/types/profile";

const QUALITY_STANDARDS = ["ISO 9001", "ISO 14001", "HACCP", "GOST", "Halal"] as const;

const LEGAL_TYPES: { value: LegalEntityType; label: string }[] = [
  { value: "TOO", label: "ТОО" },
  { value: "IP", label: "ИП" },
  { value: "AO", label: "АО" },
  { value: "GP", label: "ГП" },
  { value: "OTHER", label: "Другое" },
];

const REVENUE_RANGES: { value: RevenueRange; label: string }[] = [
  { value: "BELOW_10M", label: "до 10 млн ₸" },
  { value: "10M_50M", label: "10–50 млн ₸" },
  { value: "50M_200M", label: "50–200 млн ₸" },
  { value: "200M_1B", label: "200 млн – 1 млрд ₸" },
  { value: "ABOVE_1B", label: "свыше 1 млрд ₸" },
  { value: "PREFER_NOT_TO_SAY", label: "Не указывать" },
];

const REGION_LABELS: Record<string, string> = {
  ALMATY_CITY: "Алматы (город)",
  ASTANA_CITY: "Астана (город)",
  SHYMKENT_CITY: "Шымкент (город)",
  ALMATY_REGION: "Алматинская обл.",
  AKMOLA: "Акмолинская обл.",
  AKTOBE: "Актюбинская обл.",
  ATYRAU: "Атырауская обл.",
  EAST_KZ: "Восточно-Казахстанская обл.",
  ZHAMBYL: "Жамбылская обл.",
  WEST_KZ: "Западно-Казахстанская обл.",
  KARAGANDA: "Карагандинская обл.",
  KOSTANAY: "Костанайская обл.",
  KYZYLORDA: "Кызылординская обл.",
  MANGYSTAU: "Мангистауская обл.",
  PAVLODAR: "Павлодарская обл.",
  NORTH_KZ: "Северо-Казахстанская обл.",
  TURKESTAN: "Туркестанская обл.",
  ABAI: "Абайская обл.",
  ZHETYSU: "Жетысуская обл.",
  ULYTAU: "Улытауская обл.",
};

function SurveyForm() {
  useRequireAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const role = (searchParams.get("role") ?? "BUYER") as "BUYER" | "SUPPLIER";

  const [companyName, setCompanyName] = useState("");
  const [bin, setBin] = useState("");
  const [legalType, setLegalType] = useState<LegalEntityType>("TOO");
  const [vatRegistered, setVatRegistered] = useState(false);
  const [vatCertNumber, setVatCertNumber] = useState("");
  const [selectedStandards, setSelectedStandards] = useState<string[]>([]);
  const [industrySector, setIndustrySector] = useState<string>(INDUSTRIES[0]);
  const [businessScope, setBusinessScope] = useState("");
  const [productsServices, setProductsServices] = useState("");
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [willingCrossBorder, setWillingCrossBorder] = useState(false);
  const [revenueRange, setRevenueRange] = useState<RevenueRange>("PREFER_NOT_TO_SAY");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function toggleStandard(s: string) {
    setSelectedStandards((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  }

  function toggleRegion(region: string) {
    setSelectedRegions((prev) =>
      prev.includes(region) ? prev.filter((r) => r !== region) : [...prev, region]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selectedRegions.length === 0) {
      setError("Выберите хотя бы один регион");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await api.post("/survey/submit", {
        company_name: companyName,
        bin,
        legal_entity_type: legalType,
        vat_registered: vatRegistered,
        ...(vatRegistered && vatCertNumber ? { vat_certificate_number: vatCertNumber } : {}),
        industry_sector: industrySector,
        quality_standards: selectedStandards,
        business_scope: businessScope,
        role,
        products_services: productsServices.split(",").map((s) => s.trim()).filter(Boolean),
        operating_regions: selectedRegions,
        willing_cross_border: willingCrossBorder,
        annual_revenue_range: revenueRange,
      });
      router.push("/dashboard");
    } catch {
      setError("Не удалось сохранить анкету. Попробуйте ещё раз.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Анкета компании</h1>
        <p className="text-sm text-gray-500 mb-6">
          Роль: <span className="font-medium">{role === "BUYER" ? "Покупатель" : "Поставщик"}</span>
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Юридические данные
            </h2>
            <div className="flex flex-col gap-4">
              <Input
                label="Название компании"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
                placeholder='ТОО "Пример"'
              />
              <Input
                label="БИН (12 цифр)"
                value={bin}
                onChange={(e) => setBin(e.target.value)}
                required
                pattern="\d{12}"
                title="12 цифр"
                placeholder="123456789012"
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Форма собственности</label>
                <select
                  value={legalType}
                  onChange={(e) => setLegalType(e.target.value as LegalEntityType)}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {LEGAL_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={vatRegistered}
                  onChange={(e) => setVatRegistered(e.target.checked)}
                  className="rounded"
                />
                Плательщик НДС
              </label>
              {vatRegistered && (
                <Input
                  label="Номер НДС свидетельства"
                  value={vatCertNumber}
                  onChange={(e) => setVatCertNumber(e.target.value)}
                  required
                  placeholder="KZ000000000000"
                />
              )}
            </div>
          </section>

          <hr className="border-gray-100" />

          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              О бизнесе
            </h2>
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">Отрасль</label>
                <select
                  value={industrySector}
                  onChange={(e) => setIndustrySector(e.target.value)}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {INDUSTRIES.map((ind) => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">
                  Описание деятельности
                </label>
                <textarea
                  value={businessScope}
                  onChange={(e) => setBusinessScope(e.target.value)}
                  required
                  minLength={20}
                  rows={3}
                  placeholder="Краткое описание чем занимается ваша компания..."
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <Input
                label={role === "BUYER" ? "Что ищете (через запятую)" : "Что предлагаете (через запятую)"}
                value={productsServices}
                onChange={(e) => setProductsServices(e.target.value)}
                required
                placeholder="цемент, арматура, бетон"
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">
                  Стандарты качества{" "}
                  <span className="text-gray-400 font-normal">(необязательно)</span>
                </label>
                <div className="flex flex-wrap gap-3">
                  {QUALITY_STANDARDS.map((s) => (
                    <label key={s} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedStandards.includes(s)}
                        onChange={() => toggleStandard(s)}
                      />
                      {s}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <hr className="border-gray-100" />

          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              География
            </h2>
            <div className="flex flex-col gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-2">
                  Регионы работы{" "}
                  <span className="text-gray-400 font-normal">(выберите один или несколько)</span>
                </label>
                <div className="grid grid-cols-2 gap-1.5 max-h-48 overflow-y-auto border border-gray-200 rounded-md p-3">
                  {REGIONS.map((region) => (
                    <label key={region} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedRegions.includes(region)}
                        onChange={() => toggleRegion(region)}
                      />
                      {REGION_LABELS[region] ?? region}
                    </label>
                  ))}
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={willingCrossBorder}
                  onChange={(e) => setWillingCrossBorder(e.target.checked)}
                />
                Готов работать с компаниями из других стран
              </label>
            </div>
          </section>

          <hr className="border-gray-100" />

          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Финансы
            </h2>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Годовой оборот</label>
              <select
                value={revenueRange}
                onChange={(e) => setRevenueRange(e.target.value as RevenueRange)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {REVENUE_RANGES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
          </section>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={loading} size="lg" className="w-full">
            {loading ? "Сохранение..." : "Найти партнёров →"}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default function SurveyPage() {
  return (
    <Suspense>
      <SurveyForm />
    </Suspense>
  );
}
