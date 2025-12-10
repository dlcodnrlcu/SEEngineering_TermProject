// --- Constants and State ---
const CONSENT_KEY = 'hasConsented';
const GUIDE_ENABLED_KEY = 'isGuideEnabled';
let hasConsent = false;
let isGuideEnabled = false;
let lastScrollTime = 0;
const SCROLL_THROTTLE_MS = 500;
let pageLoadTime = new Date();
let lastUrl = window.location.href;

// --- PII Masking ---
function maskPII(text) {
    if (!text) return text;
    text = text.replace(/[\w\.-]+@[\w\.-]+\.\w+/g, '[EMAIL_REDACTED]');
    text = text.replace(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g, '[PHONE_REDACTED]');
    return text;
}

// --- Event Logging ---
function logEvent(type, details) {
    if (!hasConsent) return;

    const logData = {
        type: type,
        details: details,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight
        }
    };

    chrome.runtime.sendMessage(logData, (response) => {
        if (chrome.runtime.lastError) {
            console.error("Message sending failed:", chrome.runtime.lastError.message);
        }
    });
}

// --- Guide UI ---
class GuideManager {
    constructor(steps) {
        this.steps = steps;
        this.currentStep = 0;
        this.highlightBox = null;
        this.tooltip = null;
        this.createUI();
    }

    createUI() {
        this.highlightBox = document.createElement('div');
        this.highlightBox.id = 'follow-me-highlight-box';
        this.highlightBox.style.position = 'absolute';
        this.highlightBox.style.border = '3px solid #4CAF50';
        this.highlightBox.style.borderRadius = '5px';
        this.highlightBox.style.zIndex = '9999';
        this.highlightBox.style.pointerEvents = 'none';
        document.body.appendChild(this.highlightBox);

        this.tooltip = document.createElement('div');
        this.tooltip.id = 'follow-me-tooltip';
        this.tooltip.style.position = 'absolute';
        this.tooltip.style.background = 'white';
        this.tooltip.style.border = '1px solid #ccc';
        this.tooltip.style.borderRadius = '5px';
        this.tooltip.style.padding = '10px';
        this.tooltip.style.zIndex = '10000';
        this.tooltip.innerHTML = `
            <div id="guide-description" style="margin-bottom: 5px;"></div>
            <button id="guide-next">Next</button>
            <button id="guide-close" style="float: right; background: none; border: none; font-size: 1.2em;">&times;</button>
        `;
        document.body.appendChild(this.tooltip);

        document.getElementById('guide-next').onclick = () => this.nextStep();
        document.getElementById('guide-close').onclick = () => this.cleanup();
    }

    showStep() {
        if (this.currentStep >= this.steps.length) {
            this.cleanup();
            return;
        }

        const step = this.steps[this.currentStep];
        const element = document.querySelector(step.selector);

        if (!element) {
            console.error(`Follow Me! - Guide element not found for selector: ${step.selector}`);
            this.cleanup();
            return;
        }

        const rect = element.getBoundingClientRect();
        this.highlightBox.style.top = `${rect.top + window.scrollY}px`;
        this.highlightBox.style.left = `${rect.left + window.scrollX}px`;
        this.highlightBox.style.width = `${rect.width}px`;
        this.highlightBox.style.height = `${rect.height}px`;

        this.tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
        this.tooltip.style.left = `${rect.left + window.scrollX}px`;
        document.getElementById('guide-description').textContent = step.description;
    }

    nextStep() {
        this.currentStep++;
        this.showStep();
    }

    cleanup() {
        if (this.highlightBox) this.highlightBox.remove();
        if (this.tooltip) this.tooltip.remove();
    }
}

async function fetchAndDisplayGuide() {
    if (!isGuideEnabled) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/guide?url=${encodeURIComponent(window.location.href)}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result = await response.json();
        if (result.status === 'success' && result.data && result.data.steps && result.data.steps.length > 0) {
            const guide = new GuideManager(result.data.steps);
            guide.showStep();
        }
    } catch (error) {
        console.error('Follow Me! - Failed to fetch or display guide:', error);
    }
}

// --- Initialization ---
function init() {
    chrome.storage.local.get([CONSENT_KEY, GUIDE_ENABLED_KEY], (result) => {
        hasConsent = !!result[CONSENT_KEY];
        isGuideEnabled = !!result[GUIDE_ENABLED_KEY];

        if (hasConsent) {
            addEventListeners();
            fetchAndDisplayGuide();
        }
    });
}

// --- Event Listeners ---
function addEventListeners() {
    document.body.addEventListener('click', (event) => {
        const target = event.target;
        // Ignore clicks on the guide UI
        if (target.id.startsWith('guide-')) return;
        logEvent('click', {
            target: {
                tagName: target.tagName,
                id: target.id,
                className: target.className,
                textContent: maskPII(target.textContent.slice(0, 100))
            }
        });
    }, true);

    document.body.addEventListener('input', (event) => {
        const target = event.target;
        if (target.type === 'password') return;
        logEvent('input', {
            target: {
                tagName: target.tagName,
                id: target.id,
                className: target.className,
            },
            value: maskPII(target.value.slice(0, 100))
        });
    }, true);

    window.addEventListener('scroll', () => {
        const now = new Date().getTime();
        if (now - lastScrollTime < SCROLL_THROTTLE_MS) return;
        lastScrollTime = now;
        logEvent('scroll', {
            scrollX: window.scrollX,
            scrollY: window.scrollY,
            scrollHeight: document.body.scrollHeight
        });
    });
}

function logPageTransition() {
    const timeSpent = new Date() - pageLoadTime;
    logEvent('page_transition', {
        from: lastUrl,
        to: document.location.href,
        timeSpentMs: timeSpent
    });
}

// --- Start Script ---
init();

// Detect URL changes for single-page applications (SPA)
setInterval(() => {
    if (lastUrl !== window.location.href) {
        // Clean up old guide before fetching a new one
        const oldGuideBox = document.getElementById('follow-me-highlight-box');
        const oldTooltip = document.getElementById('follow-me-tooltip');
        if (oldGuideBox) oldGuideBox.remove();
        if (oldTooltip) oldTooltip.remove();

        logPageTransition();
        lastUrl = window.location.href;
        pageLoadTime = new Date();
        fetchAndDisplayGuide();
    }
}, 500);

window.addEventListener('beforeunload', logPageTransition);