/**
 * API Client for Bo_Check Backend
 * Connects the frontend to the FastAPI backend
 */

// API Base URL - uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

/**
 * Generic API fetch wrapper with error handling
 */
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${API_PREFIX}${endpoint}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API Error: ${response.status}`);
    }

    return response.json();
}

// ============================================
// API Response Types
// ============================================

export interface Movie {
    id: number;
    name: string;
    language: string;
    duration_minutes?: number;
    genre?: string;
    rating?: number;
    poster_url?: string;
    bms_code?: string;
}

export interface MovieListResponse {
    movies: Movie[];
    total: number;
    page: number;
    per_page: number;
    city: string;
}

export interface City {
    id: number;
    name: string;
    code: string;
    state?: string;
}

export interface Theater {
    id: number;
    name: string;
    address?: string;
    chain?: string;
    city_id: number;
}

export interface Show {
    id: number;
    showtime: string;
    format?: string;
    language?: string;
    is_available: boolean;
    seat_categories?: SeatCategory[];
}

export interface SeatCategory {
    name: string;
    price: number;
    available: number;
    total: number;
}

export interface OverviewStats {
    city: string;
    city_name?: string;
    total_theaters: number;
    total_shows_today: number;
    price_range: {
        min: number;
        max: number;
        avg: number;
    };
    message?: string;
}

export interface TrendingMovie {
    rank: number;
    movie: {
        id: number;
        name: string;
        language: string;
        rating?: number;
        poster?: string;
    };
    show_count: number;
    avg_availability: number;
}

export interface TrendingResponse {
    city: string;
    trending: TrendingMovie[];
}

// ============================================
// API Methods
// ============================================

/**
 * Cities API
 */
export const citiesApi = {
    getAll: () => apiFetch<City[]>('/cities'),
    getByCode: (code: string) => apiFetch<City>(`/cities/${code}`),
};

/**
 * Movies API
 */
export const moviesApi = {
    getList: (city: string, page = 1, perPage = 20) =>
        apiFetch<MovieListResponse>(`/movies?city=${city}&page=${page}&per_page=${perPage}`),

    getById: (movieId: number) =>
        apiFetch<Movie>(`/movies/${movieId}`),

    getShows: (movieId: number, city: string, date?: string) => {
        let endpoint = `/movies/${movieId}/shows?city=${city}`;
        if (date) endpoint += `&date=${date}`;
        return apiFetch<{
            movie: Movie;
            city: string;
            date: string;
            theaters: Array<{
                theater: Theater;
                shows: Show[];
            }>;
        }>(endpoint);
    },

    search: (query: string, city: string) =>
        apiFetch<Movie[]>(`/movies/search/${query}?city=${city}`),
};

/**
 * Theaters API
 */
export const theatersApi = {
    getByCity: (city: string) =>
        apiFetch<Theater[]>(`/theaters?city=${city}`),

    getById: (theaterId: number) =>
        apiFetch<Theater>(`/theaters/${theaterId}`),
};

/**
 * Shows API
 */
export const showsApi = {
    getByTheater: (theaterId: number, date?: string) => {
        let endpoint = `/shows?theater_id=${theaterId}`;
        if (date) endpoint += `&date=${date}`;
        return apiFetch<Show[]>(endpoint);
    },
};

/**
 * Stats API
 */
export const statsApi = {
    getOverview: (city: string) =>
        apiFetch<OverviewStats>(`/stats/overview?city=${city}`),

    getMovieStats: (movieId: number, city?: string) => {
        let endpoint = `/stats/movie/${movieId}`;
        if (city) endpoint += `?city=${city}`;
        return apiFetch<{
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
        }>(endpoint);
    },

    getTrending: (city: string, limit = 10) =>
        apiFetch<TrendingResponse>(`/stats/trending?city=${city}&limit=${limit}`),

    getPriceComparison: (movieId: number, city: string) =>
        apiFetch<{
            movie_id: number;
            city: string;
            theaters: Array<{
                id: number;
                name: string;
                chain?: string;
                min_prices: Record<string, number>;
                cheapest: number;
            }>;
        }>(`/stats/price-comparison?movie_id=${movieId}&city=${city}`),
};

/**
 * Health Check
 */
export const healthApi = {
    check: () => fetch(`${API_BASE_URL}/health`).then(r => r.json()),
    root: () => fetch(`${API_BASE_URL}/`).then(r => r.json()),
};

export { API_BASE_URL };
