import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: "default" | "gold" | "success" | "accent";
  className?: string;
  delay?: number;
}

const StatCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  variant = "default",
  className,
  delay = 0
}: StatCardProps) => {
  const variants = {
    default: "border-border/50",
    gold: "border-gold/30 glow",
    success: "border-success/30",
    accent: "border-accent/30",
  };

  const iconVariants = {
    default: "bg-muted text-muted-foreground",
    gold: "bg-gold/10 text-gold",
    success: "bg-success/10 text-success",
    accent: "bg-accent/10 text-accent",
  };

  return (
    <div 
      className={cn(
        "card-gradient rounded-xl border p-6 transition-all duration-300 hover:scale-[1.02] hover:border-gold/40 animate-fade-up",
        variants[variant],
        className
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          )}
          {trend && (
            <div className={cn(
              "inline-flex items-center gap-1 text-sm font-medium",
              trend.isPositive ? "text-success" : "text-cinema-red"
            )}>
              <span>{trend.isPositive ? "↑" : "↓"}</span>
              <span>{Math.abs(trend.value)}%</span>
              <span className="text-muted-foreground">vs yesterday</span>
            </div>
          )}
        </div>
        <div className={cn(
          "rounded-lg p-3",
          iconVariants[variant]
        )}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
