// Nasrani Heritage Community - Main JavaScript

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Initialize lazy loading for images
    var lazyImages = [].slice.call(document.querySelectorAll('img[loading="lazy"]'));
    if ('IntersectionObserver' in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    lazyImage.classList.remove('lazy');
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });
        
        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    }
});

// Smooth scroll to comments
function scrollToComments() {
    document.getElementById('comments-section').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Copy link to clipboard
function copyPostLink(postUrl) {
    navigator.clipboard.writeText(postUrl).then(function() {
        // Show success message
        var toast = document.createElement('div');
        toast.className = 'alert alert-success alert-permanent position-fixed top-0 end-0 m-3';
        toast.innerHTML = '<i class="fas fa-check-circle me-2"></i>Link copied to clipboard!';
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.remove();
        }, 3000);
    }).catch(function() {
        // Fallback
        prompt('Copy this link:', postUrl);
    });
}

// Preview image before upload
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
            document.getElementById(previewId).style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Confirm action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format dates
function formatDate(date) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

// Search debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Infinite scroll for comments (if needed)
let loadingComments = false;
window.addEventListener('scroll', function() {
    if (loadingComments) return;
    
    var commentsSection = document.getElementById('comments-section');
    if (!commentsSection) return;
    
    var rect = commentsSection.getBoundingClientRect();
    var isNearBottom = rect.bottom <= window.innerHeight + 100;
    
    if (isNearBottom) {
        loadingComments = true;
        // Load more comments via AJAX
        // Implementation depends on your pagination setup
    }
});

// Category filter toggle
function toggleCategoryFilter() {
    var filter = document.getElementById('category-filter');
    if (filter) {
        filter.classList.toggle('show');
    }
}

// Save user preferences
function saveUserPreference(key, value) {
    localStorage.setItem('nasrani_' + key, JSON.stringify(value));
}

function getUserPreference(key) {
    return JSON.parse(localStorage.getItem('nasrani_' + key));
}

// Dark mode toggle (for future expansion)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    saveUserPreference('darkMode', document.body.classList.contains('dark-mode'));
}

// Print post
function printPost() {
    window.print();
}

// Share on social media
function shareOnTwitter(title, url) {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`, '_blank');
}

function shareOnFacebook(url) {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
}

function shareOnWhatsApp(title, url) {
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' - ' + url)}`, '_blank');
}
