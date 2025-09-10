// i18n
const translations = {
    en: {
        title: "Internship Recommender",
        qualLabel: "Qualification:",
        branchLabel: "Branch:",
        pinLabel: "Pincode:",
        emojiLabel: "Interest Emoji:",
        submitBtn: "Get Recommendations",
        langToggle: "हिंदी"
    },
    hi: {
        title: "इंटर्नशिप अनुशंसक",
        qualLabel: "योग्यता:",
        branchLabel: "शाखा:",
        pinLabel: "पिनकोड:",
        emojiLabel: "रुचि इमोजी:",
        submitBtn: "अनुशंसाएं प्राप्त करें",
        langToggle: "English"
    }
};

let currentLang = 'en';

function setLanguage(lang) {
    currentLang = lang;
    document.getElementById('title').textContent = translations[lang].title;
    document.getElementById('qual-label').textContent = translations[lang].qualLabel;
    document.getElementById('branch-label').textContent = translations[lang].branchLabel;
    document.getElementById('pin-label').textContent = translations[lang].pinLabel;
    document.getElementById('emoji-label').textContent = translations[lang].emojiLabel;
    document.getElementById('submit-btn').textContent = translations[lang].submitBtn;
    document.getElementById('lang-toggle').textContent = translations[lang].langToggle;
}

document.getElementById('lang-toggle').addEventListener('click', () => {
    const newLang = currentLang === 'en' ? 'hi' : 'en';
    setLanguage(newLang);
});

// Voice-to-text
document.getElementById('voice-btn').addEventListener('click', () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = currentLang === 'hi' ? 'hi-IN' : 'en-US';
    recognition.start();
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('emoji').value = transcript;
    };
});

// API base URL - update this with your deployed backend URL
const API_BASE_URL = 'https://your-render-app.onrender.com'; // Replace with your Render backend URL after deployment

// Fix branch value mapping to match backend expected values
document.getElementById('input-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        qualification: document.getElementById('qualification').value,
        branch: document.getElementById('branch').value,
        pincode: parseInt(document.getElementById('pincode').value),
        interest_emoji: document.getElementById('emoji').value
    };

    // Map branch to backend expected values if needed
    if (data.branch === 'Mechanical') data.branch = 'Mechanical';
    else if (data.branch === 'Electrical') data.branch = 'Electrical';
    else if (data.branch === 'Civil') data.branch = 'Civil';
    else if (data.branch === 'Computer Science') data.branch = 'Computer Science';
    else if (data.branch === 'Commerce') data.branch = 'Commerce';
    else if (data.branch === 'Arts') data.branch = 'Arts';

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        displayRecommendations(result.recommendations);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('output').innerHTML = '<p>Error fetching recommendations.</p>';
    }
});

// Form submit
document.getElementById('input-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        qualification: document.getElementById('qualification').value,
        branch: document.getElementById('branch').value,
        pincode: parseInt(document.getElementById('pincode').value),
        interest_emoji: document.getElementById('emoji').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        displayRecommendations(result.recommendations);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('output').innerHTML = '<p>Error fetching recommendations.</p>';
    }
});

// Display recommendations
function displayRecommendations(recs) {
    const output = document.getElementById('output');
    output.innerHTML = '<h2>Recommendations</h2>';
    recs.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.innerHTML = `
            <div class="recommendation-title">${rec.title}</div>
            <div class="recommendation-details">
                Qualification: ${rec.required_qualification}<br>
                Branch: ${rec.required_branch}<br>
                Pincode: ${rec.pincode}<br>
                Stipend: ₹${rec.stipend}<br>
                Distance: ${rec.distance_km ? rec.distance_km.toFixed(2) + ' km' : 'N/A'}<br>
                Score: ${rec.score.toFixed(2)}
            </div>
            <button onclick="shareRec('${rec.title}', '${rec.required_qualification}')">Share</button>
            <button onclick="savePDF('${rec.title}', '${rec.required_qualification}', ${rec.stipend})">Save PDF</button>
        `;
        output.appendChild(card);
    });
}

// Share
function shareRec(title, qual) {
    if (navigator.share) {
        navigator.share({
            title: 'Internship Recommendation',
            text: `Check out this internship: ${title} requiring ${qual}`
        });
    } else {
        alert('Sharing not supported');
    }
}

// Save PDF (simple alert for now)
function savePDF(title, qual, stipend) {
    alert(`PDF saved for ${title}`);
    // Implement jsPDF here if needed
}

// PWA install
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Show install button if desired
});

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js');
    });
}
