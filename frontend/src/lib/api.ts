// API client for Bo_Check backend

import type {
    City,
    Movie,
    MovieListResponse,
    Theater,
    Show,
    StatsResponse,
    TrendingMovie,
    PriceComparison,
} from "@/types/movie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = "ApiError";
    }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                ...options?.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new ApiError(response.status, `API error: ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new Error(`Network error: ${error}`);
    }
}

// Cities API
export const citiesApi = {
    getAll: () => fetchApi<City[]>("/cities"),
    getByCode: (code: string) => fetchApi<City>(`/cities/${code}`),
};

// Movies API
export const moviesApi = {
    getAll: (params: {
        city: string;
        page?: number;
        per_page?: number;
        language?: string;
        genre?: string;
    }) => {
        const searchParams = new URLSearchParams({
            city: params.city,
            page: String(params.page || 1),
            per_page: String(params.per_page || 20),
        });
        if (params.language) searchParams.set("language", params.language);
        if (params.genre) searchParams.set("genre", params.genre);

        return fetchApi<MovieListResponse>(`/movies?${searchParams}`);
    },

    getById: (id: number) => fetchApi<Movie>(`/movies/${id}`),

    getShows: (movieId: number, city: string, date?: string) => {
        const searchParams = new URLSearchParams({ city });
        if (date) searchParams.set("date", date);

        return fetchApi<{
            movie: Movie;
            city: string;
            date: string;
            theaters: {
                theater: Theater;
                shows: Show[];
            }[];
        }>(`/movies/${movieId}/shows?${searchParams}`);
    },

    search: (query: string, city: string) =>
        fetchApi<Movie[]>(`/movies/search/${encodeURIComponent(query)}?city=${city}`),
};

// Theaters API
export const theatersApi = {
    getAll: (city: string, chain?: string) => {
        const searchParams = new URLSearchParams({ city });
        if (chain) searchParams.set("chain", chain);

        return fetchApi<Theater[]>(`/theaters?${searchParams}`);
    },

    getById: (id: number) => fetchApi<Theater>(`/theaters/${id}`),

    getShows: (theaterId: number, date?: string) => {
        const searchParams = date ? new URLSearchParams({ date }) : "";
        return fetchApi<{
            theater: Theater;
            date: string;
            movies: {
                movie: Movie;
                shows: Show[];
            }[];
        }>(`/theaters/${theaterId}/shows${searchParams ? `?${searchParams}` : ""}`);
    },
};

// Shows API
export const showsApi = {
    getById: (id: number) =>
        fetchApi<{
            id: number;
            showtime: string;
            format: string;
            movie: { id: number; name: string; poster: string };
            theater: { id: number; name: string; address: string };
            seat_categories: {
                name: string;
                price: number;
                total_seats: number;
                available_seats: number;
                occupancy_percent: number;
            }[];
        }>(`/shows/${id}`),

    getSeats: (showId: number) =>
        fetchApi<{
            show_id: number;
            total_seats: number;
            available_seats: number;
            overall_occupancy: number;
            categories: {
                name: string;
                price: number;
                total: number;
                available: number;
                booked: number;
                occupancy: number;
            }[];
        }>(`/shows/${showId}/seats`),
};

// Stats API
export const statsApi = {
    getOverview: (city: string) =>
        fetchApi<{
            city: string;
            city_name: string;
            total_theaters: number;
            total_shows_today: number;
            price_range: {
                min: number;
                max: number;
                avg: number;
            };
        }>(`/stats/overview?city=${city}`),

    getMovieStats: (movieId: number, city?: string) => {
        const params = city ? `?city=${city}` : "";
        return fetchApi<{
            movie_id: number;
            city: string;
            total_shows: number;
            price_stats: {
                min: number;
                max: number;
                avg: number;
                by_category: Record<string, number>;
            };
            occupancy_stats: {
                avg: number;
                by_category: Record<string, number>;
            };
        }>(`/stats/movie/${movieId}${params}`);
    },

    getTrending: (city: string, limit?: number) =>
        fetchApi<{
            city: string;
            trending: TrendingMovie[];
        }>(`/stats/trending?city=${city}&limit=${limit || 10}`),

    getPriceComparison: (movieId: number, city: string) =>
        fetchApi<PriceComparison>(`/stats/price-comparison?movie_id=${movieId}&city=${city}`),
};

export default {
    cities: citiesApi,
    movies: moviesApi,
    theaters: theatersApi,
    shows: showsApi,
    stats: statsApi,
};
