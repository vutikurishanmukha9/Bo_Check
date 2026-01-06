import { ArrowUp, ArrowDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatCurrency } from "@/data/mockData";

interface TrendComparisonCardProps {
  showName: string;
  currentOccupancy: number;
  previousOccupancy: number;
  currentGross: number;
  previousGross: number;
  delay?: number;
}

const TrendComparisonCard = ({
  showName,
  currentOccupancy,
  previousOccupancy,
  currentGross,
  previousGross,
  delay = 0,
}: TrendComparisonCardProps) => {
  const occupancyChange = currentOccupancy - previousOccupancy;
  const grossChange = ((currentGross - previousGross) / previousGross) * 100;

  const getTrendIcon = (change: number) => {
    if (change > 0) return <ArrowUp className="w-4 h-4" />;
    if (change < 0) return <ArrowDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = (change: number) => {
    if (change > 0) return "text-success";
    if (change < 0) return "text-cinema-red";
    return "text-muted-foreground";
  };

  return (
    <div 
      className="card-gradient rounded-xl border border-border/50 p-4 transition-all duration-300 hover:border-gold/40 animate-fade-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <h4 className="font-semibold text-gold mb-3">{showName}</h4>
      
      <div className="grid grid-cols-2 gap-4">
        {/* Occupancy */}
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Occupancy</p>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold font-mono">{currentOccupancy}%</span>
            <div className={cn("flex items-center gap-0.5 text-sm font-medium", getTrendColor(occupancyChange))}>
              {getTrendIcon(occupancyChange)}
              <span>{Math.abs(occupancyChange)}%</span>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            vs <span className="font-mono">{previousOccupancy}%</span> yesterday
          </p>
        </div>

        {/* Gross */}
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Gross</p>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold font-mono">{formatCurrency(currentGross)}</span>
          </div>
          <div className={cn("flex items-center gap-1 text-xs font-medium", getTrendColor(grossChange))}>
            {getTrendIcon(grossChange)}
            <span>{grossChange >= 0 ? "+" : ""}{grossChange.toFixed(1)}%</span>
            <span className="text-muted-foreground">vs yesterday</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendComparisonCard;
