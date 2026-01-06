import { CityData, formatCurrency, formatNumber } from "@/data/mockData";
import { MapPin } from "lucide-react";

interface CityBreakdownProps {
  cities: CityData[];
}

const CityBreakdown = ({ cities }: CityBreakdownProps) => {
  const maxGross = Math.max(...cities.map(c => c.grossAmount));

  return (
    <div className="space-y-3">
      {cities.slice(0, 8).map((city, index) => {
        const widthPercent = (city.grossAmount / maxGross) * 100;
        
        return (
          <div 
            key={`${city.city}-${city.state}`} 
            className="group relative animate-fade-up"
            style={{ animationDelay: `${index * 75}ms` }}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gold" />
                <span className="font-medium">{city.city}</span>
                <span className="text-xs text-muted-foreground">({city.state})</span>
              </div>
              <span className="font-mono text-sm font-semibold text-gold">
                {formatCurrency(city.grossAmount)}
              </span>
            </div>
            
            <div className="relative h-8 rounded-lg overflow-hidden bg-muted/50">
              <div 
                className="absolute inset-y-0 left-0 rounded-lg bg-gradient-to-r from-gold/80 to-amber/60 transition-all duration-700 ease-out group-hover:from-gold group-hover:to-amber"
                style={{ width: `${widthPercent}%` }}
              />
              <div className="absolute inset-0 flex items-center px-3 text-xs">
                <span className="font-mono text-primary-foreground font-medium drop-shadow-sm">
                  {formatNumber(city.bookedTickets)} tickets • {city.theatres} theatres
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CityBreakdown;
