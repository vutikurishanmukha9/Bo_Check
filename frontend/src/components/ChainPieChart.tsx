import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { chainData, formatCurrency } from "@/data/mockData";

const ChainPieChart = () => {
  const COLORS = [
    "hsl(45, 90%, 55%)",
    "hsl(35, 100%, 50%)",
    "hsl(25, 90%, 55%)",
    "hsl(15, 85%, 50%)",
    "hsl(5, 80%, 50%)",
    "hsl(220, 15%, 45%)",
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const total = chainData.reduce((sum, item) => sum + item.gross, 0);
      const percentage = ((data.gross / total) * 100).toFixed(1);
      
      return (
        <div className="card-gradient rounded-lg border border-border/50 p-4 shadow-xl">
          <p className="text-lg font-semibold text-gold">{data.name}</p>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-muted-foreground">
              Gross: <span className="font-mono font-medium text-foreground">{formatCurrency(data.gross)}</span>
            </p>
            <p className="text-muted-foreground">
              Share: <span className="font-mono font-medium text-foreground">{percentage}%</span>
            </p>
            <p className="text-muted-foreground">
              Theatres: <span className="font-mono font-medium text-foreground">{data.theatres}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.05) return null;

    return (
      <text 
        x={x} 
        y={y} 
        fill="hsl(var(--background))" 
        textAnchor="middle" 
        dominantBaseline="central"
        className="font-semibold text-sm"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chainData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={100}
            innerRadius={40}
            fill="#8884d8"
            dataKey="gross"
            paddingAngle={2}
          >
            {chainData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            layout="horizontal"
            verticalAlign="bottom"
            align="center"
            formatter={(value) => <span className="text-foreground text-sm">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChainPieChart;
