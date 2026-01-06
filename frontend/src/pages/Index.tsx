import { useState, useEffect } from "react";
import { Ticket, Building2, IndianRupee, Users, TrendingUp, Map, BarChart3, Calendar, PieChartIcon, Wifi, WifiOff } from "lucide-react";
import Header from "@/components/Header";
import StatCard from "@/components/StatCard";
import TicketProgress from "@/components/TicketProgress";
import StateChart from "@/components/StateChart";
import TheatreTable from "@/components/TheatreTable";
import CityBreakdown from "@/components/CityBreakdown";
import ShowTrendChart from "@/components/ShowTrendChart";
import DailyTrendChart from "@/components/DailyTrendChart";
import ChainPieChart from "@/components/ChainPieChart";
import TrendComparisonCard from "@/components/TrendComparisonCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useHealth, useStats, useTheaters } from "@/hooks/useApi";
import { theatres, getStateData, getCityData, getTotalStats, formatCurrency, formatNumber, getShowComparison, dailyTrends, type Theatre } from "@/data/mockData";

const Index = () => {
  // Default city for API calls
  const [selectedCity] = useState("MUM");

  // API health check
  const { data: healthData, isLoading: healthLoading, isError: healthError } = useHealth();

  // API data hooks
  const { data: apiStats, isLoading: statsLoading } = useStats(selectedCity);
  const { data: apiTheaters, isLoading: theatersLoading } = useTheaters(selectedCity);

  // Check if backend is connected
  const isBackendConnected = healthData?.status === "healthy";

  // Use API data if available, otherwise fall back to mock data
  const stats = getTotalStats();
  const stateData = getStateData();
  const cityData = getCityData();
  const showComparison = getShowComparison();

  // Merge API theaters with mock data format if available
  const displayTheatres: Theatre[] = apiTheaters && apiTheaters.length > 0
    ? apiTheaters.map((t, i) => ({
      id: String(t.id),
      name: t.name,
      city: "Mumbai", // Would come from API
      state: "Maharashtra",
      totalSeats: 400,
      bookedSeats: 350,
      grossAmount: 250000,
    }))
    : theatres;

  // Calculate day-to-day trend
  const latestDay = dailyTrends[dailyTrends.length - 1];
  const previousDay = dailyTrends[dailyTrends.length - 2];
  const dailyOccupancyChange = latestDay.occupancy - previousDay.occupancy;
  const dailyGrossChange = ((latestDay.gross - previousDay.gross) / previousDay.gross) * 100;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container px-4 py-8 space-y-8">
        {/* API Connection Status */}
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm ${healthLoading ? 'bg-muted/50 text-muted-foreground' :
          isBackendConnected ? 'bg-success/10 text-success' : 'bg-muted/50 text-muted-foreground'
          }`}>
          {healthLoading ? (
            <>
              <div className="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full" />
              <span>Connecting to backend...</span>
            </>
          ) : isBackendConnected ? (
            <>
              <Wifi className="w-4 h-4" />
              <span>Connected to Bo_Check API • Live data enabled</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4" />
              <span>Using demo data • Start backend to see live data</span>
            </>
          )}
        </div>

        {/* Hero Stats */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Gross Collection"
            value={formatCurrency(stats.grossAmount)}
            subtitle="All India Revenue"
            icon={<IndianRupee className="w-6 h-6" />}
            trend={{ value: 12.5, isPositive: true }}
            variant="gold"
            delay={0}
          />
          <StatCard
            title="Tickets Booked"
            value={formatNumber(stats.bookedSeats)}
            subtitle={`${stats.occupancyRate}% occupancy`}
            icon={<Ticket className="w-6 h-6" />}
            trend={{ value: 8.3, isPositive: true }}
            variant="success"
            delay={100}
          />
          <StatCard
            title="Available Tickets"
            value={formatNumber(stats.availableSeats)}
            subtitle="Remaining capacity"
            icon={<Users className="w-6 h-6" />}
            variant="default"
            delay={200}
          />
          <StatCard
            title="Active Theatres"
            value={apiStats?.total_theaters || stats.totalTheatres}
            subtitle={`Across ${stateData.length} states`}
            icon={<Building2 className="w-6 h-6" />}
            variant="accent"
            delay={300}
          />
        </section>

        {/* Ticket Progress Overview */}
        <section className="card-gradient rounded-xl border border-border/50 p-6 animate-fade-up" style={{ animationDelay: "400ms" }}>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-5 h-5 text-gold" />
            <h2 className="text-lg font-semibold">Ticket Sales Overview</h2>
          </div>
          <TicketProgress
            booked={stats.bookedSeats}
            total={stats.totalSeats}
            label="All India Occupancy"
            size="lg"
          />
        </section>

        {/* Show-to-Show Trend Comparison */}
        <section className="animate-fade-up" style={{ animationDelay: "450ms" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">Show-to-Show Comparison</h2>
            </div>
            <span className="text-sm text-muted-foreground">Today vs Yesterday</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
            {showComparison.map((show, index) => (
              <TrendComparisonCard
                key={show.showName}
                showName={show.showName}
                currentOccupancy={show.currentOccupancy}
                previousOccupancy={show.previousOccupancy}
                currentGross={show.currentGross}
                previousGross={show.previousGross}
                delay={index * 50}
              />
            ))}
          </div>

          <div className="card-gradient rounded-xl border border-border/50 p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-4">Occupancy Trend by Show</h3>
            <ShowTrendChart />
          </div>
        </section>

        {/* Day-to-Day Trends */}
        <section className="animate-fade-up" style={{ animationDelay: "500ms" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">Day-to-Day Trends</h2>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <span className={dailyOccupancyChange >= 0 ? "text-success" : "text-cinema-red"}>
                Occupancy: {dailyOccupancyChange >= 0 ? "+" : ""}{dailyOccupancyChange}%
              </span>
              <span className={dailyGrossChange >= 0 ? "text-success" : "text-cinema-red"}>
                Gross: {dailyGrossChange >= 0 ? "+" : ""}{dailyGrossChange.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="card-gradient rounded-xl border border-border/50 p-6">
            <Tabs defaultValue="occupancy" className="w-full">
              <TabsList className="mb-4 bg-muted/50">
                <TabsTrigger value="occupancy">Occupancy Trend</TabsTrigger>
                <TabsTrigger value="gross">Gross Collection</TabsTrigger>
              </TabsList>
              <TabsContent value="occupancy">
                <DailyTrendChart metric="occupancy" />
              </TabsContent>
              <TabsContent value="gross">
                <DailyTrendChart metric="gross" />
              </TabsContent>
            </Tabs>
          </div>
        </section>

        {/* Charts Row - Pie Chart + State Chart */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chain Distribution Pie Chart */}
          <div className="card-gradient rounded-xl border border-border/50 p-6 animate-fade-up" style={{ animationDelay: "550ms" }}>
            <div className="flex items-center gap-2 mb-4">
              <PieChartIcon className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">Chain-wise Distribution</h2>
            </div>
            <ChainPieChart />
          </div>

          {/* State-wise Chart */}
          <div className="card-gradient rounded-xl border border-border/50 p-6 animate-fade-up" style={{ animationDelay: "600ms" }}>
            <div className="flex items-center gap-2 mb-4">
              <Map className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">Gross by State</h2>
            </div>
            <StateChart data={stateData} />
          </div>
        </section>

        {/* City Breakdown */}
        <section className="card-gradient rounded-xl border border-border/50 p-6 animate-fade-up" style={{ animationDelay: "650ms" }}>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">City Performance</h2>
            </div>
            <span className="text-xs text-muted-foreground">Top 8 cities</span>
          </div>
          <CityBreakdown cities={cityData} />
        </section>

        {/* Theatre Table */}
        <section className="animate-fade-up" style={{ animationDelay: "700ms" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Ticket className="w-5 h-5 text-gold" />
              <h2 className="text-lg font-semibold">Theatre-wise Collection</h2>
            </div>
            <span className="text-sm text-muted-foreground">{displayTheatres.length} theatres</span>
          </div>
          <TheatreTable theatres={displayTheatres} />
        </section>

        {/* Footer */}
        <footer className="pt-8 pb-4 text-center text-sm text-muted-foreground border-t border-border/30">
          <p>Bo_Analytics Dashboard • Real-time Box Office Tracking for India</p>
        </footer>
      </main>
    </div>
  );
};

export default Index;
