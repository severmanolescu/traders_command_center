async function loadGlobalCryptoData() {
    try {
        const response = await fetch('/api/global-crypto-data');
        const data = await response.json();

        // Update value and classification
        document.getElementById('total-market-cap-value').textContent = data.market_cap_value;

        const change = data.market_cap_change;
        const changeText = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;

        console.log('change value:', change);
        console.log('changeText:', changeText);

        const changeSpan = document.getElementById('market-cap-change-value');
        changeSpan.textContent = changeText;

        // Change color class on the parent <p>
        const changeP = document.getElementById('total-market-cap-change');
        changeP.classList.remove('text-green-500', 'text-red-500');
        changeP.classList.add(change < 0 ? 'text-red-500' : 'text-green-500');

        document.getElementById('total-market-cap-24h-change').textContent = data.market_cap_24h_change;

        document.getElementById('btc-dominance').textContent = data.btc_dominance;
        document.getElementById('eth-dominance').textContent = data.eth_dominance;

        document.getElementById('defi_market_cap').textContent = data.defi_market_cap;
        document.getElementById('defi_24h_change').textContent = data.defi_24h_change;

    } catch (error) {
        console.error('Error loading data:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadGlobalCryptoData);