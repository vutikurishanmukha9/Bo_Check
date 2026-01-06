import { cn } from "@/lib/utils";

interface TicketProgressProps {
  booked: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
  size?: "sm" | "md" | "lg";
}

const TicketProgress = ({ 
  booked, 
  total, 
  label, 
  showPercentage = true,
  size = "md" 
}: TicketProgressProps) => {
  const percentage = (booked / total) * 100;
  const available = total - booked;

  const sizeClasses = {
    sm: "h-2",
    md: "h-3",
    lg: "h-4",
  };

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{label}</span>
          {showPercentage && (
            <span className="font-mono font-medium text-gold">
              {percentage.toFixed(1)}%
            </span>
          )}
        </div>
      )}
      <div className={cn(
        "relative w-full overflow-hidden rounded-full bg-muted",
        sizeClasses[size]
      )}>
        <div 
          className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-gold to-amber transition-all duration-1000 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-success">
          <span className="font-mono font-semibold">{booked.toLocaleString('en-IN')}</span>
          <span className="text-muted-foreground"> booked</span>
        </span>
        <span className="text-muted-foreground">
          <span className="font-mono font-semibold">{available.toLocaleString('en-IN')}</span>
          <span> available</span>
        </span>
      </div>
    </div>
  );
};

export default TicketProgress;
