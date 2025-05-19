 document.addEventListener('DOMContentLoaded', function() {
        // Get modals
        const buyModal = document.getElementById('buyModal');
        const sellModal = document.getElementById('sellModal');

        // Get all buy and sell buttons
        const buyButtons = document.querySelectorAll('.buy-btn');
        const sellButtons = document.querySelectorAll('.sell-btn');

        // Get close buttons
        const closeButtons = document.querySelectorAll('.close-modal');

        // Get form elements
        const buyForm = document.getElementById('buyForm');
        const sellForm = document.getElementById('sellForm');

    buyButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get asset info from data attributes
            const assetId = this.getAttribute('data-asset-id');
            const symbol = this.getAttribute('data-symbol');
            const currentPrice = this.getAttribute('data-price');

            // Clear previous event listeners to prevent duplicates
            const quantityInput = document.getElementById('buy_quantity');
            const priceInput = document.getElementById('buy_current_price');
            const oldQuantityInput = quantityInput.cloneNode(true);
            const oldPriceInput = priceInput.cloneNode(true);
            quantityInput.parentNode.replaceChild(oldQuantityInput, quantityInput);
            priceInput.parentNode.replaceChild(oldPriceInput, priceInput);

            // Get fresh references
            const newQuantityInput = document.getElementById('buy_quantity');
            const newPriceInput = document.getElementById('buy_current_price');

            // Populate hidden fields in the form
            document.getElementById('buy_asset_name').value = symbol;
            document.getElementById('buy_symbol').textContent = symbol;

            // Set initial numeric price value
            const numericPrice = parseFloat(currentPrice);
            document.getElementById('buy_price_numeric').value = numericPrice.toFixed(8);

            // Format for display
            newPriceInput.value = formatNumber(numericPrice);

            // Clear quantity field
            newQuantityInput.value = '';
            document.getElementById('buy_quantity_numeric').value = '';
            document.getElementById('buy_total_value').textContent = '$0.00';

            // Helper functions for formatting
            function formatNumber(value) {
                return new Intl.NumberFormat('en-US').format(value);
            }

            function parseCurrency(value) {
                return parseFloat(value.replace(/[^\d.-]/g, '')) || 0;
            }

            function formatCurrency(value) {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(value);
            }

            // Handle quantity input with formatting
            newQuantityInput.addEventListener('input', function() {
                // Get the current value
                let inputValue = this.value;

                // Remove any non-numeric characters except the decimal point
                inputValue = inputValue.replace(/[^\d.]/g, '');

                // Ensure only one decimal point
                const parts = inputValue.split('.');
                if (parts.length > 2) {
                    inputValue = parts[0] + '.' + parts.slice(1).join('');
                }

                // Store this cleaned value for calculations
                let numericValue;

                // Special handling for decimal input in progress
                if (inputValue === '' || inputValue === '.') {
                    // User is starting with a decimal point or has cleared the field
                    numericValue = 0;
                    this.value = inputValue; // Keep as-is for user experience
                    document.getElementById('buy_quantity_numeric').value = '';
                } else {
                    // Parse the value to a number for calculations
                    numericValue = parseFloat(inputValue);

                    // Store the numeric value for form submission
                    document.getElementById('buy_quantity_numeric').value = numericValue.toFixed(8);

                    // Format display differently based on whether we're dealing with a decimal
                    if (inputValue.includes('.')) {
                        // For decimal numbers, preserve the decimal part exactly as typed
                        const [intPart, decPart] = inputValue.split('.');
                        // Format only the integer part
                        const formattedInt = intPart === '' ? '0' : formatNumber(parseInt(intPart));
                        this.value = formattedInt + '.' + decPart;
                    } else {
                        // For whole numbers, format normally
                        this.value = formatNumber(numericValue);
                    }
                }

                // Calculate and update total
                updateTotal();
            });

            // Handle price input with formatting
            newPriceInput.addEventListener('input', function() {
                // Store raw numeric value first
                const rawValue = this.value.replace(/[^\d.]/g, '');
                const numericValue = parseFloat(rawValue) || 0;
                document.getElementById('buy_price_numeric').value = numericValue.toFixed(8);

                // Skip formatting if emptying the field
                if (rawValue === '') {
                    this.value = '';
                } else {
                    // Format for display with commas
                    this.value = formatNumber(numericValue);
                }

                // Calculate and update total
                updateTotal();
            });

            // Function to update the total display
            function updateTotal() {
                const price = parseFloat(document.getElementById('buy_price_numeric').value) || 0;
                const quantity = parseFloat(document.getElementById('buy_quantity_numeric').value) || 0;
                const total = price * quantity;
                document.getElementById('buy_total_value').textContent = formatCurrency(total);
            }

            // Handle form submission
            document.getElementById('buyForm').addEventListener('submit', function(e) {
                // Form is already set up to submit the hidden numeric fields
                // No need to prevent default
            });

            // Show the modal
            buyModal.classList.remove('hidden');
        });
    });

    sellButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get asset info from data attributes
            const assetId = this.getAttribute('data-asset-id');
            const symbol = this.getAttribute('data-symbol');
            const currentPrice = this.getAttribute('data-price');
            const maxQuantity = this.getAttribute('data-holdings');

            // Clear previous event listeners to prevent duplicates
            const quantityInput = document.getElementById('sell_quantity');
            const oldQuantityInput = quantityInput.cloneNode(true);
            quantityInput.parentNode.replaceChild(oldQuantityInput, quantityInput);

            // Get fresh references
            const newQuantityInput = document.getElementById('sell_quantity');

            // Populate hidden fields in the form
            document.getElementById('sell_asset_id').value = symbol;
            document.getElementById('sell_symbol').textContent = symbol;

            // Set initial numeric price value
            const numericPrice = parseFloat(currentPrice);
            document.getElementById('sell_current_price').textContent = formatCurrency(numericPrice);

            // Add hidden fields for numeric values (need to add these to your HTML)
            if (!document.getElementById('sell_price_numeric')) {
                const priceNumericInput = document.createElement('input');
                priceNumericInput.type = 'hidden';
                priceNumericInput.id = 'sell_price_numeric';
                priceNumericInput.name = 'price';
                document.getElementById('sellForm').appendChild(priceNumericInput);
            }
            document.getElementById('sell_price_numeric').value = numericPrice.toFixed(8);

            if (!document.getElementById('sell_quantity_numeric')) {
                const quantityNumericInput = document.createElement('input');
                quantityNumericInput.type = 'hidden';
                quantityNumericInput.id = 'sell_quantity_numeric';
                quantityNumericInput.name = 'quantity';
                document.getElementById('sellForm').appendChild(quantityNumericInput);
            }

            // Clear quantity field
            newQuantityInput.value = '';
            document.getElementById('sell_quantity_numeric').value = '';
            document.getElementById('sell_total_value').textContent = '$0.00';

            // Set max quantity display
            document.getElementById('sell_max_quantity').textContent = formatNumber(parseFloat(maxQuantity));

            // Helper functions for formatting
            function formatNumber(value) {
                return new Intl.NumberFormat('en-US').format(value);
            }

            function parseCurrency(value) {
                return parseFloat(value.replace(/[^\d.-]/g, '')) || 0;
            }

            function formatCurrency(value) {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(value);
            }

            // Handle quantity input with proper decimal handling
            newQuantityInput.addEventListener('input', function() {
                // Get the current cursor position
                const cursorPos = this.selectionStart;
                const previousLength = this.value.length;

                // Store the current input value
                let rawValue = this.value;

                // Clean input: keep only digits and at most one decimal point
                let cleanValue = '';
                let decimalCount = 0;

                for (let i = 0; i < rawValue.length; i++) {
                    const char = rawValue[i];
                    if (char === '.' && decimalCount === 0) {
                        cleanValue += char;
                        decimalCount++;
                    } else if (/\d/.test(char)) {
                        cleanValue += char;
                    }
                }

                // Parse as float for calculations or 0 if empty/invalid
                const numericValue = cleanValue === '' || cleanValue === '.' ? 0 : parseFloat(cleanValue);

                // Enforce max quantity
                const maxQty = parseFloat(maxQuantity);
                let finalValue = numericValue;

                // Only apply max limit if we have a complete number (not in the middle of typing)
                if (!(cleanValue.endsWith('.') || cleanValue === '')) {
                    finalValue = Math.min(numericValue, maxQty);
                }

                // Store the numeric value for form submission
                document.getElementById('sell_quantity_numeric').value =
                    (cleanValue === '' || cleanValue === '.') ? '' : finalValue.toFixed(8);

                // Keep input as is when empty or just a decimal point
                // This is important for UX when typing decimals
                if (cleanValue === '' || cleanValue === '.') {
                    this.value = cleanValue;
                } else {
                    // Handle formatting differently based on whether we're dealing with a decimal
                    if (cleanValue.includes('.')) {
                        // For decimal numbers, only format the integer part
                        const [intPart, decimalPart] = cleanValue.split('.');
                        const formattedInt = intPart === '' ? '' : formatNumber(parseInt(intPart));
                        this.value = formattedInt + '.' + decimalPart;
                    } else {
                        // For whole numbers, format the entire value
                        this.value = formatNumber(finalValue);
                    }
                }

                // Adjust cursor position after formatting
                // This helps maintain cursor position after formatting changes the length
                const lengthDiff = this.value.length - previousLength;
                const newPosition = cursorPos + lengthDiff;
                this.setSelectionRange(newPosition, newPosition);

                // Calculate and update total value display
                updateTotal();
            });

            // Function to update the total display
            function updateTotal() {
                const price = numericPrice;
                const quantityValue = document.getElementById('sell_quantity_numeric').value;
                const quantity = quantityValue === '' ? 0 : parseFloat(quantityValue);
                const total = price * quantity;
                document.getElementById('sell_total_value').textContent = formatCurrency(total);
            }

            // Handle form submission
            document.getElementById('sellForm').addEventListener('submit', function(e) {
                // Ensure quantity is valid before submitting
                const quantityValue = document.getElementById('sell_quantity_numeric').value;
                if (quantityValue === '' || parseFloat(quantityValue) <= 0) {
                    e.preventDefault();
                    alert('Please enter a valid quantity greater than 0');
                    return false;
                }
                // Form will submit the hidden numeric fields
            });

            // Show the modal
            sellModal.classList.remove('hidden');
        });
    });
    // Close modal functionality
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('buyModal').classList.add('hidden');
            document.getElementById('sellModal').classList.add('hidden');
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === buyModal) {
            buyModal.classList.add('hidden');
        }
        if (event.target === sellModal) {
            sellModal.classList.add('hidden');
        }
    });
});