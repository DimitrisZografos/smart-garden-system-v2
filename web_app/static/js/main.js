/**
 * Smart Garden System Web Interface
 * Main JavaScript file for common functionality
 */

// Auto-refresh system status every 30 seconds
setInterval(function() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status-text').textContent = data.system_status;
            document.getElementById('last-updated').textContent = data.last_updated;
        })
        .catch(error => console.error('Error updating status:', error));
}, 30000);

// Format date and time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format date only
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Format time only
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = new bootstrap.Alert(notification);
        alert.close();
    }, 5000);
}

// Handle form validation
function validateForm(form) {
    // Add was-validated class to show validation feedback
    form.classList.add('was-validated');
    
    // Check validity
    return form.checkValidity();
}

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});