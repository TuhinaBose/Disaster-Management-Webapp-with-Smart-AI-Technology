/**
 * AI DISASTER PREDICTION INTERACTION HANDLER
 */

document.addEventListener('DOMContentLoaded', () => {
    const predictForm = document.getElementById('predict-form');
    const resultBox = document.getElementById('prediction-result-box');

    // Preset scenarios
    const presets = {
        severe_flood: { rainfall: 220, river_level: 8.8, wind_speed: 45, temperature: 28, humidity: 92, earthquake_mag: 1.2 },
        severe_cyclone: { rainfall: 140, river_level: 5.2, wind_speed: 125, temperature: 29, humidity: 88, earthquake_mag: 0.0 },
        earthquake: { rainfall: 10, river_level: 1.5, wind_speed: 15, temperature: 24, humidity: 45, earthquake_mag: 6.7 },
        normal: { rainfall: 15, river_level: 1.8, wind_speed: 20, temperature: 27, humidity: 55, earthquake_mag: 0.0 }
    };

    // Handle Preset Clicks
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const key = e.target.closest('.preset-btn').dataset.preset;
            if (presets[key]) {
                const data = presets[key];
                document.getElementById('rainfall').value = data.rainfall;
                document.getElementById('river_level').value = data.river_level;
                document.getElementById('wind_speed').value = data.wind_speed;
                document.getElementById('temperature').value = data.temperature;
                document.getElementById('humidity').value = data.humidity;
                document.getElementById('earthquake_mag').value = data.earthquake_mag;
            }
        });
    });

    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('predict-btn');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Analyzing Risk with AI...`;

            const formData = {
                rainfall: parseFloat(document.getElementById('rainfall').value || 0),
                river_level: parseFloat(document.getElementById('river_level').value || 0),
                wind_speed: parseFloat(document.getElementById('wind_speed').value || 0),
                temperature: parseFloat(document.getElementById('temperature').value || 0),
                humidity: parseFloat(document.getElementById('humidity').value || 0),
                earthquake_mag: parseFloat(document.getElementById('earthquake_mag').value || 0)
            };

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (data.success) {
                    displayResult(data.prediction);
                } else {
                    alert('Error evaluating prediction: ' + data.error);
                }
            } catch (err) {
                console.error("Prediction Error:", err);
                alert("Failed to connect to AI server. Please try again.");
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    function displayResult(pred) {
        if (!resultBox) return;

        resultBox.classList.remove('d-none');
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        const riskLevelEl = document.getElementById('res-risk-level');
        const riskScoreEl = document.getElementById('res-risk-score');
        const progressBarEl = document.getElementById('res-progress-bar');
        const recsListEl = document.getElementById('res-recommendations');

        const level = pred.risk_level;
        const score = pred.risk_score;

        riskLevelEl.textContent = level.toUpperCase() + ' RISK';
        riskScoreEl.textContent = score + '% Risk Score';

        progressBarEl.style.width = score + '%';
        progressBarEl.className = 'progress-bar progress-bar-striped progress-bar-animated ';

        if (level === 'High') {
            riskLevelEl.className = 'badge risk-badge-high fs-5';
            progressBarEl.classList.add('bg-danger');
        } else if (level === 'Medium') {
            riskLevelEl.className = 'badge risk-badge-medium fs-5';
            progressBarEl.classList.add('bg-warning');
        } else {
            riskLevelEl.className = 'badge risk-badge-low fs-5';
            progressBarEl.classList.add('bg-success');
        }

        recsListEl.innerHTML = '';
        pred.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.className = 'mb-2 text-slate-200';
            li.innerHTML = `<i class="fa-solid fa-angle-right text-cyan me-2"></i> ${rec}`;
            recsListEl.appendChild(li);
        });
    }
});
