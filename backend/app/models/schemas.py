"""SQLAlchemy ORM models for movie booking data."""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Text, Integer, Float, DateTime, Date, ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class City(Base):
    """Metropolitan cities supported by Bo_Check."""
    
    __tablename__ = "cities"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    theaters: Mapped[list["Theater"]] = relationship(back_populates="city", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<City(name={self.name}, code={self.code})>"


class Movie(Base):
    """Movie information scraped from booking platforms."""
    
    __tablename__ = "movies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(50))
    genres: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    duration_mins: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    release_date: Mapped[Optional[date]] = mapped_column(Date)
    poster_url: Mapped[Optional[str]] = mapped_column(Text)
    synopsis: Mapped[Optional[str]] = mapped_column(Text)
    certification: Mapped[Optional[str]] = mapped_column(String(10))  # U, UA, A, etc.
    source: Mapped[str] = mapped_column(String(50))  # bookmyshow, district
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shows: Mapped[list["Show"]] = relationship(back_populates="movie", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Movie(name={self.name}, language={self.language})>"


class Theater(Base):
    """Theater/Cinema information."""
    
    __tablename__ = "theaters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    chain: Mapped[Optional[str]] = mapped_column(String(100))  # PVR, INOX, Cinepolis, etc.
    amenities: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(50))
    
    # Foreign Keys
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    
    # Relationships
    city: Mapped["City"] = relationship(back_populates="theaters")
    shows: Mapped[list["Show"]] = relationship(back_populates="theater", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Theater(name={self.name})>"


class Show(Base):
    """Individual show/screening information."""
    
    __tablename__ = "shows"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    showtime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    format: Mapped[str] = mapped_column(String(20), default="2D")  # 2D, 3D, IMAX, 4DX
    language: Mapped[Optional[str]] = mapped_column(String(50))
    subtitles: Mapped[Optional[str]] = mapped_column(String(50))
    is_available: Mapped[bool] = mapped_column(default=True)
    booking_url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50))
    
    # Foreign Keys
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    theater_id: Mapped[int] = mapped_column(ForeignKey("theaters.id"))
    
    # Metadata
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    movie: Mapped["Movie"] = relationship(back_populates="shows")
    theater: Mapped["Theater"] = relationship(back_populates="shows")
    seat_categories: Mapped[list["SeatCategory"]] = relationship(back_populates="show", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Show(movie={self.movie_id}, time={self.showtime})>"


class SeatCategory(Base):
    """Seat category with pricing and availability."""
    
    __tablename__ = "seat_categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # Standard, Premium, Recliner
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, default=0)
    available_seats: Mapped[int] = mapped_column(Integer, default=0)
    
    # Foreign Keys
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"))
    
    # Relationships
    show: Mapped["Show"] = relationship(back_populates="seat_categories")
    
    @property
    def occupancy_percent(self) -> float:
        """Calculate occupancy percentage."""
        if self.total_seats == 0:
            return 0.0
        return ((self.total_seats - self.available_seats) / self.total_seats) * 100
    
    def __repr__(self) -> str:
        return f"<SeatCategory(name={self.name}, price={self.price})>"
