// News Summarizer Web App JavaScript

class NewsSummarizerApp {
    constructor() {
        this.currentStep = 1;
        this.maxSteps = 4;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadVoices();
        this.formatPhoneInput();
    }

    bindEvents() {
        const form = document.getElementById('newsForm');
        const mobileInput = document.getElementById('mobile_number');
        
        form.addEventListener('submit', (e) => this.handleSubmit(e));
        mobileInput.addEventListener('input', (e) => this.formatPhoneNumber(e));
        
        // Add real-time validation
        mobileInput.addEventListener('blur', () => this.validatePhoneNumber());
    }

    formatPhoneInput() {
        const phoneInput = document.getElementById('mobile_number');
        phoneInput.addEventListener('keypress', (e) => {
            // Allow numbers, characters, space, parentheses
            const allowedChars = /^[0-9\(\)\s]+$/;
            if (!allowedChars.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    formatPhoneNumber(event) {
        let value = event.target.value;
        
        // If it's a Telegram username, don't format it
        if (value.startsWith('@')) {
            event.target.value = value;
            return;
        }
        
        // Format phone numbers
        value = value.replace(/\D/g, '');
        
        event.target.value = value;
    }

    validatePhoneNumber() {
        const phoneInput = document.getElementById('mobile_number');
        const value = phoneInput.value.trim();
        
        // Check if it's a Telegram username (starts with @)
        // if (value.startsWith('@')) {
        //     if (value.length < 2) {
        //         this.showFieldError(phoneInput, 'Please enter a valid Telegram username');
        //         return false;
        //     } else {
        //         this.clearFieldError(phoneInput);
        //         return true;
        //     }
        // }
        
        // // Check if it's a phone number
        // const numericValue = value.replace(/\D/g, '');
        // if (numericValue.length < 10) {
        //     this.showFieldError(phoneInput, 'Please enter a valid Telegram username (@username) or phone number with country code');
        //     return false;
        // } else {
        //     this.clearFieldError(phoneInput);
        //     return true;
        // }
        return true;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        field.style.borderColor = '#f56565';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#f56565';
        errorDiv.style.fontSize = '0.85rem';
        errorDiv.style.marginTop = '5px';
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.style.borderColor = '';
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const data = await response.json();
            
            if (data.success) {
                this.populateVoiceSelect(data.voices, data.recommended);
            }
        } catch (error) {
            console.log('Could not load voices:', error);
        }
    }

    populateVoiceSelect(voices, recommended) {
        const voiceSelect = document.getElementById('voice');
        
        // Clear existing options except the first few
        while (voiceSelect.children.length > 5) {
            voiceSelect.removeChild(voiceSelect.lastChild);
        }
        
        // Add recommended voices
        Object.entries(recommended).forEach(([type, voiceId]) => {
            const voice = voices.find(v => v.id === voiceId);
            if (voice) {
                const option = document.createElement('option');
                option.value = voiceId;
                option.textContent = `${voice.name} (${voice.gender} - ${voice.language})`;
                voiceSelect.appendChild(option);
            }
        });
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        // Validate form
        // if (!this.validatePhoneNumber()) {
        //     return;
        // }
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        // Show loading state
        this.showLoadingState();
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(data)
            });
            
            const result = await response.json();
            
            if (result.success && result.task_id) {
                // Start polling for task status
                this.pollTaskStatus(result.task_id);
            } else {
                this.showErrorState(result.error || 'An error occurred');
            }
        } catch (error) {
            this.showErrorState('Network error: ' + error.message);
        }
    }

    async pollTaskStatus(taskId) {
        try {
            const response = await fetch(`/task/${taskId}`);
            const taskData = await response.json();
            
            if (taskData.success) {
                // Update progress
                this.updateProgress(taskData.progress, taskData.message);
                
                if (taskData.status === 'completed') {
                    // Task completed successfully
                    this.showResultsState(taskData.result);
                } else if (taskData.status === 'failed') {
                    // Task failed
                    this.showErrorState(taskData.message);
                } else {
                    // Task still processing, continue polling
                    setTimeout(() => this.pollTaskStatus(taskId), 2000);
                }
            } else {
                this.showErrorState('Failed to check task status');
            }
        } catch (error) {
            this.showErrorState('Error checking task status: ' + error.message);
        }
    }

