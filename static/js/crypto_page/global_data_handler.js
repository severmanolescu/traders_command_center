async function loadGlobalCryptoData() {
    try {
        const response = await fetch('/api/global-crypto-data');
        const data = await response.json();

        // Update value and classification
        document.getElementById('total-market-cap-value').textContent = data.market_cap_value;
        document.getElementById('total-market-cap-change').style.color = data.market_cap_change;
        document.getElementById('total-market-cap-24h-change').textContent = data.market_cap_24h_change;
        document.getElementById('btc-dominance').textContent = data.btc_dominance;
        document.getElementById('eth-dominance').textContent = data.eth_dominance;

    } catch (error) {
        console.error('Error loading data:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadGlobalCryptoData);