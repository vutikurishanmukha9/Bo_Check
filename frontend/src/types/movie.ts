// Movie booking types for Bo_Check

export interface City {
    id: number;
    name: string;
    code: string;
    state: string;
}

export interface Movie {
    id: number;
    external_id: string;
    name: string;
    language: string | null;
    genres: string[];
    duration_mins: number | null;
    rating: number | null;
    release_date: string | null;
    poster_url: string | null;
    synopsis: string | null;
    certification: string | null;
    source: string;
}

export interface Theater {
    id: number;
    name: string;
    address: string | null;
    chain: string | null;
    city_code?: string;
}

export interface SeatCategory {
    name: string;
    price: number;
    total_seats: number;
    available_seats: number;
    occupancy_percent: number;
}

export interface Show {
    id: number;
    showtime: string;
    format: string;
    language: string | null;
    is_available: boolean;
    booking_url: string | null;
    theater: Theater;
    seat_categories: SeatCategory[];
}

export interface MovieListResponse {
    movies: Movie[];
    total: number;
    page: number;
    per_page: number;
    city: string;
}

export interface MovieWithShows extends Movie {
    shows: Show[];
}

export interface TheaterWithShows extends Theater {
    shows: Show[];
}

export interface StatsResponse {
    total_shows: number;
    total_theaters: number;
    avg_price: number;
    min_price: number;
    max_price: number;
    avg_occupancy: number;
    price_by_category: Record<string, number>;
    occupancy_by_time: Record<string, number>;
}

export interface TrendingMovie {
    rank: number;
    movie: Movie;
    show_count: number;
    avg_availability: number;
}

export interface PriceComparison {
    movie_id: number;
    city: string;
    theaters: {
        id: number;
        name: string;
        chain: string | null;
        min_prices: Record<string, number>;
        cheapest: number;
    }[];
}
