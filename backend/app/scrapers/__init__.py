"""Scrapers package for Bo_Check."""

from app.scrapers.base import BaseScraper
from app.scrapers.bookmyshow import BookMyShowScraper

__all__ = ["BaseScraper", "BookMyShowScraper"]
