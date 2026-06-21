import random
import uuid
from datetime import datetime, timezone

from app.models import (
    EventType,
    LiveMatchPayload,
    MatchEvent,
    MatchState,
    TeamStats,
)

PREMIER_LEAGUE_TEAMS = {
    "Arsenal": [
        "David Raya", "Ben White", "William Saliba", "Gabriel Magalhaes",
        "Oleksandr Zinchenko", "Thomas Partey", "Martin Odegaard", "Declan Rice",
        "Bukayo Saka", "Gabriel Martinelli", "Kai Havertz",
    ],
    "Chelsea": [
        "Robert Sanchez", "Reece James", "Thiago Silva", "Levi Colwill",
        "Marc Cucurella", "Moises Caicedo", "Enzo Fernandez", "Cole Palmer",
        "Raheem Sterling", "Nicolas Jackson", "Christopher Nkunku",
    ],
    "Manchester City": [
        "Ederson", "Kyle Walker", "Ruben Dias", "John Stones", "Nathan Ake",
        "Rodri", "Kevin De Bruyne", "Phil Foden", "Bernardo Silva", "Erling Haaland", "Julian Alvarez",
    ],
    "Liverpool": [
        "Alisson", "Trent Alexander-Arnold", "Virgil van Dijk", "Ibrahima Konate", "Andy Robertson",
        "Fabinho", "Jordan Henderson", "Mohamed Salah", "Luis Diaz", "Diogo Jota", "Darwin Nunez",
    ],
    "Manchester United": [
        "Andre Onana", "Wan-Bissaka", "Harry Maguire", "Lisandro Martinez", "Luke Shaw",
        "Scott McTominay", "Bruno Fernandes", "Marcus Rashford", "Jadon Sancho", "Alejandro Garnacho", "Rasmus Hojlund",
    ],
    "Tottenham": [
        "Hugo Lloris", "Porro", "Cristian Romero", "Micky van de Ven", "Ben Davies",
        "Yves Bissouma", "Rodrigo Bentancur", "Son Heung-min", "James Maddison", "Heung-Min Son", "Richarlison",
    ],
    "Newcastle United": [
        "Nick Pope", "Kieran Trippier", "Sven Botman", "Fabian Schar", "Dan Burn",
        "Bruno Guimaraes", "Jonjo Shelvey", "Allan Saint-Maximin", "Miguel Almiron", "Anthony Gordon", "Alexander Isak",
    ],
    "Brighton": [
        "Robert Sanchez", "Joel Veltman", "Lewis Dunk", "Igor Julio", "Alexis Mac Allister",
        "Moisés Caicedo", "Adam Lallana", "Alexis Mac Allister", "Tariq Lamptey", "Evan Ferguson", "Deniz Undav",
    ],
    "Aston Villa": [
        "Emiliano Martinez", "Matty Cash", "Ezri Konsa", "Pau Torres", "Lucas Digne",
        "Douglas Luiz", "John McGinn", "Ollie Watkins", "Morgan Rogers", "Moussa Diaby", "Jhon Duran",
    ],
    "West Ham": [
        "Lukasz Fabianski", "Vladimir Coufal", "Thilo Kehrer", "Kurt Zouma", "Emerson",
        "Declan Rice", "Tomas Soucek", "Mohammed Kudus", "Said Benrahma", "Jarrod Bowen", "Michail Antonio",
    ],
}

# Default teams
HOME_TEAM = "Arsenal"
AWAY_TEAM = "Chelsea"

EVENT_WEIGHTS = [
    (EventType.POSSESSION_UPDATE, 45),
    (EventType.FOUL, 15),
    (EventType.SHOT_ON_TARGET, 10),
    (EventType.CORNER, 8),
    (EventType.OFFSIDE, 7),
    (EventType.GOAL, 3),
    (EventType.YELLOW_CARD, 5),
    (EventType.RED_CARD, 1),
    (EventType.SUBSTITUTION, 3),
    (EventType.VAR_CHECK, 2),
    (EventType.INJURY, 1),
]

EVENT_DESCRIPTIONS = {
    EventType.GOAL: [
        "{player} slots it home!",
        "{player} scores a stunning goal!",
        "{player} heads it in from a corner!",
    ],
    EventType.YELLOW_CARD: [
        "{player} is booked for a dangerous foul.",
        "{player} receives a yellow card for simulation.",
        "{player} is cautioned for dissent.",
    ],
    EventType.RED_CARD: [
        "{player} receives a straight red card!",
        "{player} is sent off after a second yellow.",
        "Shocking dismissal for {player}!",
    ],
    EventType.SUBSTITUTION: [
        "{player} comes off the bench to replace a teammate.",
        "Manager brings on {player} to change things up.",
    ],
    EventType.CORNER: [
        "{player} delivers the corner kick.",
        "Corner won by {player}.",
    ],
    EventType.FOUL: [
        "{player} gives away a foul.",
        "{player} brings down the attacker.",
    ],
    EventType.OFFSIDE: [
        "{player} is caught offside. Flag is raised.",
        "Offside call against {player}.",
    ],
    EventType.VAR_CHECK: [
        "VAR is reviewing the incident involving {player}.",
        "Referee consults VAR after {player}'s challenge.",
    ],
    EventType.INJURY: [
        "{player} is down on the pitch receiving treatment.",
        "{player} appears to have picked up a knock.",
    ],
    EventType.SHOT_ON_TARGET: [
        "{player} forces a save from the goalkeeper!",
        "{player} tests the keeper with a powerful shot.",
    ],
    EventType.POSSESSION_UPDATE: [
        "Possession stats updated.",
        "Ball retention figures recalculated.",
    ],
}


