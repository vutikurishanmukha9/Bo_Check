"use client";

import { useState } from "react";
import { useParams } from "next/navigation";

// Types
interface Show {
    id: number;
    time: string;
    format: string;
    seats: {
        category: string;
        price: number;
        available: number;
        total: number;
    }[];
}

interface Theater {
    id: number;
    name: string;
    chain: string;
    address: string;
    shows: Show[];
}

// Mock data
const MOCK_MOVIE = {
    id: 1,
    name: "Pushpa 2: The Rule",
    language: "Telugu",
    genres: ["Action", "Drama", "Thriller"],
    rating: 8.5,
    duration_mins: 180,
    certification: "UA",
    release_date: "2024-12-05",
    synopsis: "Pushpa Raj returns in this action-packed sequel, continuing his rise in the world of red sandalwood smuggling while facing new challenges and enemies.",
};

const MOCK_THEATERS: Theater[] = [
    {
        id: 1,
        name: "PVR ICON: GVK One Mall",
        chain: "PVR",
        address: "GVK One Mall, Banjara Hills, Hyderabad",
        shows: [
            { id: 1, time: "09:30 AM", format: "2D", seats: [{ category: "Classic", price: 250, available: 45, total: 120 }, { category: "Premium", price: 450, available: 12, total: 40 }] },
            { id: 2, time: "01:00 PM", format: "2D", seats: [{ category: "Classic", price: 250, available: 5, total: 120 }, { category: "Premium", price: 450, available: 0, total: 40 }] },
            { id: 3, time: "04:30 PM", format: "IMAX", seats: [{ category: "IMAX", price: 700, available: 80, total: 200 }] },
            { id: 4, time: "08:00 PM", format: "2D", seats: [{ category: "Classic", price: 300, available: 0, total: 120 }, { category: "Premium", price: 550, available: 0, total: 40 }] },
            { id: 5, time: "11:00 PM", format: "2D", seats: [{ category: "Classic", price: 250, available: 90, total: 120 }, { category: "Premium", price: 450, available: 30, total: 40 }] },
        ],
    },
    {
        id: 2,
        name: "INOX: Hyderabad Central Mall",
        chain: "INOX",
        address: "Hyderabad Central Mall, Punjagutta",
        shows: [
            { id: 6, time: "10:00 AM", format: "2D", seats: [{ category: "Silver", price: 200, available: 60, total: 100 }, { category: "Gold", price: 350, available: 25, total: 50 }] },
            { id: 7, time: "02:00 PM", format: "2D", seats: [{ category: "Silver", price: 200, available: 15, total: 100 }, { category: "Gold", price: 350, available: 5, total: 50 }] },
            { id: 8, time: "06:00 PM", format: "3D", seats: [{ category: "Silver 3D", price: 280, available: 30, total: 100 }, { category: "Gold 3D", price: 450, available: 10, total: 50 }] },
            { id: 9, time: "09:30 PM", format: "2D", seats: [{ category: "Silver", price: 200, available: 70, total: 100 }, { category: "Gold", price: 350, available: 40, total: 50 }] },
        ],
    },
    {
        id: 3,
        name: "Cinepolis: Nexus Mall",
        chain: "Cinepolis",
        address: "Nexus Mall, Kukatpally",
        shows: [
            { id: 10, time: "11:00 AM", format: "2D", seats: [{ category: "Regular", price: 180, available: 80, total: 150 }, { category: "Recliner", price: 500, available: 8, total: 20 }] },
            { id: 11, time: "03:00 PM", format: "4DX", seats: [{ category: "4DX", price: 800, available: 20, total: 60 }] },
            { id: 12, time: "07:00 PM", format: "2D", seats: [{ category: "Regular", price: 220, available: 40, total: 150 }, { category: "Recliner", price: 600, available: 2, total: 20 }] },
            { id: 13, time: "10:30 PM", format: "2D", seats: [{ category: "Regular", price: 180, available: 120, total: 150 }, { category: "Recliner", price: 500, available: 15, total: 20 }] },
        ],
    },
];

const DATES = [
    { date: "Today", day: "Mon", full: "2026-01-05" },
    { date: "6", day: "Tue", full: "2026-01-06" },
    { date: "7", day: "Wed", full: "2026-01-07" },
    { date: "8", day: "Thu", full: "2026-01-08" },
    { date: "9", day: "Fri", full: "2026-01-09" },
    { date: "10", day: "Sat", full: "2026-01-10" },
    { date: "11", day: "Sun", full: "2026-01-11" },
];

function getAvailabilityColor(available: number, total: number): string {
    const percentage = (available / total) * 100;
    if (percentage === 0) return "border-red-500 text-red-400 bg-red-500/10";
    if (percentage < 20) return "border-orange-500 text-orange-400 bg-orange-500/10";
    if (percentage < 50) return "border-yellow-500 text-yellow-400 bg-yellow-500/10";
    return "border-green-500 text-green-400 bg-green-500/10";
}

function ShowButton({ show }: { show: Show }) {
    const totalAvailable = show.seats.reduce((sum, s) => sum + s.available, 0);
    const totalSeats = show.seats.reduce((sum, s) => sum + s.total, 0);
    const minPrice = Math.min(...show.seats.map(s => s.price));
    const isSoldOut = totalAvailable === 0;

    return (
        <button
            disabled={isSoldOut}
            className={`px-4 py-3 rounded-xl border-2 transition-all ${isSoldOut
                    ? "border-slate-600 text-slate-500 bg-slate-800/50 cursor-not-allowed"
                    : getAvailabilityColor(totalAvailable, totalSeats) + " hover:scale-105"
                }`}
        >
            <div className="text-sm font-semibold">{show.time}</div>
            <div className="text-xs mt-1">{show.format}</div>
            <div className="text-xs mt-1">₹{minPrice}+</div>
            {isSoldOut && <div className="text-[10px] mt-1">SOLD OUT</div>}
        </button>
    );
}

