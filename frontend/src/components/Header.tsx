import { Clapperboard, TrendingUp } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

const Header = () => {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-gold to-amber glow">
            <Clapperboard className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              <span className="text-gradient">BO</span> Analytics
            </h1>
            <p className="text-xs text-muted-foreground">Box Office Dashboard</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/30">
            <TrendingUp className="w-4 h-4 text-success" />
            <span className="text-sm font-medium text-success">Live</span>
          </div>
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium">Today</p>
            <p className="text-xs text-muted-foreground">
              {new Date().toLocaleDateString('en-IN', { 
                weekday: 'short', 
                day: 'numeric', 
                month: 'short' 
              })}
            </p>
          </div>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default Header;
