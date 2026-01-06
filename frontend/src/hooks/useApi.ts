/**
 * React Query hooks for API data fetching
 */

import { useQuery } from '@tanstack/react-query';
import {
    citiesApi,
    moviesApi,
    theatersApi,
    statsApi,
    healthApi,
    type Movie,
    type MovieListResponse,
    type City,
    type Theater,
    type OverviewStats,
    type TrendingResponse,
} from '@/lib/api';

// Query key factory for consistent cache keys
export const queryKeys = {
    cities: ['cities'] as const,
    city: (code: string) => ['city', code] as const,
    movies: (city: string, page?: number) => ['movies', city, page] as const,
    movie: (id: number) => ['movie', id] as const,
    movieShows: (movieId: number, city: string, date?: string) =>
        ['movieShows', movieId, city, date] as const,
    theaters: (city: string) => ['theaters', city] as const,
    stats: (city: string) => ['stats', city] as const,
    trending: (city: string) => ['trending', city] as const,
    health: ['health'] as const,
};

/**
 * Hook to fetch all cities
 */
export function useCities() {
    return useQuery({
        queryKey: queryKeys.cities,
        queryFn: citiesApi.getAll,
        staleTime: 1000 * 60 * 30, // Cache for 30 minutes
    });
}

/**
 * Hook to fetch movies by city
 */
export function useMovies(city: string, page = 1, perPage = 20) {
    return useQuery({
        queryKey: queryKeys.movies(city, page),
        queryFn: () => moviesApi.getList(city, page, perPage),
        enabled: !!city,
        staleTime: 1000 * 60 * 5, // Cache for 5 minutes
    });
}

/**
 * Hook to fetch a single movie
 */
export function useMovie(movieId: number) {
    return useQuery({
        queryKey: queryKeys.movie(movieId),
        queryFn: () => moviesApi.getById(movieId),
        enabled: !!movieId,
    });
}

/**
 * Hook to fetch movie shows
 */
export function useMovieShows(movieId: number, city: string, date?: string) {
    return useQuery({
        queryKey: queryKeys.movieShows(movieId, city, date),
        queryFn: () => moviesApi.getShows(movieId, city, date),
        enabled: !!movieId && !!city,
        staleTime: 1000 * 60 * 2, // Cache for 2 minutes (shows change frequently)
    });
}

/**
 * Hook to fetch theaters by city
 */
export function useTheaters(city: string) {
    return useQuery({
        queryKey: queryKeys.theaters(city),
        queryFn: () => theatersApi.getByCity(city),
        enabled: !!city,
        staleTime: 1000 * 60 * 15, // Cache for 15 minutes
    });
}

/**
 * Hook to fetch overview stats for a city
 */
export function useStats(city: string) {
    return useQuery({
        queryKey: queryKeys.stats(city),
        queryFn: () => statsApi.getOverview(city),
        enabled: !!city,
        staleTime: 1000 * 60 * 5,
    });
}

/**
 * Hook to fetch trending movies
 */
export function useTrending(city: string, limit = 10) {
    return useQuery({
        queryKey: queryKeys.trending(city),
        queryFn: () => statsApi.getTrending(city, limit),
        enabled: !!city,
        staleTime: 1000 * 60 * 5,
    });
}

/**
 * Hook to check API health
 */
export function useHealth() {
    return useQuery({
        queryKey: queryKeys.health,
        queryFn: healthApi.check,
        staleTime: 1000 * 30, // Check every 30 seconds
        retry: 1,
    });
}

/**
 * Type exports for use in components
 */
export type {
    Movie,
    MovieListResponse,
    City,
    Theater,
    OverviewStats,
    TrendingResponse,
};
