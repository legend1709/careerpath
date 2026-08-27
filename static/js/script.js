// ==================== NAVBAR BURGER ==================== 

document.addEventListener('DOMContentLoaded', function() {
    const navbarBurger = document.getElementById('navbarBurger');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (navbarBurger) {
        navbarBurger.addEventListener('click', function() {
            navbarMenu.style.display = navbarMenu.style.display === 'flex' ? 'none' : 'flex';
            navbarBurger.classList.toggle('active');
        });
    }
});

// ==================== FLASH MESSAGE AUTO-CLOSE ==================== 

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-close after 5 seconds
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

// ==================== SMOOTH SCROLL ==================== 

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== FORM VALIDATION ==================== 

const forms = document.querySelectorAll('form');

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        let isValid = true;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = 'var(--danger-color)';
            } else {
                input.style.borderColor = '';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});