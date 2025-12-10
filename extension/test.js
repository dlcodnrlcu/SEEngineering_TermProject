// Since we don't have a test runner, we'll create a simple one.
// This file will be loaded by test.html

// --- Function to be tested (copied from content.js) ---
function maskPII(text) {
    if (!text) return text;
    text = text.replace(/[\w\.-]+@[\w\.-]+\.\w+/g, '[EMAIL_REDACTED]');
    text = text.replace(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g, '[PHONE_REDACTED]');
    return text;
}

// --- Test Suite ---
const testResults = [];

function test(description, fn) {
    try {
        fn();
        testResults.push({ description, status: '✅ Passed' });
    } catch (error) {
        testResults.push({ description, status: `❌ Failed`, error: error.message });
    }
}

function assertEquals(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(message || `Expected "${expected}" but got "${actual}"`);
    }
}

// --- Test Cases for maskPII ---

test('maskPII should redact a simple email address', () => {
    const input = 'My email is test@example.com.';
    const expected = 'My email is [EMAIL_REDACTED].';
    assertEquals(maskPII(input), expected);
});

test('maskPII should redact multiple email addresses', () => {
    const input = 'Contact support@service.com or admin@domain.org.';
    const expected = 'Contact [EMAIL_REDACTED] or [EMAIL_REDACTED].';
    assertEquals(maskPII(input), expected);
});

test('maskPII should redact a standard phone number', () => {
    const input = 'Call me at 123-456-7890.';
    const expected = 'Call me at [PHONE_REDACTED].';
    assertEquals(maskPII(input), expected);
});

test('maskPII should redact a phone number with parentheses and spaces', () => {
    const input = 'The number is (123) 456 7890.';
    const expected = 'The number is [PHONE_REDACTED].';
    assertEquals(maskPII(input), expected);
});

test('maskPII should redact a phone number with country code', () => {
    const input = 'Use +1 123 456 7890 for international.';
    const expected = 'Use [PHONE_REDACTED] for international.';
    assertEquals(maskPII(input), expected);
});

test('maskPII should not change text with no PII', () => {
    const input = 'This is a safe sentence.';
    const expected = 'This is a safe sentence.';
    assertEquals(maskPII(input), expected);
});

test('maskPII should return null or empty if input is so', () => {
    assertEquals(maskPII(null), null);
    assertEquals(maskPII(''), '');
});

// --- Run and Report ---
function runTests() {
    console.log("--- Running Frontend Unit Tests ---");
    testResults.forEach(result => {
        if (result.status.includes('Failed')) {
            console.error(`${result.status}: ${result.description}`);
            console.error(`   Error: ${result.error}`);
        } else {
            console.log(`${result.status}: ${result.description}`);
        }
    });
    console.log("--- Test Run Complete ---");
}

runTests();