function TheaterRow({ theater }: { theater: Theater }) {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="glass rounded-2xl overflow-hidden">
            <div className="p-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    {/* Theater Info */}
                    <div className="flex-shrink-0 md:w-64">
                        <div className="flex items-center gap-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${theater.chain === "PVR" ? "bg-red-600/20 text-red-400" :
                                    theater.chain === "INOX" ? "bg-blue-600/20 text-blue-400" :
                                        "bg-purple-600/20 text-purple-400"
                                }`}>
                                {theater.chain}
                            </span>
                        </div>
                        <h3 className="text-lg font-semibold text-white mt-2">{theater.name}</h3>
                        <p className="text-slate-400 text-sm mt-1">{theater.address}</p>
                    </div>

                    {/* Shows */}
                    <div className="flex-1">
                        <div className="flex flex-wrap gap-3">
                            {theater.shows.map((show) => (
                                <ShowButton key={show.id} show={show} />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Expand for price details */}
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="mt-4 text-indigo-400 text-sm hover:text-indigo-300 flex items-center gap-1"
                >
                    {isExpanded ? "Hide price details" : "Show price details"}
                    <span className={`transition-transform ${isExpanded ? "rotate-180" : ""}`}>▼</span>
                </button>
            </div>

            {/* Expanded Price Details */}
            {isExpanded && (
                <div className="border-t border-slate-700 bg-slate-800/50 p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {theater.shows.slice(0, 3).map((show) => (
                            <div key={show.id} className="glass rounded-xl p-4">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="font-medium text-white">{show.time}</span>
                                    <span className="text-xs bg-slate-700 px-2 py-1 rounded">{show.format}</span>
                                </div>
                                {show.seats.map((seat, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-sm py-1">
                                        <span className="text-slate-400">{seat.category}</span>
                                        <div className="flex items-center gap-3">
                                            <span className="text-white">₹{seat.price}</span>
                                            <span className={`text-xs ${seat.available === 0 ? "text-red-400" : "text-green-400"}`}>
                                                {seat.available}/{seat.total}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default function MovieDetailPage() {
    const params = useParams();
    const [selectedDate, setSelectedDate] = useState(0);
    const movie = MOCK_MOVIE;
    const theaters = MOCK_THEATERS;

    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Movie Header */}
                <div className="glass rounded-2xl p-6 md:p-8 mb-8">
                    <div className="flex flex-col md:flex-row gap-6">
                        {/* Poster */}
                        <div className="w-full md:w-48 flex-shrink-0">
                            <div className="aspect-[2/3] bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl flex items-center justify-center">
                                <span className="text-6xl">🎬</span>
                            </div>
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <div className="flex flex-wrap items-center gap-3 mb-3">
                                <span className="bg-slate-700 px-3 py-1 rounded-full text-sm">{movie.certification}</span>
                                <span className="bg-indigo-600/20 text-indigo-400 px-3 py-1 rounded-full text-sm">{movie.language}</span>
                            </div>
                            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{movie.name}</h1>

                            <div className="flex flex-wrap items-center gap-4 text-slate-400 mb-4">
                                {movie.rating && (
                                    <span className="flex items-center gap-1">
                                        <span className="text-yellow-400">⭐</span>
                                        <span className="text-white font-medium">{movie.rating}/10</span>
                                    </span>
                                )}
                                <span>🕐 {Math.floor(movie.duration_mins / 60)}h {movie.duration_mins % 60}m</span>
                                <span>📅 {movie.release_date}</span>
                            </div>

                            <div className="flex flex-wrap gap-2 mb-4">
                                {movie.genres.map((genre) => (
                                    <span key={genre} className="bg-slate-700 px-3 py-1 rounded-full text-sm text-slate-300">
                                        {genre}
                                    </span>
                                ))}
                            </div>

                            <p className="text-slate-400 leading-relaxed">{movie.synopsis}</p>
                        </div>
                    </div>
                </div>

                {/* Date Selector */}
                <div className="glass rounded-2xl p-4 mb-6">
                    <div className="flex gap-2 overflow-x-auto pb-2">
                        {DATES.map((date, idx) => (
                            <button
                                key={idx}
                                onClick={() => setSelectedDate(idx)}
                                className={`flex-shrink-0 px-6 py-3 rounded-xl text-center transition ${selectedDate === idx
                                        ? "bg-indigo-600 text-white"
                                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                                    }`}
                            >
                                <div className="text-xs opacity-70">{date.day}</div>
                                <div className="font-semibold">{date.date}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Legend */}
                <div className="flex flex-wrap gap-4 mb-6 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded border-2 border-green-500 bg-green-500/10"></div>
                        <span className="text-slate-400">Available</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded border-2 border-yellow-500 bg-yellow-500/10"></div>
                        <span className="text-slate-400">Filling Fast</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded border-2 border-orange-500 bg-orange-500/10"></div>
                        <span className="text-slate-400">Almost Full</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded border-2 border-red-500 bg-red-500/10"></div>
                        <span className="text-slate-400">Sold Out</span>
                    </div>
                </div>

                {/* Theaters List */}
                <div className="space-y-4">
                    {theaters.map((theater) => (
                        <TheaterRow key={theater.id} theater={theater} />
                    ))}
                </div>
            </div>
        </div>
    );
}
