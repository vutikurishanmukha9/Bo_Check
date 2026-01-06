import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { dailyTrends, formatCurrency } from "@/data/mockData";

interface DailyTrendChartProps {
  metric: "occupancy" | "gross";
}

const DailyTrendChart = ({ metric }: DailyTrendChartProps) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="card-gradient rounded-lg border border-border/50 p-4 shadow-xl">
          <p className="text-lg font-semibold text-gold">{label}</p>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-muted-foreground">
              Occupancy: <span className="font-mono font-medium text-foreground">{data.occupancy}%</span>
            </p>
            <p className="text-muted-foreground">
              Gross: <span className="font-mono font-medium text-foreground">{formatCurrency(data.gross)}</span>
            </p>
            <p className="text-muted-foreground">
              Tickets: <span className="font-mono font-medium text-foreground">{data.ticketsSold.toLocaleString('en-IN')}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={dailyTrends} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="day" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
            tickFormatter={(value) => metric === "occupancy" ? `${value}%` : `₹${(value/100000).toFixed(0)}L`}
          />
          <Tooltip content={<CustomTooltip />} />
          {metric === "occupancy" ? (
            <Line 
              type="monotone" 
              dataKey="occupancy" 
              stroke="hsl(var(--gold))" 
              strokeWidth={3}
              dot={{ fill: "hsl(var(--gold))", strokeWidth: 2, r: 5 }}
              activeDot={{ r: 8, fill: "hsl(var(--accent))" }}
            />
          ) : (
            <Line 
              type="monotone" 
              dataKey="gross" 
              stroke="hsl(var(--success))" 
              strokeWidth={3}
              dot={{ fill: "hsl(var(--success))", strokeWidth: 2, r: 5 }}
              activeDot={{ r: 8, fill: "hsl(var(--accent))" }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DailyTrendChart;
