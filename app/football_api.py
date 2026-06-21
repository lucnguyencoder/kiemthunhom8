"""
Football Data API Client
Fetches real football match data from football-data.org
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
PREMIER_LEAGUE_ID = 2790
API_KEY = "demo"  # Free tier - limited to 10 requests/minute

class FootballDataClient:
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = FOOTBALL_DATA_BASE_URL
        self.headers = {"X-Auth-Token": api_key}
    
    async def get_live_matches(self) -> List[Dict[str, Any]]:
        """Get live and recent matches from Premier League"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Get matches from last 7 days and next 7 days
                today = datetime.now()
                start_date = (today - timedelta(days=7)).isoformat()
                end_date = (today + timedelta(days=7)).isoformat()
                
                url = f"{self.base_url}/competitions/{PREMIER_LEAGUE_ID}/matches"
                params = {
                    "dateFrom": start_date,
                    "dateTo": end_date,
                    "status": "LIVE,FINISHED"
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Filter for available matches
                matches = [m for m in data.get("matches", []) if m.get("homeTeam") and m.get("awayTeam")]
                return sorted(matches, key=lambda x: x.get("utcDate", ""), reverse=True)[:5]
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    async def get_match_detail(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed info for a specific match"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{self.base_url}/matches/{match_id}"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching match detail {match_id}: {e}")
            return None
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get all Premier League teams"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{self.base_url}/competitions/{PREMIER_LEAGUE_ID}/teams"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("teams", [])
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return []


# Singleton instance
client = FootballDataClient()
