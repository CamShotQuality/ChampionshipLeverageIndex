from datetime import datetime

# Get the current year and determine the NBA season year
# NBA season spans across two calendar years, so we need to determine which season we're in
current_date = datetime.now()
current_year = current_date.year
current_month = current_date.month

# If we're in the 9 months (before October), we're in the previous season
# If we're in October or later, we're in the current season
SEASON_END_YEAR = current_year + 1 if current_month >= 10 else current_year

# Regular Season End date
REGULAR_END = datetime(SEASON_END_YEAR, 4, 15).date()
REGULAR_START = datetime(SEASON_END_YEAR, 10, 20).date() 