// Main JavaScript for WAR KRS Web Application

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh functionality
    function setupAutoRefresh() {
        // Check if we're on dashboard and there's an active session
        if (window.location.pathname === '/' && $('.status-active').length > 0) {
            // Refresh every 30 seconds when WAR is active
            setTimeout(function() {
                location.reload();
            }, 30000);
        }
    }

    // Status update functionality
    function updateStatus() {
        if (window.location.pathname === '/') {
            $.get('/api/status')
                .done(function(data) {
                    // Update status indicators
                    updateStatusIndicators(data);
                    
                    // Setup auto-refresh if needed
                    if (data.status === 'active') {
                        setupAutoRefresh();
                    }
                })
                .fail(function() {
                    console.log('Failed to fetch status update');
                });
        }
    }

    function updateStatusIndicators(data) {
        // Update status badge
        var statusElement = $('.status-indicator');
        if (statusElement.length > 0) {
            statusElement.removeClass('status-active status-stopped status-error');
            if (data.status === 'active') {
                statusElement.addClass('status-active');
            } else if (data.status === 'error') {
                statusElement.addClass('status-error');
            } else {
                statusElement.addClass('status-stopped');
            }
        }

        // Update counters
        if (data.total_attempts !== undefined) {
            $('.total-attempts').text(data.total_attempts);
        }
        if (data.successful_attempts !== undefined) {
            $('.successful-attempts').text(data.successful_attempts);
        }
        if (data.courses_obtained !== undefined) {
            $('.courses-obtained').text(data.courses_obtained.length);
        }
    }

    // Form enhancements
    function setupFormEnhancements() {
        // Course selection helper
        $('#target_courses').on('change', function() {
            var selected = $(this).val();
            var count = selected ? selected.length : 0;
            var helpText = $(this).siblings('.form-text');
            if (helpText.length > 0) {
                helpText.text('Dipilih: ' + count + ' mata kuliah. Gunakan Ctrl + klik untuk memilih multiple.');
            }
        });

        // Form validation feedback
        $('form').on('submit', function() {
            $(this).find('button[type="submit"]').prop('disabled', true).html(
                '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Memproses...'
            );
        });

        // Password field toggle
        $('.password-toggle').on('click', function() {
            var passwordField = $(this).siblings('input[type="password"], input[type="text"]');
            var type = passwordField.attr('type') === 'password' ? 'text' : 'password';
            passwordField.attr('type', type);
            $(this).find('i').toggleClass('bi-eye bi-eye-slash');
        });
    }

    // WAR control functions
    function setupWarControls() {
        // Start WAR confirmation
        $('form[action*="start"]').on('submit', function(e) {
            if (!confirm('Yakin ingin memulai proses WAR KRS? Pastikan pengaturan sudah benar.')) {
                e.preventDefault();
                return false;
            }
        });

        // Stop WAR confirmation
        $('form[action*="stop"]').on('submit', function(e) {
            if (!confirm('Yakin ingin menghentikan proses WAR KRS?')) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Progress bar animations
    function animateProgressBars() {
        $('.progress-bar').each(function() {
            var width = $(this).attr('aria-valuenow') + '%';
            $(this).css('width', '0%').animate({
                width: width
            }, 1000);
        });
    }

    // Log auto-scroll
    function setupLogAutoScroll() {
        if (window.location.pathname === '/logs') {
            // Auto-scroll to bottom of logs if on first page
            var urlParams = new URLSearchParams(window.location.search);
            if (!urlParams.has('page') || urlParams.get('page') === '1') {
                $('html, body').animate({
                    scrollTop: $(document).height()
                }, 1000);
            }
        }
    }

    // Real-time log updates (if on dashboard)
    function setupLogUpdates() {
        if (window.location.pathname === '/' && $('#recent-logs').length > 0) {
            setInterval(function() {
                // Fetch latest logs via AJAX (simplified)
                // This would require an additional endpoint
            }, 10000); // Every 10 seconds
        }
    }

    // Course filter functionality
    function setupCourseFilter() {
        $('#course-filter').on('keyup', function() {
            var filter = $(this).val().toLowerCase();
            $('#target_courses option').each(function() {
                var text = $(this).text().toLowerCase();
                if (text.indexOf(filter) === -1) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    }

    // Notification system
    function showNotification(message, type = 'info') {
        var alertClass = 'alert-' + (type === 'error' ? 'danger' : type);
        var notification = $('<div class="alert ' + alertClass + ' alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>');
        
        $('body').append(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            notification.alert('close');
        }, 5000);
    }

    // Error handling for AJAX requests
    $(document).ajaxError(function(event, xhr, settings, thrownError) {
        if (xhr.status === 401) {
            showNotification('Sesi login telah berakhir. Silakan login kembali.', 'warning');
            setTimeout(function() {
                window.location.href = '/login';
            }, 2000);
        } else if (xhr.status >= 500) {
            showNotification('Terjadi kesalahan server. Silakan coba lagi.', 'error');
        }
    });

    // Initialize all functions
    setupFormEnhancements();
    setupWarControls();
    animateProgressBars();
    setupLogAutoScroll();
    setupLogUpdates();
    setupCourseFilter();
    
    // Start status updates
    updateStatus();
    setInterval(updateStatus, 5000); // Every 5 seconds

    // Page-specific initializations
    var currentPage = window.location.pathname;
    
    if (currentPage === '/') {
        // Dashboard specific
        console.log('Dashboard loaded');
    } else if (currentPage === '/settings') {
        // Settings specific
        console.log('Settings loaded');
        
        // Show selected courses count
        $('#target_courses').trigger('change');
    } else if (currentPage === '/logs') {
        // Logs specific
        console.log('Logs loaded');
    }
});

// Global utility functions
window.WarKRS = {
    showNotification: function(message, type = 'info') {
        // Same as above function, made global
    },
    
    refreshStatus: function() {
        // Force status refresh
        window.location.reload();
    },
    
    formatDateTime: function(dateString) {
        var date = new Date(dateString);
        return date.toLocaleDateString('id-ID') + ' ' + date.toLocaleTimeString('id-ID');
    }
};