def _pick_event_type() -> EventType:
    types, weights = zip(*EVENT_WEIGHTS)
    return random.choices(types, weights=weights, k=1)[0]


def _pick_team(home_team: str, away_team: str) -> str:
    return random.choice([home_team, away_team])


def _pick_player(team: str) -> str:
    return random.choice(PREMIER_LEAGUE_TEAMS[team])


def _build_event(
    minute: int, 
    home: TeamStats, 
    away: TeamStats,
    home_team: str,
    away_team: str,
) -> MatchEvent:
    event_type = _pick_event_type()
    team = _pick_team(home_team, away_team)
    player = _pick_player(team)
    template = random.choice(EVENT_DESCRIPTIONS[event_type])
    description = template.format(player=player)

    stats = home if team == home_team else away

    if event_type == EventType.GOAL:
        stats.score += 1
        stats.shots += 1
        stats.shots_on_target += 1
    elif event_type == EventType.YELLOW_CARD:
        stats.yellow_cards += 1
        stats.fouls += 1
    elif event_type == EventType.RED_CARD:
        stats.red_cards += 1
    elif event_type == EventType.CORNER:
        stats.corners += 1
    elif event_type == EventType.FOUL:
        stats.fouls += 1
    elif event_type == EventType.SHOT_ON_TARGET:
        stats.shots += 1
        stats.shots_on_target += 1
    elif event_type == EventType.POSSESSION_UPDATE:
        home_poss = random.randint(30, 70)
        home.possession = home_poss
        away.possession = 100 - home_poss

    return MatchEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        minute=minute,
        added_time=random.choice([None, None, None, random.randint(1, 5)]),
        team=team,
        player=player,
        description=description,
    )


def create_initial_state(home_team: str = HOME_TEAM, away_team: str = AWAY_TEAM) -> MatchState:
    return MatchState(
        match_id=str(uuid.uuid4()),
        status="IN_PROGRESS",
        minute=0,
        added_time=0,
        home=TeamStats(
            name=home_team, score=0, possession=50, shots=0,
            shots_on_target=0, corners=0, fouls=0, yellow_cards=0, red_cards=0,
        ),
        away=TeamStats(
            name=away_team, score=0, possession=50, shots=0,
            shots_on_target=0, corners=0, fouls=0, yellow_cards=0, red_cards=0,
        ),
    )


def create_state_from_match_data(match_data: dict) -> MatchState:
    """Create match state from real Football-Data.org API response"""
    home = match_data.get("homeTeam", {})
    away = match_data.get("awayTeam", {})
    score = match_data.get("score", {})
    
    # Extract scores
    home_score = score.get("fullTime", {}).get("home", 0) or 0
    away_score = score.get("fullTime", {}).get("away", 0) or 0
    
    # If match is live, use current score
    if match_data.get("status") in ["LIVE", "IN_PLAY"]:
        home_score = score.get("current", {}).get("home", home_score) or home_score
        away_score = score.get("current", {}).get("away", away_score) or away_score
    
    status = "IN_PROGRESS" if match_data.get("status") in ["LIVE", "IN_PLAY"] else "FINISHED"
    
    return MatchState(
        match_id=str(match_data.get("id", uuid.uuid4())),
        status=status,
        minute=match_data.get("minute", 0) or 0,
        added_time=0,
        home=TeamStats(
            name=home.get("name", "Home"),
            score=home_score,
            possession=50,
            shots=0,
            shots_on_target=0,
            corners=0,
            fouls=0,
            yellow_cards=0,
            red_cards=0,
        ),
        away=TeamStats(
            name=away.get("name", "Away"),
            score=away_score,
            possession=50,
            shots=0,
            shots_on_target=0,
            corners=0,
            fouls=0,
            yellow_cards=0,
            red_cards=0,
        ),
    )


def generate_tick(state: MatchState, home_team: str = HOME_TEAM, away_team: str = AWAY_TEAM) -> LiveMatchPayload:
    state.minute = min(state.minute + random.randint(0, 1), 90)
    if state.minute >= 90:
        state.added_time += random.randint(0, 1)
        state.status = "EXTRA_TIME" if state.added_time <= 5 else "FINISHED"

    event = _build_event(state.minute, state.home, state.away, home_team, away_team)
    state.latest_event = event

    return LiveMatchPayload(
        timestamp=datetime.now(timezone.utc).isoformat(),
        match=state,
    )