import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Bo_Check - Movie Booking Statistics India",
  description: "Real-time movie booking stats including show timings, seat availability, and ticket prices across metropolitan cities in India.",
  keywords: ["movies", "booking", "statistics", "india", "bookmyshow", "ticket prices", "seat availability"],
  authors: [{ name: "Bo_Check Team" }],
  openGraph: {
    title: "Bo_Check - Movie Booking Statistics India",
    description: "Real-time movie booking stats across India",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased min-h-screen">
        <div className="min-h-screen flex flex-col">
          {/* Header */}
          <header className="glass sticky top-0 z-50 border-b border-white/10">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <a href="/" className="flex items-center gap-3">
                  <span className="text-3xl">🎬</span>
                  <span className="text-2xl font-bold gradient-text">Bo_Check</span>
                </a>
                <div className="hidden md:flex items-center gap-8">
                  <a href="/" className="text-slate-300 hover:text-white transition">Home</a>
                  <a href="/movies" className="text-slate-300 hover:text-white transition">Movies</a>
                  <a href="/theaters" className="text-slate-300 hover:text-white transition">Theaters</a>
                  <a href="/analytics" className="text-slate-300 hover:text-white transition">Analytics</a>
                </div>
                <div className="flex items-center gap-4">
                  <select 
                    className="bg-slate-800 text-white px-4 py-2 rounded-lg border border-slate-600 focus:border-indigo-500 outline-none"
                    defaultValue="MUM"
                  >
                    <option value="MUM">Mumbai</option>
                    <option value="DEL">Delhi NCR</option>
                    <option value="BLR">Bangalore</option>
                    <option value="HYD">Hyderabad</option>
                    <option value="CHE">Chennai</option>
                    <option value="KOL">Kolkata</option>
                    <option value="PUN">Pune</option>
                    <option value="AHM">Ahmedabad</option>
                  </select>
                </div>
              </div>
            </nav>
          </header>

          {/* Main Content */}
          <main className="flex-1">
            {children}
          </main>

          {/* Footer */}
          <footer className="glass border-t border-white/10 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                  <h3 className="text-lg font-semibold mb-4 gradient-text">Bo_Check</h3>
                  <p className="text-slate-400 text-sm">
                    Real-time movie booking statistics for metropolitan cities across India.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-3 text-white">Cities</h4>
                  <ul className="space-y-2 text-sm text-slate-400">
                    <li><a href="/movies?city=MUM" className="hover:text-white">Mumbai</a></li>
                    <li><a href="/movies?city=DEL" className="hover:text-white">Delhi NCR</a></li>
                    <li><a href="/movies?city=BLR" className="hover:text-white">Bangalore</a></li>
                    <li><a href="/movies?city=HYD" className="hover:text-white">Hyderabad</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-3 text-white">Features</h4>
                  <ul className="space-y-2 text-sm text-slate-400">
                    <li>Show Timings</li>
                    <li>Seat Availability</li>
                    <li>Ticket Prices</li>
                    <li>Price Comparison</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-3 text-white">Data Sources</h4>
                  <ul className="space-y-2 text-sm text-slate-400">
                    <li>BookMyShow</li>
                    <li>District</li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-slate-700 mt-8 pt-6 text-center text-sm text-slate-400">
                <p>© 2026 Bo_Check. For educational purposes only.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
