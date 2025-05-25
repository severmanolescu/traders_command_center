document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing form...'); // Debug log

  const form = document.getElementById('assetForm');
  const submitBtn = document.getElementById('submitBtn');
  const formMessages = document.getElementById('formMessages');
  const successMessage = document.getElementById('successMessage');
  const errorMessage = document.getElementById('errorMessage');
  const successText = document.getElementById('successText');
  const errorText = document.getElementById('errorText');

  console.log('Form elements found:', {
    form: !!form,
    submitBtn: !!submitBtn,
    formMessages: !!formMessages
  }); // Debug log

  if (!form || !submitBtn) {
    console.error('Form or submit button not found!');
    return;
  }

  // Set default date to today
  const purchaseDateInput = document.getElementById('purchaseDate');
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  purchaseDateInput.value = now.toISOString().slice(0, 16);

  console.log('Adding click event listener to submit button...'); // Debug log

  // Handle button click directly (no form submission)
  submitBtn.addEventListener('click', async function(e) {
    console.log('Submit button clicked!'); // This should appear in console
    e.preventDefault();
    e.stopPropagation();

    const originalBtnText = submitBtn.textContent;

    try {
      // Show loading state
      submitBtn.textContent = 'Adding...';
      submitBtn.disabled = true;
      hideMessages();

      // Get form values directly (not using FormData)
      const asset = document.getElementById('asset').value;
      const amount = document.getElementById('amount').value;
      const purchasePrice = document.getElementById('purchasePrice').value;
      const purchaseDate = document.getElementById('purchaseDate').value;
      const exchange = document.getElementById('exchange').value;
      const wallet = document.getElementById('wallet').value;
      const notes = document.getElementById('notes').value;

      console.log('Form values:', { asset, amount, purchasePrice, purchaseDate, exchange, wallet, notes });

      // Basic client-side validation
      if (!asset || !amount || !purchasePrice || !purchaseDate) {
        throw new Error('Please fill in all required fields');
      }

      if (parseFloat(amount) <= 0) {
        throw new Error('Amount must be greater than 0');
      }

      if (parseFloat(purchasePrice) <= 0) {
        throw new Error('Purchase price must be greater than 0');
      }

      console.log('Making request to /add-transaction');

      // Create form data manually (like the test button)
      const formData = new FormData();
      formData.append('asset', asset);
      formData.append('amount', amount);
      formData.append('purchasePrice', purchasePrice);
      formData.append('purchaseDate', purchaseDate);
      formData.append('exchange', exchange);
      formData.append('wallet', wallet);
      formData.append('notes', notes);

      // Submit via fetch (exactly like the test button)
      const response = await fetch('/add-transaction', {
        method: 'POST',
        body: formData
      });

      console.log('Response status:', response.status);
      console.log('Response URL:', response.url);

      // Handle JSON response
      const result = await response.json();
      console.log('JSON Response:', result);

      if (response.ok) {
        showSuccess(result.success || result.message || 'Transaction added successfully!');

        // Clear form manually
        document.getElementById('asset').value = '';
        document.getElementById('amount').value = '';
        document.getElementById('purchasePrice').value = '';
        document.getElementById('exchange').value = 'binance';
        document.getElementById('wallet').value = '';
        document.getElementById('notes').value = '';

        // Reset date to current time
        purchaseDateInput.value = now.toISOString().slice(0, 16);
      } else {
        throw new Error(result.error || 'Failed to add transaction');
      }

    } catch (error) {
      console.error('Error:', error);
      showError(error.message);
    } finally {
      // Reset button
      submitBtn.textContent = originalBtnText;
      submitBtn.disabled = false;
    }
  });

  console.log('Event listener added successfully'); // Debug log

  // Cancel button handler
  document.getElementById('cancelAddAsset').addEventListener('click', function() {
    if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
      form.reset();
      hideMessages();
    }
  });

  // Reset button handler
  form.addEventListener('reset', function() {
    hideMessages();
    // Reset date to current time after form reset
    setTimeout(() => {
      purchaseDateInput.value = now.toISOString().slice(0, 16);
    }, 10);
  });

  function showSuccess(message) {
    successText.textContent = message;
    successMessage.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    formMessages.classList.remove('hidden');
  }

  function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    successMessage.classList.add('hidden');
    formMessages.classList.remove('hidden');
  }

  function hideMessages() {
    formMessages.classList.add('hidden');
    successMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');
  }
});