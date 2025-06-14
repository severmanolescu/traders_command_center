async function loadFearGreedData() {
    try {
        const response = await fetch('/api/fear-greed');
        const data = await response.json();

        // Update the gauge fill
        document.getElementById('gauge-fill').style.strokeDashoffset = data.stroke_offset;

        // Update value and classification
        document.getElementById('index-value').textContent = data.value;
        document.getElementById('index-value').style.color = data.color;
        document.getElementById('index-classification').textContent = data.classification;

        // Update timestamp
        document.getElementById('last-updated').textContent = data.last_updated;

    } catch (error) {
        console.error('Error loading data:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadFearGreedData);