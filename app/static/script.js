let ws = null;
let eventsList = [];
let selectedHomeTeam = "Arsenal";
let selectedAwayTeam = "Chelsea";
let selectedMatchId = null;

// Initialize
async function init() {
    await loadTeams();
    await loadLiveMatches();
    setupEventListeners();
}

// Load available teams
async function loadTeams() {
    try {
        const response = await fetch('/teams');
        const data = await response.json();
        const teams = data.teams;
        
        const homeSelect = document.getElementById('homeTeam');
        const awaySelect = document.getElementById('awayTeam');
        
        teams.forEach(team => {
            const option1 = document.createElement('option');
            option1.value = team;
            option1.textContent = team;
            homeSelect.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = team;
            option2.textContent = team;
            awaySelect.appendChild(option2);
        });
        
        // Set defaults
        homeSelect.value = selectedHomeTeam;
        awaySelect.value = selectedAwayTeam;
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

// Load live matches from API
async function loadLiveMatches() {
    try {
        const response = await fetch('/matches');
        const data = await response.json();
        const matches = data.matches || [];
        
        const matchesList = document.getElementById('matchesList');
        matchesList.innerHTML = '';
        
        if (matches.length === 0) {
            matchesList.innerHTML = '<p class="placeholder">No live matches available</p>';
            return;
        }
        
        matches.forEach(match => {
            const matchEl = document.createElement('div');
            matchEl.className = 'match-card';
            matchEl.innerHTML = `
                <div class="match-header">
                    <span class="status-badge ${match.status.toLowerCase()}">${match.status}</span>
                </div>
                <div class="match-content">
                    <div class="team home-team-card">
                        <span class="team-name">${match.homeTeam}</span>
                        <span class="score">${match.score.fullTime?.home ?? '-'}</span>
                    </div>
                    <div class="vs-text">vs</div>
                    <div class="team away-team-card">
                        <span class="score">${match.score.fullTime?.away ?? '-'}</span>
                        <span class="team-name">${match.awayTeam}</span>
                    </div>
                </div>
                <button class="select-match-btn" onclick="selectLiveMatch(${match.id}, '${match.homeTeam}', '${match.awayTeam}')">Test This Match</button>
            `;
            matchesList.appendChild(matchEl);
        });
    } catch (error) {
        console.error('Error loading live matches:', error);
        document.getElementById('matchesList').innerHTML = '<p class="error">Failed to load matches</p>';
    }
}

// Select a live match and start test
async function selectLiveMatch(matchId, homeTeam, awayTeam) {
    selectedMatchId = matchId;
    selectedHomeTeam = homeTeam;
    selectedAwayTeam = awayTeam;
    startMatch();
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('homeTeam').addEventListener('change', (e) => {
        selectedHomeTeam = e.target.value;
        selectedMatchId = null;
    });
    
    document.getElementById('awayTeam').addEventListener('change', (e) => {
        selectedAwayTeam = e.target.value;
        selectedMatchId = null;
    });
    
    document.getElementById('startBtn').addEventListener('click', startMatch);
    document.getElementById('backBtn').addEventListener('click', backToSelection);
    
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
}

// Switch tabs
function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Start match and performance test
async function startMatch() {
    if (selectedHomeTeam === selectedAwayTeam) {
        alert('Please select different teams!');
        return;
    }
    
    // Hide selection panel
    document.getElementById('selectionPanel').style.display = 'none';
    document.getElementById('matchPanel').style.display = 'block';
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'none';
    
    // Clear events
    eventsList = [];
    
    // Start WebSocket connection for live match
    connectWebSocket();
    
    // Wait a bit for match to start, then run performance test
    setTimeout(runPerformanceTest, 2000);
}

// Connect to WebSocket for live match
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsUrl = `${protocol}//${window.location.host}/live-match?home_team=${selectedHomeTeam}&away_team=${selectedAwayTeam}`;
    
    if (selectedMatchId) {
        wsUrl += `&match_id=${selectedMatchId}`;
    }
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('Connected to WebSocket');
        updateStatus('Connected - Match Live', true);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            updateMatchDisplay(data);
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('Connection error', false);
    };

    ws.onclose = () => {
        console.log('WebSocket closed');
        updateStatus('Match Finished', true);
    };
}

