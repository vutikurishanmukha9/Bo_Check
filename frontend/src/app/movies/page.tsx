"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

// Types
interface Movie {
    id: number;
    name: string;
    language: string;
    genres: string[];
    rating: number | null;
    poster_url: string | null;
    duration_mins: number | null;
    certification: string | null;
}

// Mock data
const MOCK_MOVIES: Movie[] = [
    { id: 1, name: "Pushpa 2: The Rule", language: "Telugu", genres: ["Action", "Drama"], rating: 8.5, poster_url: null, duration_mins: 180, certification: "UA" },
    { id: 2, name: "Kalki 2898 AD", language: "Telugu", genres: ["Sci-Fi", "Action"], rating: 8.2, poster_url: null, duration_mins: 175, certification: "UA" },
    { id: 3, name: "Fighter", language: "Hindi", genres: ["Action", "Thriller"], rating: 7.8, poster_url: null, duration_mins: 160, certification: "UA" },
    { id: 4, name: "Dunki", language: "Hindi", genres: ["Comedy", "Drama"], rating: 7.5, poster_url: null, duration_mins: 155, certification: "U" },
    { id: 5, name: "Salaar", language: "Telugu", genres: ["Action"], rating: 8.0, poster_url: null, duration_mins: 175, certification: "A" },
    { id: 6, name: "Animal", language: "Hindi", genres: ["Action", "Drama"], rating: 7.2, poster_url: null, duration_mins: 200, certification: "A" },
    { id: 7, name: "Jawan", language: "Hindi", genres: ["Action", "Thriller"], rating: 8.3, poster_url: null, duration_mins: 165, certification: "UA" },
    { id: 8, name: "Pathaan", language: "Hindi", genres: ["Action", "Spy"], rating: 7.9, poster_url: null, duration_mins: 146, certification: "UA" },
    { id: 9, name: "RRR", language: "Telugu", genres: ["Action", "Drama"], rating: 9.0, poster_url: null, duration_mins: 187, certification: "UA" },
    { id: 10, name: "KGF Chapter 2", language: "Kannada", genres: ["Action"], rating: 8.4, poster_url: null, duration_mins: 168, certification: "UA" },
    { id: 11, name: "Brahmastra", language: "Hindi", genres: ["Fantasy", "Action"], rating: 6.5, poster_url: null, duration_mins: 167, certification: "UA" },
    { id: 12, name: "Leo", language: "Tamil", genres: ["Action", "Thriller"], rating: 7.6, poster_url: null, duration_mins: 164, certification: "UA" },
];

const CITIES = [
    { code: "MUM", name: "Mumbai" },
    { code: "DEL", name: "Delhi NCR" },
    { code: "BLR", name: "Bangalore" },
    { code: "HYD", name: "Hyderabad" },
    { code: "CHE", name: "Chennai" },
    { code: "KOL", name: "Kolkata" },
    { code: "PUN", name: "Pune" },
    { code: "AHM", name: "Ahmedabad" },
];

const LANGUAGES = ["All", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "English"];

function MovieCard({ movie }: { movie: Movie }) {
    return (
        <a href={`/movies/${movie.id}`} className="glass rounded-2xl overflow-hidden card-hover group block">
            {/* Poster */}
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
                {movie.certification && (
                    <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur px-2 py-1 rounded text-xs font-medium text-white">
                        {movie.certification}
                    </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                    <span className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium text-center">
                        View Shows
                    </span>
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
        </a>
    );
}

function MoviesPageContent() {
    const searchParams = useSearchParams();
    const cityParam = searchParams.get("city") || "MUM";

    const [selectedCity, setSelectedCity] = useState(cityParam);
    const [selectedLanguage, setSelectedLanguage] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [movies, setMovies] = useState<Movie[]>(MOCK_MOVIES);
    const [isLoading, setIsLoading] = useState(false);

    // Filter movies
    const filteredMovies = movies.filter((movie) => {
        const matchesLanguage = selectedLanguage === "All" || movie.language === selectedLanguage;
        const matchesSearch = movie.name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesLanguage && matchesSearch;
    });

    useEffect(() => {
        setIsLoading(true);
        const timer = setTimeout(() => {
            setMovies(MOCK_MOVIES);
            setIsLoading(false);
        }, 300);
        return () => clearTimeout(timer);
    }, [selectedCity]);

    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold gradient-text mb-2">Movies</h1>
                    <p className="text-slate-400">
                        Now showing in {CITIES.find(c => c.code === selectedCity)?.name}
                    </p>
                </div>

                {/* Filters */}
                <div className="glass rounded-2xl p-6 mb-8">
                    <div className="flex flex-col md:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search movies..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white placeholder:text-slate-500 focus:border-indigo-500 outline-none"
                            />
                        </div>

                        {/* City Filter */}
                        <div>
                            <select
                                value={selectedCity}
                                onChange={(e) => setSelectedCity(e.target.value)}
                                className="w-full md:w-auto px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white focus:border-indigo-500 outline-none"
                            >
                                {CITIES.map((city) => (
                                    <option key={city.code} value={city.code}>
                                        {city.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Language Filter */}
                        <div>
                            <select
                                value={selectedLanguage}
                                onChange={(e) => setSelectedLanguage(e.target.value)}
                                className="w-full md:w-auto px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white focus:border-indigo-500 outline-none"
                            >
                                {LANGUAGES.map((lang) => (
                                    <option key={lang} value={lang}>
                                        {lang}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Language Pills */}
                    <div className="flex flex-wrap gap-2 mt-4">
                        {LANGUAGES.map((lang) => (
                            <button
                                key={lang}
                                onClick={() => setSelectedLanguage(lang)}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition ${selectedLanguage === lang
                                    ? "bg-indigo-600 text-white"
                                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                                    }`}
                            >
                                {lang}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Results Count */}
                <div className="mb-6">
                    <p className="text-slate-400">
                        Showing <span className="text-white font-medium">{filteredMovies.length}</span> movies
                    </p>
                </div>

                {/* Movies Grid */}
                {isLoading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                        {[...Array(12)].map((_, i) => (
                            <div key={i} className="glass rounded-2xl overflow-hidden">
                                <div className="aspect-[2/3] bg-slate-700 shimmer"></div>
                                <div className="p-4 space-y-2">
                                    <div className="h-5 bg-slate-700 rounded shimmer"></div>
                                    <div className="h-4 bg-slate-700 rounded w-2/3 shimmer"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : filteredMovies.length === 0 ? (
                    <div className="text-center py-16">
                        <span className="text-6xl mb-4 block">🎬</span>
                        <h3 className="text-xl font-semibold text-white mb-2">No movies found</h3>
                        <p className="text-slate-400">Try adjusting your filters or search query</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                        {filteredMovies.map((movie) => (
                            <MovieCard key={movie.id} movie={movie} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default function MoviesPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen py-8 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="h-10 w-48 bg-slate-700 rounded shimmer mb-8"></div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                        {[...Array(12)].map((_, i) => (
                            <div key={i} className="glass rounded-2xl overflow-hidden">
                                <div className="aspect-[2/3] bg-slate-700 shimmer"></div>
                                <div className="p-4 space-y-2">
                                    <div className="h-5 bg-slate-700 rounded shimmer"></div>
                                    <div className="h-4 bg-slate-700 rounded w-2/3 shimmer"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        }>
            <MoviesPageContent />
        </Suspense>
    );
}
