import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function formatDuration(mins: number): string {
    const hours = Math.floor(mins / 60);
    const minutes = mins % 60;
    return `${hours}h ${minutes}m`;
}

export function formatPrice(price: number): string {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(price);
}

export function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
    });
}

export function formatTime(dateString: string): string {
    return new Date(dateString).toLocaleTimeString("en-IN", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
    });
}

export function getOccupancyColor(occupancy: number): string {
    if (occupancy >= 90) return "text-red-400";
    if (occupancy >= 70) return "text-orange-400";
    if (occupancy >= 50) return "text-yellow-400";
    return "text-green-400";
}

export function getAvailabilityStatus(available: number, total: number): {
    label: string;
    color: string;
} {
    const percentage = (available / total) * 100;

    if (percentage === 0) {
        return { label: "Sold Out", color: "text-red-400" };
    }
    if (percentage < 20) {
        return { label: "Almost Full", color: "text-orange-400" };
    }
    if (percentage < 50) {
        return { label: "Filling Fast", color: "text-yellow-400" };
    }
    return { label: "Available", color: "text-green-400" };
}

export const CITIES = [
    { code: "MUM", name: "Mumbai", state: "Maharashtra" },
    { code: "DEL", name: "Delhi NCR", state: "Delhi" },
    { code: "BLR", name: "Bangalore", state: "Karnataka" },
    { code: "HYD", name: "Hyderabad", state: "Telangana" },
    { code: "CHE", name: "Chennai", state: "Tamil Nadu" },
    { code: "KOL", name: "Kolkata", state: "West Bengal" },
    { code: "PUN", name: "Pune", state: "Maharashtra" },
    { code: "AHM", name: "Ahmedabad", state: "Gujarat" },
] as const;

export type CityCode = (typeof CITIES)[number]["code"];
