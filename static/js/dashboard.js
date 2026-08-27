document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard interactions
    initializeDashboard();
});

function initializeDashboard() {
    // Add any dashboard-specific interactions here
    
    // Smooth transitions for cards
    const cards = document.querySelectorAll('.stat-card, .latest-assessment-card');
    
    cards.forEach((card, index) => {
        card.style.animation = `slideUp 0.5s ease ${index * 0.1}s both`;
    });
}

// Add slide-up animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);