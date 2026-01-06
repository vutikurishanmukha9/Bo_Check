import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { StateData, formatCurrency } from "@/data/mockData";

interface StateChartProps {
  data: StateData[];
}

const StateChart = ({ data }: StateChartProps) => {
  const chartData = data.map(item => ({
    ...item,
    grossInLakhs: item.grossAmount / 100000,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as StateData;
      return (
        <div className="card-gradient rounded-lg border border-border/50 p-4 shadow-xl">
          <p className="text-lg font-semibold text-gold">{data.state}</p>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-muted-foreground">
              Gross: <span className="font-mono font-medium text-foreground">{formatCurrency(data.grossAmount)}</span>
            </p>
            <p className="text-muted-foreground">
              Theatres: <span className="font-mono font-medium text-foreground">{data.totalTheatres}</span>
            </p>
            <p className="text-muted-foreground">
              Occupancy: <span className="font-mono font-medium text-success">
                {((data.bookedTickets / data.totalTickets) * 100).toFixed(1)}%
              </span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-[350px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 15% 18%)" />
          <XAxis 
            dataKey="state" 
            stroke="hsl(220 10% 55%)"
            tick={{ fill: "hsl(220 10% 55%)", fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="hsl(220 10% 55%)"
            tick={{ fill: "hsl(220 10% 55%)", fontSize: 12 }}
            tickFormatter={(value) => `₹${value}L`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'hsl(220 15% 15%)' }} />
          <Bar dataKey="grossInLakhs" radius={[6, 6, 0, 0]}>
            {chartData.map((_, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={index === 0 ? "hsl(45 90% 55%)" : `hsl(45 ${70 - index * 5}% ${55 - index * 3}%)`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StateChart;
