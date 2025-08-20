// Vercel-compatible WAR KRS functionality
// This replaces background threads with API calls

// Auto-refresh dashboard status
function refreshWarStatus() {
    fetch('/api/war/status')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('war-status');
            if (statusElement) {
                if (data.status === 'active') {
                    statusElement.innerHTML = `
                        <div class="alert alert-info">
                            <strong>Status:</strong> WAR process sedang berjalan...
                            <br><small>Started: ${new Date(data.started_at).toLocaleString()}</small>
                        </div>
                    `;
                } else if (data.status === 'completed') {
                    statusElement.innerHTML = `
                        <div class="alert alert-success">
                            <strong>Status:</strong> WAR process selesai
                            <br><small>Completed: ${new Date(data.last_activity).toLocaleString()}</small>
                        </div>
                    `;
                } else if (data.status === 'failed') {
                    statusElement.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>Status:</strong> WAR process gagal
                            <br><small>Failed: ${new Date(data.last_activity).toLocaleString()}</small>
                        </div>
                    `;
                } else {
                    statusElement.innerHTML = `
                        <div class="alert alert-secondary">
                            <strong>Status:</strong> Tidak ada WAR process yang berjalan
                        </div>
                    `;
                }
            }
        })
        .catch(error => {
            console.error('Error checking WAR status:', error);
        });
}

// Enhanced start WAR function for Vercel
function startWarVercel() {
    const startButton = document.getElementById('start-war-btn');
    const statusDiv = document.getElementById('war-status');
    
    if (startButton) {
        startButton.disabled = true;
        startButton.innerHTML = 'Memulai...';
    }
    
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>Status:</strong> Memulai WAR process...
            </div>
        `;
    }
    
    fetch('/api/war/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error:</strong> ${data.error}
                    </div>
                `;
            }
        } else {
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Selesai!</strong> ${data.message}
                        <br><strong>Berhasil:</strong> ${data.successful_courses.length} mata kuliah
                        <br><strong>Gagal:</strong> ${data.failed_courses.length} mata kuliah
                    </div>
                `;
            }
        }
        
        // Refresh status after completion
        setTimeout(refreshWarStatus, 1000);
    })
    .catch(error => {
        console.error('Error starting WAR:', error);
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> Network error occurred
                </div>
            `;
        }
    })
    .finally(() => {
        if (startButton) {
            startButton.disabled = false;
            startButton.innerHTML = 'Mulai WAR KRS';
        }
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Refresh status on page load
    refreshWarStatus();
    
    // Auto-refresh every 10 seconds (only for active processes)
    setInterval(() => {
        const statusElement = document.getElementById('war-status');
        if (statusElement && statusElement.innerHTML.includes('sedang berjalan')) {
            refreshWarStatus();
        }
    }, 10000);
    
    // Override the form submission if this is Vercel environment
    const warForm = document.querySelector('form[action="/war/start"]');
    if (warForm) {
        // Check if we're in a serverless environment
        const isVercel = window.location.hostname.includes('vercel.app') || 
                        window.location.hostname.includes('vercel.com');
        
        if (isVercel) {
            warForm.addEventListener('submit', function(e) {
                e.preventDefault();
                startWarVercel();
            });
        }
    }
});
