import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { getShowComparison, formatCurrency } from "@/data/mockData";

const ShowTrendChart = () => {
  const data = getShowComparison();

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const current = payload.find((p: any) => p.dataKey === "currentOccupancy");
      const previous = payload.find((p: any) => p.dataKey === "previousOccupancy");
      const change = current?.value - previous?.value;
      
      return (
        <div className="card-gradient rounded-lg border border-border/50 p-4 shadow-xl">
          <p className="text-lg font-semibold text-gold">{label}</p>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-muted-foreground">
              Today: <span className="font-mono font-medium text-foreground">{current?.value}%</span>
            </p>
            <p className="text-muted-foreground">
              Yesterday: <span className="font-mono font-medium text-foreground">{previous?.value}%</span>
            </p>
            <p className={change >= 0 ? "text-success" : "text-cinema-red"}>
              Change: <span className="font-mono font-medium">{change >= 0 ? "+" : ""}{change}%</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="showName" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'hsl(var(--muted) / 0.3)' }} />
          <Legend 
            wrapperStyle={{ paddingTop: '10px' }}
            formatter={(value) => <span className="text-foreground text-sm">{value === "currentOccupancy" ? "Today" : "Yesterday"}</span>}
          />
          <Bar 
            dataKey="previousOccupancy" 
            fill="hsl(var(--muted-foreground))" 
            radius={[4, 4, 0, 0]}
            name="previousOccupancy"
          />
          <Bar 
            dataKey="currentOccupancy" 
            fill="hsl(var(--gold))" 
            radius={[4, 4, 0, 0]}
            name="currentOccupancy"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ShowTrendChart;