    updateProgress(progress, message) {
        // Update progress bar
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        // Update progress text
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${progress}% - ${message}`;
        }
    }

    showLoadingState() {
        this.hideAllStates();
        document.getElementById('loadingState').classList.remove('hidden');
        
        // Animate through loading steps
        this.animateLoadingSteps();
    }

    animateLoadingSteps() {
        const steps = document.querySelectorAll('.step');
        let currentStep = 0;
        
        const stepInterval = setInterval(() => {
            // Remove active class from all steps
            steps.forEach(step => step.classList.remove('active'));
            
            // Add active class to current step
            if (steps[currentStep]) {
                steps[currentStep].classList.add('active');
            }
            
            currentStep++;
            
            if (currentStep >= steps.length) {
                clearInterval(stepInterval);
            }
        }, 2000);
    }

    showResultsState(result) {
        this.hideAllStates();
        const resultsState = document.getElementById('resultsState');
        
        // Update result details
        document.getElementById('articlesCount').textContent = result.articles_count || 0;
        document.getElementById('audioStatus').textContent = result.audio_created ? 'Audio generated' : 'Audio generation failed';
        
        // Update Telegram status (priority)
        const telegramStatus = document.getElementById('telegramStatus');
        const telegramMessage = document.getElementById('telegramMessage');
        telegramMessage.textContent = result.telegram_message || 'Not configured';
        
        if (result.telegram_sent) {
            telegramStatus.style.color = '#48bb78';
            telegramMessage.textContent = result.telegram_message + (result.telegram_audio_sent ? ' (with audio)' : '');
        } else {
            telegramStatus.style.color = '#f56565';
        }
        
        // Update WhatsApp status (fallback)
        const whatsappStatus = document.getElementById('whatsappStatus');
        const whatsappMessage = document.getElementById('whatsappMessage');
        whatsappMessage.textContent = result.whatsapp_message || 'Not configured';
        
        if (result.whatsapp_sent) {
            whatsappStatus.style.color = '#48bb78';
        } else {
            whatsappStatus.style.color = '#f56565';
        }
        
        // Set up download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (result.audio_url) {
            downloadBtn.href = result.audio_url;
            downloadBtn.style.display = 'inline-flex';
        } else {
            downloadBtn.style.display = 'none';
        }
        
        resultsState.classList.remove('hidden');
        
        // Auto-download the audio file
        if (result.audio_url) {
            setTimeout(() => {
                window.open(result.audio_url, '_blank');
            }, 1000);
        }
    }

    showErrorState(errorMessage) {
        this.hideAllStates();
        const errorState = document.getElementById('errorState');
        document.getElementById('errorMessage').textContent = errorMessage;
        errorState.classList.remove('hidden');
    }

    hideAllStates() {
        const states = ['loadingState', 'resultsState', 'errorState'];
        states.forEach(stateId => {
            document.getElementById(stateId).classList.add('hidden');
        });
        
        // Reset form visibility
        document.querySelector('.form-container').style.display = 'block';
    }

    resetForm() {
        // Hide all states and show form
        this.hideAllStates();
        document.querySelector('.form-container').style.display = 'block';
        
        // Reset form
        document.getElementById('newsForm').reset();
        
        // Clear any field errors
        const inputs = document.querySelectorAll('.form-input');
        inputs.forEach(input => this.clearFieldError(input));
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Modal functions
function showAbout() {
    document.getElementById('aboutModal').classList.remove('hidden');
}

function hideAbout() {
    document.getElementById('aboutModal').classList.add('hidden');
}

// Global reset function for buttons
function resetForm() {
    if (window.app) {
        window.app.resetForm();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NewsSummarizerApp();
});

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('aboutModal');
    if (e.target === modal) {
        hideAbout();
    }
});

// Handle escape key for modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideAbout();
    }
});
