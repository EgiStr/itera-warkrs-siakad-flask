"""
Vercel Cron WAR Management Interface
Add this to your existing dashboard template
"""

# Add to templates/dashboard.html or create new template

WAR_BACKGROUND_HTML = """
<div class="card">
    <div class="card-header">
        <h5>Background WAR Process</h5>
        <small class="text-muted">Automatic course registration via Vercel Cron</small>
    </div>
    <div class="card-body">
        <div id="warStatus" class="mb-3">
            <div class="d-flex justify-content-between align-items-center">
                <span>Status: <span id="currentStatus" class="badge bg-secondary">Stopped</span></span>
                <span id="lastActivity" class="text-muted small"></span>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <label for="warInterval" class="form-label">Check Interval (minutes)</label>
                <input type="number" class="form-control" id="warInterval" value="5" min="1" max="60">
            </div>
            <div class="col-md-4 d-flex align-items-end">
                <button id="startWarBtn" class="btn btn-success me-2">Start WAR</button>
                <button id="stopWarBtn" class="btn btn-danger" disabled>Stop</button>
            </div>
        </div>
        
        <div class="mt-3">
            <h6>Recent Activity</h6>
            <div id="warLogs" class="border rounded p-2" style="height: 200px; overflow-y: auto; background-color: #f8f9fa;">
                <small class="text-muted">No activity yet...</small>
            </div>
        </div>
        
        <div class="mt-3">
            <div class="row">
                <div class="col-sm-6">
                    <strong>Total Attempts:</strong> <span id="totalAttempts">0</span>
                </div>
                <div class="col-sm-6">
                    <strong>Successful:</strong> <span id="successfulAttempts">0</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let currentSessionId = null;

// Start WAR Background Process
document.getElementById('startWarBtn').addEventListener('click', async function() {
    const interval = document.getElementById('warInterval').value;
    
    try {
        const response = await fetch('/api/war/start-cron', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                interval_minutes: parseInt(interval)
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentSessionId = result.session_id;
            updateWarStatus('scheduled', result.message);
            document.getElementById('startWarBtn').disabled = true;
            document.getElementById('stopWarBtn').disabled = false;
            addLogEntry('SUCCESS', 'WAR background process started');
            
            // Start monitoring
            startStatusMonitoring();
        } else {
            addLogEntry('ERROR', result.error || 'Failed to start WAR');
        }
    } catch (error) {
        addLogEntry('ERROR', 'Network error: ' + error.message);
    }
});

// Stop WAR Process
document.getElementById('stopWarBtn').addEventListener('click', async function() {
    if (!currentSessionId) return;
    
    try {
        const response = await fetch(`/api/war/stop/${currentSessionId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateWarStatus('stopped', 'WAR process stopped');
            document.getElementById('startWarBtn').disabled = false;
            document.getElementById('stopWarBtn').disabled = true;
            addLogEntry('INFO', 'WAR process stopped by user');
            
            // Stop monitoring
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
        } else {
            addLogEntry('ERROR', result.error || 'Failed to stop WAR');
        }
    } catch (error) {
        addLogEntry('ERROR', 'Network error: ' + error.message);
    }
});

// Manual Trigger
function triggerManualWAR() {
    fetch('/api/war/trigger', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: currentSessionId
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.successful_courses && result.successful_courses.length > 0) {
            addLogEntry('SUCCESS', `Manual WAR successful: ${result.successful_courses.join(', ')}`);
        } else {
            addLogEntry('INFO', 'Manual WAR completed: ' + (result.message || 'No courses obtained'));
        }
    })
    .catch(error => {
        addLogEntry('ERROR', 'Manual trigger failed: ' + error.message);
    });
}

// Status Monitoring
let statusInterval = null;

function startStatusMonitoring() {
    if (statusInterval) clearInterval(statusInterval);
    
    statusInterval = setInterval(async function() {
        if (!currentSessionId) return;
        
        try {
            const response = await fetch(`/api/war/status/${currentSessionId}`);
            const status = await response.json();
            
            updateWarStatus(status.status);
            document.getElementById('lastActivity').textContent = 
                status.last_activity ? 'Last: ' + new Date(status.last_activity).toLocaleString() : '';
            
            document.getElementById('totalAttempts').textContent = status.total_attempts || 0;
            document.getElementById('successfulAttempts').textContent = status.successful_attempts || 0;
            
            // Update logs
            if (status.recent_logs && status.recent_logs.length > 0) {
                const logsContainer = document.getElementById('warLogs');
                status.recent_logs.forEach(log => {
                    addLogEntry(log.level, log.message, new Date(log.timestamp));
                });
            }
            
            // If completed or failed, stop monitoring
            if (['completed', 'failed', 'stopped'].includes(status.status)) {
                document.getElementById('startWarBtn').disabled = false;
                document.getElementById('stopWarBtn').disabled = true;
                clearInterval(statusInterval);
                statusInterval = null;
            }
            
        } catch (error) {
            console.error('Status monitoring error:', error);
        }
    }, 30000); // Check every 30 seconds
}

function updateWarStatus(status, message = null) {
    const statusEl = document.getElementById('currentStatus');
    statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    
    // Update badge color
    statusEl.className = 'badge ' + {
        'active': 'bg-success',
        'scheduled': 'bg-info', 
        'completed': 'bg-primary',
        'failed': 'bg-danger',
        'stopped': 'bg-secondary'
    }[status] || 'bg-secondary';
    
    if (message) {
        addLogEntry('INFO', message);
    }
}

function addLogEntry(level, message, timestamp = null) {
    const logsContainer = document.getElementById('warLogs');
    const time = timestamp || new Date();
    const timeStr = time.toLocaleTimeString();
    
    const levelClass = {
        'SUCCESS': 'text-success',
        'ERROR': 'text-danger', 
        'WARNING': 'text-warning',
        'INFO': 'text-info'
    }[level] || '';
    
    const logEntry = document.createElement('div');
    logEntry.className = 'mb-1';
    logEntry.innerHTML = `<small><span class="text-muted">[${timeStr}]</span> <span class="${levelClass}">${level}:</span> ${message}</small>`;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Keep only last 50 entries
    while (logsContainer.children.length > 50) {
        logsContainer.removeChild(logsContainer.firstChild);
    }
}

// Check for existing active session on page load
window.addEventListener('load', function() {
    // You can add logic here to check for existing active sessions
    // and restore the interface state
});
</script>

<!-- Add manual trigger button -->
<div class="mt-2">
    <button onclick="triggerManualWAR()" class="btn btn-outline-primary btn-sm">
        Manual Trigger
    </button>
    <small class="text-muted ms-2">Run one WAR attempt now</small>
</div>
"""
