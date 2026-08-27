let currentStep = 1;
const totalSteps = 5;

document.addEventListener('DOMContentLoaded', function() {
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('assessmentForm');
    
    // Next button
    nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (validateCurrentStep()) {
            if (currentStep < totalSteps) {
                currentStep++;
                showStep(currentStep);
                updateProgress();
            }
        } else {
            showAlert('Please select at least one option to continue', 'warning');
        }
    });
    
    // Previous button
    prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
            updateProgress();
        }
    });
    
    // Submit button
    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (validateCurrentStep()) {
            form.submit();
        } else {
            showAlert('Please select at least one option', 'warning');
        }
    });
    
    // Show initial step
    showStep(1);
    updateProgress();
});

function showStep(stepNum) {
    // Hide all steps
    for (let i = 1; i <= totalSteps; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) step.style.display = 'none';
    }
    
    // Show current step
    const currentStepElement = document.getElementById(`step-${stepNum}`);
    if (currentStepElement) currentStepElement.style.display = 'block';
    
    // Update buttons
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    prevBtn.style.display = stepNum === 1 ? 'none' : 'flex';
    nextBtn.style.display = stepNum === totalSteps ? 'none' : 'flex';
    submitBtn.style.display = stepNum === totalSteps ? 'flex' : 'none';
}

function updateProgress() {
    const progressFill = document.getElementById('progressFill');
    const currentStepSpan = document.getElementById('currentStep');
    
    const percentage = (currentStep / totalSteps) * 100;
    progressFill.style.width = percentage + '%';
    currentStepSpan.textContent = currentStep;
}

function validateCurrentStep() {
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    const checkboxes = currentStepElement.querySelectorAll('input[type="checkbox"]');
    
    // Check if at least one checkbox is selected
    const isChecked = Array.from(checkboxes).some(cb => cb.checked);
    
    return isChecked;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `<span>${message}</span><button type="button" class="btn-close" onclick="this.parentElement.style.display='none'"><i class="fas fa-times"></i></button>`;
    
    const form = document.getElementById('assessmentForm');
    form.insertBefore(alertDiv, form.firstChild);
    
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 3000);
}