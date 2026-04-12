import clsx from "clsx";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={clsx("rounded-lg bg-white shadow-sm border border-gray-200 p-4", className)}>
      {children}
    </div>
  );
}
