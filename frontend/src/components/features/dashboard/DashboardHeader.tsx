import { Badge } from "@/components/ui/Badge";

interface DashboardHeaderProps {
  userEmail?: string;
  role?: string | null;
}

export function DashboardHeader({ userEmail, role }: DashboardHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Мои совпадения</h1>
        {userEmail && <p className="text-sm text-gray-500 mt-1">{userEmail}</p>}
      </div>
      {role && (
        <Badge variant={role.toUpperCase() === "BUYER" ? "teal" : "green"}>
          {role.toUpperCase() === "BUYER" ? "Покупатель" : "Поставщик"}
        </Badge>
      )}
    </div>
  );
}
