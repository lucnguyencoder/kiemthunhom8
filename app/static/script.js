const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/live-match`;

let ws = null;
let eventsList = [];

function connectWebSocket() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('Connected to WebSocket');
        updateStatus('Connected - Waiting for match...', true);
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
        updateStatus('Disconnected', false);
        setTimeout(connectWebSocket, 3000);
    };
}

function updateStatus(message, isConnected) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.style.color = isConnected ? '#2ed573' : '#ff4757';
}

function updateMatchDisplay(data) {
    const match = data.match;

    // Update score
    document.getElementById('homeName').textContent = match.home.name;
    document.getElementById('homeScore').textContent = match.home.score;
    document.getElementById('homePossession').textContent = match.home.possession + '%';

    document.getElementById('awayName').textContent = match.away.name;
    document.getElementById('awayScore').textContent = match.away.score;
    document.getElementById('awayPossession').textContent = match.away.possession + '%';

    // Update minute
    document.getElementById('minute').textContent = match.minute + "'";

    // Update status badge
    const badge = document.getElementById('statusBadge');
    if (match.status === 'FINISHED') {
        badge.textContent = 'FINISHED';
        badge.classList.add('finished');
    } else {
        badge.textContent = 'LIVE';
        badge.classList.remove('finished');
    }

    // Add event if exists
    if (match.latest_event && match.latest_event.event_type) {
        addEvent(match.minute, match.latest_event);
    }

    // Update status
    if (match.status === 'FINISHED') {
        updateStatus('Match Finished', true);
    } else {
        updateStatus('Match Live', true);
    }
}

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
        <span class="event-time">[${minute}']</span>
        <span class="event-type">${typeDisplay}</span>
        <span class="event-description">${event.description}</span>
    `;

    const eventsList = document.getElementById('eventsList');
    if (eventsList.querySelector('.placeholder')) {
        eventsList.innerHTML = '';
    }

    eventsList.insertBefore(eventEl, eventsList.firstChild);

    // Keep only last 50 events
    while (eventsList.children.length > 50) {
        eventsList.removeChild(eventsList.lastChild);
    }
}

// Connect on page load
window.addEventListener('DOMContentLoaded', connectWebSocket);

// Reconnect on page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (ws) ws.close();
    } else {
        if (!ws || ws.readyState === WebSocket.CLOSED) {
            connectWebSocket();
        }
    }
});
