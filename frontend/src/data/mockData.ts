export interface Theatre {
  id: string;
  name: string;
  city: string;
  state: string;
  totalSeats: number;
  bookedSeats: number;
  grossAmount: number;
}

export interface StateData {
  state: string;
  totalTheatres: number;
  totalTickets: number;
  bookedTickets: number;
  grossAmount: number;
}

export interface CityData {
  city: string;
  state: string;
  theatres: number;
  bookedTickets: number;
  grossAmount: number;
}

export interface ShowTrend {
  showName: string;
  occupancy: number;
  gross: number;
  date: string;
}

export interface DailyTrend {
  date: string;
  day: string;
  occupancy: number;
  gross: number;
  ticketsSold: number;
}

export interface ChainData {
  name: string;
  theatres: number;
  gross: number;
  color: string;
}

export const theatres: Theatre[] = [
  { id: "1", name: "PVR Phoenix", city: "Mumbai", state: "Maharashtra", totalSeats: 450, bookedSeats: 380, grossAmount: 285000 },
  { id: "2", name: "INOX Nariman", city: "Mumbai", state: "Maharashtra", totalSeats: 320, bookedSeats: 290, grossAmount: 217500 },
  { id: "3", name: "Cinepolis Andheri", city: "Mumbai", state: "Maharashtra", totalSeats: 280, bookedSeats: 245, grossAmount: 183750 },
  { id: "4", name: "PVR Orion", city: "Bangalore", state: "Karnataka", totalSeats: 400, bookedSeats: 360, grossAmount: 270000 },
  { id: "5", name: "INOX Forum", city: "Bangalore", state: "Karnataka", totalSeats: 350, bookedSeats: 310, grossAmount: 232500 },
  { id: "6", name: "PVR ECR", city: "Chennai", state: "Tamil Nadu", totalSeats: 380, bookedSeats: 340, grossAmount: 255000 },
  { id: "7", name: "SPI Sathyam", city: "Chennai", state: "Tamil Nadu", totalSeats: 420, bookedSeats: 395, grossAmount: 296250 },
  { id: "8", name: "INOX Quest", city: "Kolkata", state: "West Bengal", totalSeats: 300, bookedSeats: 255, grossAmount: 191250 },
  { id: "9", name: "PVR Select", city: "Delhi", state: "Delhi", totalSeats: 500, bookedSeats: 465, grossAmount: 348750 },
  { id: "10", name: "PVR Plaza", city: "Delhi", state: "Delhi", totalSeats: 280, bookedSeats: 250, grossAmount: 187500 },
  { id: "11", name: "INOX Insignia", city: "Delhi", state: "Delhi", totalSeats: 150, bookedSeats: 145, grossAmount: 145000 },
  { id: "12", name: "Cinepolis DLF", city: "Gurugram", state: "Haryana", totalSeats: 320, bookedSeats: 280, grossAmount: 210000 },
  { id: "13", name: "PVR Elante", city: "Chandigarh", state: "Punjab", totalSeats: 350, bookedSeats: 300, grossAmount: 225000 },
  { id: "14", name: "INOX Crystal", city: "Pune", state: "Maharashtra", totalSeats: 280, bookedSeats: 240, grossAmount: 180000 },
  { id: "15", name: "PVR Icon", city: "Hyderabad", state: "Telangana", totalSeats: 420, bookedSeats: 390, grossAmount: 292500 },
  { id: "16", name: "AMB Cinemas", city: "Hyderabad", state: "Telangana", totalSeats: 380, bookedSeats: 365, grossAmount: 328500 },
  { id: "17", name: "INOX GVK", city: "Hyderabad", state: "Telangana", totalSeats: 300, bookedSeats: 270, grossAmount: 202500 },
  { id: "18", name: "PVR Lulu", city: "Kochi", state: "Kerala", totalSeats: 350, bookedSeats: 310, grossAmount: 232500 },
  { id: "19", name: "Cinepolis Seasons", city: "Pune", state: "Maharashtra", totalSeats: 290, bookedSeats: 260, grossAmount: 195000 },
  { id: "20", name: "PVR Treasure", city: "Ahmedabad", state: "Gujarat", totalSeats: 320, bookedSeats: 275, grossAmount: 206250 },
];

// Show-to-show trends (previous shows vs current)
export const showTrends: ShowTrend[] = [
  { showName: "Morning 9AM", occupancy: 45, gross: 450000, date: "2024-01-06" },
  { showName: "Matinee 12PM", occupancy: 62, gross: 720000, date: "2024-01-06" },
  { showName: "Afternoon 3PM", occupancy: 78, gross: 890000, date: "2024-01-06" },
  { showName: "Evening 6PM", occupancy: 92, gross: 1250000, date: "2024-01-06" },
  { showName: "Night 9PM", occupancy: 88, gross: 1180000, date: "2024-01-06" },
];

