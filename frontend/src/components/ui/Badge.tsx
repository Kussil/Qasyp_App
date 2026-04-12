import clsx from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "teal" | "green" | "amber" | "gray";
  className?: string;
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        {
          "bg-gray-100 text-gray-800": variant === "default",
          "bg-teal-100 text-teal-800": variant === "teal",
          "bg-green-100 text-green-800": variant === "green",
          "bg-amber-100 text-amber-800": variant === "amber",
          "bg-gray-100 text-gray-500": variant === "gray",
        },
        className
      )}
    >
      {children}
    </span>
  );
}
