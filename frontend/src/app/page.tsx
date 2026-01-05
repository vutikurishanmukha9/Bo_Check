"use client";

import { useState, useEffect } from "react";

// Types
interface Movie {
  id: number;
  name: string;
  language: string;
  genres: string[];
  rating: number | null;
  poster_url: string | null;
  duration_mins: number | null;
}

interface City {
  code: string;
  name: string;
}

// Mock data for demo (will be replaced with API calls)
const MOCK_MOVIES: Movie[] = [
  { id: 1, name: "Pushpa 2: The Rule", language: "Telugu", genres: ["Action", "Drama"], rating: 8.5, poster_url: null, duration_mins: 180 },
  { id: 2, name: "Kalki 2898 AD", language: "Telugu", genres: ["Sci-Fi", "Action"], rating: 8.2, poster_url: null, duration_mins: 175 },
  { id: 3, name: "Fighter", language: "Hindi", genres: ["Action", "Thriller"], rating: 7.8, poster_url: null, duration_mins: 160 },
  { id: 4, name: "Dunki", language: "Hindi", genres: ["Comedy", "Drama"], rating: 7.5, poster_url: null, duration_mins: 155 },
  { id: 5, name: "Salaar", language: "Telugu", genres: ["Action"], rating: 8.0, poster_url: null, duration_mins: 175 },
  { id: 6, name: "Animal", language: "Hindi", genres: ["Action", "Drama"], rating: 7.2, poster_url: null, duration_mins: 200 },
];

const CITIES: City[] = [
  { code: "MUM", name: "Mumbai" },
  { code: "DEL", name: "Delhi NCR" },
  { code: "BLR", name: "Bangalore" },
  { code: "HYD", name: "Hyderabad" },
  { code: "CHE", name: "Chennai" },
  { code: "KOL", name: "Kolkata" },
  { code: "PUN", name: "Pune" },
  { code: "AHM", name: "Ahmedabad" },
];

// Stats Component
function StatsCard({ icon, label, value, color }: { icon: string; label: string; value: string; color: string }) {
  return (
    <div className="glass rounded-2xl p-6 card-hover">
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl ${color}`}>
          {icon}
        </div>
        <div>
          <p className="text-slate-400 text-sm">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}

// Movie Card Component
function MovieCard({ movie }: { movie: Movie }) {
  return (
    <div className="glass rounded-2xl overflow-hidden card-hover group">
      {/* Poster Placeholder */}
      <div className="aspect-[2/3] bg-gradient-to-br from-indigo-600 to-purple-700 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-6xl">🎬</span>
        </div>
        {movie.rating && (
          <div className="absolute top-3 right-3 bg-black/70 backdrop-blur px-3 py-1 rounded-full flex items-center gap-1">
            <span className="text-yellow-400">⭐</span>
            <span className="text-white font-medium">{movie.rating}</span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
          <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium transition">
            View Shows
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-white text-lg truncate">{movie.name}</h3>
        <p className="text-slate-400 text-sm mt-1">
          {movie.language} • {movie.genres.slice(0, 2).join(", ")}
        </p>
        {movie.duration_mins && (
          <p className="text-slate-500 text-xs mt-2">
            🕐 {Math.floor(movie.duration_mins / 60)}h {movie.duration_mins % 60}m
          </p>
        )}
      </div>
    </div>
  );
}

// City Card Component
function CityCard({ city, isSelected, onClick }: { city: City; isSelected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-xl transition-all ${isSelected
          ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
          : "glass text-slate-300 hover:bg-slate-700"
        }`}
    >
      <span className="font-medium">{city.name}</span>
    </button>
  );
}

// Main Page Component
export default function Home() {
  const [selectedCity, setSelectedCity] = useState<string>("MUM");
  const [movies, setMovies] = useState<Movie[]>(MOCK_MOVIES);
  const [isLoading, setIsLoading] = useState(false);

  // Simulated loading effect
  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => {
      setMovies(MOCK_MOVIES);
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [selectedCity]);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Movie Booking Stats</span>
            </h1>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Real-time show timings, seat availability, and ticket prices across India&apos;s metropolitan cities
            </p>
          </div>

          {/* City Selector */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {CITIES.map((city) => (
              <CityCard
                key={city.code}
                city={city}
                isSelected={selectedCity === city.code}
                onClick={() => setSelectedCity(city.code)}
              />
            ))}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
            <StatsCard
              icon="🎬"
              label="Movies Showing"
              value="24"
              color="bg-indigo-600/20"
            />
            <StatsCard
              icon="🎭"
              label="Theaters"
              value="156"
              color="bg-purple-600/20"
            />
            <StatsCard
              icon="🎟️"
              label="Shows Today"
              value="1,240"
              color="bg-orange-600/20"
            />
            <StatsCard
              icon="💰"
              label="Avg. Price"
              value="₹350"
              color="bg-green-600/20"
            />
          </div>
        </div>
      </section>

      {/* Movies Section */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-white">
              Now Showing in {CITIES.find(c => c.code === selectedCity)?.name}
            </h2>
            <a href="/movies" className="text-indigo-400 hover:text-indigo-300 flex items-center gap-2">
              View All
              <span>→</span>
            </a>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="glass rounded-2xl overflow-hidden">
                  <div className="aspect-[2/3] bg-slate-700 shimmer"></div>
                  <div className="p-4 space-y-2">
                    <div className="h-5 bg-slate-700 rounded shimmer"></div>
                    <div className="h-4 bg-slate-700 rounded w-2/3 shimmer"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 gradient-text">
            What You Can Do
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 bg-indigo-600/20 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
                🕐
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Show Timings</h3>
              <p className="text-slate-400">
                Find all show timings for any movie across theaters in your city
              </p>
            </div>

            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 bg-orange-600/20 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
                💺
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Seat Availability</h3>
              <p className="text-slate-400">
                Check real-time seat availability and occupancy for any show
              </p>
            </div>

            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 bg-green-600/20 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
                💰
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Price Comparison</h3>
              <p className="text-slate-400">
                Compare ticket prices across different theaters to find the best deals
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-3xl p-12 text-center relative overflow-hidden pulse-glow">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/10 to-purple-600/10"></div>
            <div className="relative z-10">
              <h2 className="text-3xl font-bold mb-4 text-white">
                Ready to explore?
              </h2>
              <p className="text-slate-400 mb-8 max-w-xl mx-auto">
                Search for your favorite movie and find the best show timings and prices in your city.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <input
                  type="text"
                  placeholder="Search for a movie..."
                  className="px-6 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white placeholder:text-slate-500 focus:border-indigo-500 outline-none w-full sm:w-80"
                />
                <button className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition">
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