// Update match display
function updateMatchDisplay(data) {
    const match = data.match;

    document.getElementById('homeName').textContent = match.home.name;
    document.getElementById('homeScore').textContent = match.home.score;
    document.getElementById('homePossession').textContent = match.home.possession + '%';

    document.getElementById('awayName').textContent = match.away.name;
    document.getElementById('awayScore').textContent = match.away.score;
    document.getElementById('awayPossession').textContent = match.away.possession + '%';

    document.getElementById('minute').textContent = match.minute + "'";

    const badge = document.getElementById('statusBadge');
    if (match.status === 'FINISHED') {
        badge.textContent = 'FINISHED';
        badge.classList.add('finished');
    } else {
        badge.textContent = 'LIVE';
        badge.classList.remove('finished');
    }

    if (match.latest_event && match.latest_event.event_type) {
        addEvent(match.minute, match.latest_event);
    }

    if (match.status === 'FINISHED') {
        updateStatus('Match Finished', true);
    } else {
        updateStatus('Match Live', true);
    }
}

// Add event to display
function addEvent(minute, event) {
    const eventEl = document.createElement('div');
    eventEl.className = 'event';

    const eventType = event.event_type.toLowerCase();
    if (eventType.includes('goal')) {
        eventEl.classList.add('goal');
    } else if (eventType.includes('yellow')) {
        eventEl.classList.add('yellow-card');
    } else if (eventType.includes('red')) {
        eventEl.classList.add('red-card');
    } else if (eventType.includes('possession')) {
        eventEl.classList.add('possession');
    }

    const typeDisplay = event.event_type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');

    eventEl.innerHTML = `
        <span class="event-minute">${minute}'</span>
        <span class="event-type">${typeDisplay}</span>
        <span class="event-description">${event.description}</span>
    `;

    const eventsList_el = document.getElementById('eventsList');
    if (eventsList_el.querySelector('.placeholder')) {
        eventsList_el.innerHTML = '';
    }
    eventsList_el.insertBefore(eventEl, eventsList_el.firstChild);

    if (eventsList_el.children.length > 10) {
        eventsList_el.removeChild(eventsList_el.lastChild);
    }
}

// Update status
function updateStatus(message, isConnected) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.style.color = isConnected ? '#2ed573' : '#ff4757';
}

// Run performance test
async function runPerformanceTest() {
    console.log('Starting performance test...');
    
    document.getElementById('loadingIndicator').style.display = 'flex';
    document.getElementById('loadingClientCount').textContent = '1000';
    
    try {
        const response = await fetch(`/perf-test?home_team=${selectedHomeTeam}&away_team=${selectedAwayTeam}&num_clients=1000`, {
            method: 'POST'
        });
        
        const results = await response.json();
        console.log('Performance test results:', results);
        
        // Display results
        displayResults(results);
        
        // Close WebSocket
        if (ws) {
            ws.close();
        }
        
    } catch (error) {
        console.error('Error running performance test:', error);
        document.getElementById('loadingIndicator').style.display = 'none';
    }
}

// Display performance test results
function displayResults(results) {
    document.getElementById('loadingIndicator').style.display = 'none';
    document.getElementById('matchPanel').style.display = 'none';
    document.getElementById('resultsPanel').style.display = 'block';
    
    // Summary
    document.getElementById('duration').textContent = results.test_duration_s + ' s';
    document.getElementById('clientsCount').textContent = results.clients_targeted.toLocaleString();
    document.getElementById('messagesCount').textContent = results.total_messages.toLocaleString();
    document.getElementById('errorsCount').textContent = results.errors.toLocaleString();
    
    // Latency metrics
    if (results.latency && Object.keys(results.latency).length > 0) {
        document.getElementById('latMin').textContent = results.latency.min_ms.toFixed(3) + ' ms';
        document.getElementById('latMax').textContent = results.latency.max_ms.toFixed(3) + ' ms';
        document.getElementById('latMean').textContent = results.latency.mean_ms.toFixed(3) + ' ms';
        document.getElementById('latMedian').textContent = results.latency.median_ms.toFixed(3) + ' ms';
        document.getElementById('latStdev').textContent = results.latency.stdev_ms.toFixed(3) + ' ms';
        document.getElementById('latP95').textContent = results.latency.p95_ms.toFixed(3) + ' ms';
        document.getElementById('latP99').textContent = results.latency.p99_ms.toFixed(3) + ' ms';
    }
}

// Back to selection
function backToSelection() {
    document.getElementById('selectionPanel').style.display = 'block';
    document.getElementById('matchPanel').style.display = 'none';
    document.getElementById('resultsPanel').style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