export const previousShowTrends: ShowTrend[] = [
  { showName: "Morning 9AM", occupancy: 38, gross: 380000, date: "2024-01-05" },
  { showName: "Matinee 12PM", occupancy: 55, gross: 640000, date: "2024-01-05" },
  { showName: "Afternoon 3PM", occupancy: 72, gross: 820000, date: "2024-01-05" },
  { showName: "Evening 6PM", occupancy: 85, gross: 1100000, date: "2024-01-05" },
  { showName: "Night 9PM", occupancy: 82, gross: 1050000, date: "2024-01-05" },
];

// Day-to-day trends (last 7 days)
export const dailyTrends: DailyTrend[] = [
  { date: "2024-01-01", day: "Mon", occupancy: 58, gross: 2850000, ticketsSold: 3800 },
  { date: "2024-01-02", day: "Tue", occupancy: 52, gross: 2450000, ticketsSold: 3200 },
  { date: "2024-01-03", day: "Wed", occupancy: 48, gross: 2200000, ticketsSold: 2900 },
  { date: "2024-01-04", day: "Thu", occupancy: 55, gross: 2600000, ticketsSold: 3400 },
  { date: "2024-01-05", day: "Fri", occupancy: 75, gross: 3800000, ticketsSold: 4800 },
  { date: "2024-01-06", day: "Sat", occupancy: 88, gross: 4490000, ticketsSold: 5900 },
  { date: "2024-01-07", day: "Sun", occupancy: 92, gross: 4850000, ticketsSold: 6200 },
];

// Chain distribution for pie chart
export const chainData: ChainData[] = [
  { name: "PVR", theatres: 8, gross: 1850000, color: "hsl(45, 90%, 55%)" },
  { name: "INOX", theatres: 6, gross: 1189000, color: "hsl(35, 100%, 50%)" },
  { name: "Cinepolis", theatres: 3, gross: 588750, color: "hsl(25, 90%, 55%)" },
  { name: "SPI", theatres: 1, gross: 296250, color: "hsl(15, 85%, 50%)" },
  { name: "AMB", theatres: 1, gross: 328500, color: "hsl(5, 80%, 50%)" },
  { name: "Others", theatres: 1, gross: 232500, color: "hsl(220, 15%, 45%)" },
];

export const getStateData = (): StateData[] => {
  const stateMap = new Map<string, StateData>();
  
  theatres.forEach(theatre => {
    const existing = stateMap.get(theatre.state);
    if (existing) {
      existing.totalTheatres += 1;
      existing.totalTickets += theatre.totalSeats;
      existing.bookedTickets += theatre.bookedSeats;
      existing.grossAmount += theatre.grossAmount;
    } else {
      stateMap.set(theatre.state, {
        state: theatre.state,
        totalTheatres: 1,
        totalTickets: theatre.totalSeats,
        bookedTickets: theatre.bookedSeats,
        grossAmount: theatre.grossAmount,
      });
    }
  });
  
  return Array.from(stateMap.values()).sort((a, b) => b.grossAmount - a.grossAmount);
};

export const getCityData = (): CityData[] => {
  const cityMap = new Map<string, CityData>();
  
  theatres.forEach(theatre => {
    const key = `${theatre.city}-${theatre.state}`;
    const existing = cityMap.get(key);
    if (existing) {
      existing.theatres += 1;
      existing.bookedTickets += theatre.bookedSeats;
      existing.grossAmount += theatre.grossAmount;
    } else {
      cityMap.set(key, {
        city: theatre.city,
        state: theatre.state,
        theatres: 1,
        bookedTickets: theatre.bookedSeats,
        grossAmount: theatre.grossAmount,
      });
    }
  });
  
  return Array.from(cityMap.values()).sort((a, b) => b.grossAmount - a.grossAmount);
};

export const getTotalStats = () => {
  const totalSeats = theatres.reduce((sum, t) => sum + t.totalSeats, 0);
  const bookedSeats = theatres.reduce((sum, t) => sum + t.bookedSeats, 0);
  const grossAmount = theatres.reduce((sum, t) => sum + t.grossAmount, 0);
  
  return {
    totalTheatres: theatres.length,
    totalSeats,
    bookedSeats,
    availableSeats: totalSeats - bookedSeats,
    occupancyRate: ((bookedSeats / totalSeats) * 100).toFixed(1),
    grossAmount,
  };
};

export const formatCurrency = (amount: number): string => {
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  } else if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} L`;
  } else if (amount >= 1000) {
    return `₹${(amount / 1000).toFixed(1)}K`;
  }
  return `₹${amount.toLocaleString('en-IN')}`;
};

export const formatNumber = (num: number): string => {
  return num.toLocaleString('en-IN');
};

export const getShowComparison = () => {
  return showTrends.map((current, index) => {
    const previous = previousShowTrends[index];
    return {
      showName: current.showName,
      currentOccupancy: current.occupancy,
      previousOccupancy: previous.occupancy,
      occupancyChange: current.occupancy - previous.occupancy,
      currentGross: current.gross,
      previousGross: previous.gross,
      grossChange: ((current.gross - previous.gross) / previous.gross) * 100,
    };
  });
};
