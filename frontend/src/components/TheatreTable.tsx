import { Theatre, formatCurrency } from "@/data/mockData";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface TheatreTableProps {
  theatres: Theatre[];
}

const TheatreTable = ({ theatres }: TheatreTableProps) => {
  const getOccupancyBadge = (booked: number, total: number) => {
    const percentage = (booked / total) * 100;
    if (percentage >= 90) {
      return <Badge className="bg-cinema-red/20 text-cinema-red border-cinema-red/30">Housefull</Badge>;
    } else if (percentage >= 75) {
      return <Badge className="bg-success/20 text-success border-success/30">High</Badge>;
    } else if (percentage >= 50) {
      return <Badge className="bg-gold/20 text-gold border-gold/30">Medium</Badge>;
    }
    return <Badge className="bg-muted text-muted-foreground border-border">Low</Badge>;
  };

  return (
    <div className="rounded-xl border border-border/50 card-gradient overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="border-border/50 hover:bg-transparent">
            <TableHead className="text-muted-foreground font-semibold">Theatre</TableHead>
            <TableHead className="text-muted-foreground font-semibold">City</TableHead>
            <TableHead className="text-muted-foreground font-semibold">State</TableHead>
            <TableHead className="text-muted-foreground font-semibold text-center">Tickets</TableHead>
            <TableHead className="text-muted-foreground font-semibold text-center">Status</TableHead>
            <TableHead className="text-muted-foreground font-semibold text-right">Gross</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {theatres.map((theatre, index) => (
            <TableRow 
              key={theatre.id} 
              className="border-border/30 hover:bg-muted/30 transition-colors animate-fade-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <TableCell className="font-medium">{theatre.name}</TableCell>
              <TableCell className="text-muted-foreground">{theatre.city}</TableCell>
              <TableCell className="text-muted-foreground">{theatre.state}</TableCell>
              <TableCell className="text-center">
                <span className="font-mono">
                  <span className="text-success">{theatre.bookedSeats}</span>
                  <span className="text-muted-foreground">/</span>
                  <span>{theatre.totalSeats}</span>
                </span>
              </TableCell>
              <TableCell className="text-center">
                {getOccupancyBadge(theatre.bookedSeats, theatre.totalSeats)}
              </TableCell>
              <TableCell className="text-right font-mono font-medium text-gold">
                {formatCurrency(theatre.grossAmount)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default TheatreTable;
