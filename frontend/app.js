// -------------------------------------------------------------
//  Configuration
// -------------------------------------------------------------
const API_BASE = 'http://localhost:8000';

// -------------------------------------------------------------
//  DOM references
// -------------------------------------------------------------
const form = document.getElementById('recommendForm');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const resultsDiv = document.getElementById('results');

// -------------------------------------------------------------
//  Form submission
// -------------------------------------------------------------
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const userInput = document.getElementById('userInput').value.trim();
  const mode = document.getElementById('modeSelect').value;
  const preferencesRaw = document.getElementById('preferencesInput').value.trim();

  // Parse optional preferences JSON
  let preferences = null;
  if (preferencesRaw) {
    try {
      preferences = JSON.parse(preferencesRaw);
    } catch {
      alert('Invalid JSON for preferences. Please fix or leave empty.');
      return;
    }
  }

  if (!userInput) {
    alert('Please describe what you are looking for.');
    return;
  }

  // Disable UI
  submitBtn.disabled = true;
  loading.style.display = 'block';
  resultsDiv.innerHTML = '';
  resultsDiv.classList.remove('active');

  try {
    const response = await fetch(`${API_BASE}/api/v1/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: userInput,
        preferences: preferences,
        mode: mode,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error (${response.status}): ${errorText}`);
    }

    const data = await response.json();
    displayResults(data, mode);

  } catch (err) {
    resultsDiv.innerHTML = `
      <div class="result-card error">
        <strong>❌ Error</strong>
        <p>${err.message}</p>
        <p style="font-size:0.85rem; margin-top:8px;">
          Make sure the backend is running at ${API_BASE}
        </p>
      </div>
    `;
    resultsDiv.classList.add('active');
  } finally {
    submitBtn.disabled = false;
    loading.style.display = 'none';
  }
});

// -------------------------------------------------------------
//  Render results
// -------------------------------------------------------------
function displayResults(data, mode) {
  const recs = data.recommendations;

  // If recommendations is a plain string (chain or crew raw output)
  if (typeof recs === 'string') {
    resultsDiv.innerHTML = `
      <div class="result-card">
        <h3>📋 Recommendations <span class="mode-tag">${mode}</span></h3>
        <p style="white-space: pre-wrap;">${recs}</p>
      </div>
    `;
    resultsDiv.classList.add('active');
    return;
  }

  // If it's an array of objects (graph mode)
  if (Array.isArray(recs)) {
    if (recs.length === 0) {
      resultsDiv.innerHTML = `<div class="result-card"><p>No recommendations found.</p></div>`;
      resultsDiv.classList.add('active');
      return;
    }

    let html = `<div style="margin-bottom:12px;"><span class="mode-tag">${mode}</span> <span style="color:#b5b5d9;">${recs.length} recommendations</span></div>`;
    recs.forEach((item, idx) => {
      const title = item.title || item.name || `Recommendation #${idx+1}`;
      const desc = item.overview || item.description || item.reasoning || '';
      const extra = item.rating ? `⭐ ${item.rating}` : '';
      html += `
        <div class="result-card">
          <h3>${idx+1}. ${title}</h3>
          ${desc ? `<p>${desc}</p>` : ''}
          ${extra ? `<div class="meta">${extra}</div>` : ''}
        </div>
      `;
    });
    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('active');
    return;
  }

  // Fallback: show raw JSON
  resultsDiv.innerHTML = `
    <div class="result-card">
      <h3>📊 Raw Response <span class="mode-tag">${mode}</span></h3>
      <pre style="background:rgba(0,0,0,0.3); padding:12px; border-radius:12px; overflow-x:auto; color:#cfcfef;">${JSON.stringify(recs, null, 2)}</pre>
    </div>
  `;
  resultsDiv.classList.add('active');
}

// -------------------------------------------------------------
//  Health check (on load)
// -------------------------------------------------------------
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`);
    if (res.ok) {
      console.log('✅ Backend is healthy');
    } else {
      console.warn('⚠️ Backend health check failed');
    }
  } catch {
    console.warn('⚠️ Cannot reach backend. Is it running?');
  }
}
checkHealth();