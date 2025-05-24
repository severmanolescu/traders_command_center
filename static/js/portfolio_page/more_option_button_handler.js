document.addEventListener('DOMContentLoaded', function() {
  // Get the dropdown menu element
  const dropdownMenu = document.getElementById('dropdown-menu');

  // Check if dropdown menu exists
  if (!dropdownMenu) {
    console.error("Dropdown menu element with ID 'dropdown-menu' not found in the document");
    return; // Exit early if element not found
  }

  let currentAssetSymbol = null;

  // Handle clicks anywhere on the document to close dropdown
  document.addEventListener('click', function(event) {
    if (!event.target.closest('.more-options-btn') && !event.target.closest('#dropdown-menu')) {
      dropdownMenu.classList.add('hidden');
    }
  });

  // Handle more-options button clicks
  document.querySelectorAll('.more-options-btn').forEach(button => {
    button.addEventListener('click', function(event) {
      event.stopPropagation();

      // Get the asset ID from the data attribute
      const dropdownId = this.getAttribute('data-dropdown-id');
      if (dropdownId) {
        const assetId = dropdownId.replace('dropdown-', '');
        currentAssetSymbol = assetId;

        // Position and display the dropdown
        positionDropdownMenu(this, dropdownMenu);
      }
    });
  });

  // Handle action button clicks - check each element exists before adding listeners
  const viewDetailsOption = dropdownMenu.querySelector('.view-details-option');
  if (viewDetailsOption) {
    viewDetailsOption.addEventListener('click', function() {
      viewDetails(currentAssetSymbol);
    });
  }

  const transactionHistoryOption = dropdownMenu.querySelector('.transaction-history-option');
  if (transactionHistoryOption) {
    transactionHistoryOption.addEventListener('click', function() {
      showTransactionHistory(currentAssetSymbol);
    });
  }

  const exportDataOption = dropdownMenu.querySelector('.export-data-option');
  if (exportDataOption) {
    exportDataOption.addEventListener('click', function() {
      exportData(currentAssetSymbol);
    });
  }

  const deleteAssetOption = dropdownMenu.querySelector('.delete-asset-option');
  if (deleteAssetOption) {
    deleteAssetOption.addEventListener('click', function() {
      deleteAsset(currentAssetSymbol);
    });
  }
});

// Function to position the dropdown menu next to the button
function positionDropdownMenu(button, dropdownMenu) {
  // Safety check
  if (!button || !dropdownMenu) {
    console.error("Button or dropdown menu is missing");
    return;
  }

  // Get button position
  const buttonRect = button.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

  // Position the dropdown menu
  dropdownMenu.style.position = 'absolute';
  dropdownMenu.style.top = (buttonRect.bottom + scrollTop) + 'px';
  dropdownMenu.style.left = (buttonRect.left + scrollLeft) + 'px';

  // Check if dropdown would go off the right edge of the screen
  if (buttonRect.left + dropdownMenu.offsetWidth > window.innerWidth) {
    dropdownMenu.style.left = (buttonRect.right - dropdownMenu.offsetWidth + scrollLeft) + 'px';
  }

  // Check if dropdown would go off the bottom of the screen
  if (buttonRect.bottom + dropdownMenu.offsetHeight > window.innerHeight) {
    dropdownMenu.style.top = (buttonRect.top - dropdownMenu.offsetHeight + scrollTop) + 'px';
  }

  // Show the dropdown menu
  dropdownMenu.classList.remove('hidden');
}

// Action functions with safety checks
function viewDetails(currentAssetSymbol) {
  console.log('View details for asset:', currentAssetSymbol);
  const dropdownMenu = document.getElementById('dropdown-menu');
  if (dropdownMenu) dropdownMenu.classList.add('hidden');

  // Navigate to crypto details page
  window.location.href = `/crypto/details?id=${currentAssetSymbol}`;
}

function showTransactionHistory(currentAssetSymbol) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    // Create expanded container
    const expandedTable = document.createElement('div');
    expandedTable.className = 'expanded-table';

    // Create header with close button
    const header = document.createElement('div');
    header.className = 'expanded-header';

    const title = document.createElement('h2');
    title.className = 'text-xl font-semibold';
    title.textContent = `${currentAssetSymbol} Transaction History`; // Show specific symbol

    const closeBtn = document.createElement('button');
    closeBtn.className = 'text-gray-400 hover:text-white focus:outline-none';
    closeBtn.innerHTML = '&times;';
    closeBtn.style.fontSize = '24px';

    header.appendChild(title);
    header.appendChild(closeBtn);

    // Create container for the table
    const tableContainer = document.createElement('div');
    tableContainer.className = 'expanded-container';

    // Show loading state
    tableContainer.innerHTML = '<div class="py-8 text-center text-gray-400">Loading transactions...</div>';

    // Add all elements to the expanded table
    expandedTable.appendChild(header);
    expandedTable.appendChild(tableContainer);

    // Add expanded table to body
    document.body.appendChild(expandedTable);

    // Fetch filtered transactions from backend
    fetch(`/transactions/${currentAssetSymbol}`)
        .then(response => response.json())
        .then(transactions => {
            // Clone the original table structure
            const originalTable = document.querySelector('#transactionTable').closest('table');
            const clonedTable = originalTable.cloneNode(true);

            // Clear the tbody and populate with filtered data
            const tbody = clonedTable.querySelector('tbody');
            tbody.innerHTML = ''; // Clear existing content

            if (transactions.length === 0) {
                // No transactions found
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="py-4 text-center text-gray-400">No transactions found for ${currentAssetSymbol}</td>
                    </tr>
                `;
            } else {
                // Add filtered transactions
                transactions.forEach(tx => {
                    const row = document.createElement('tr');
                    row.className = 'border-b border-gray-700 hover:bg-gray-750';

                    const actionClass = tx.action === 'BUY' ? 'text-green-500 bg-green-500' : 'text-red-500 bg-red-500';

                    row.innerHTML = `
                        <td class="py-3 pr-4 text-sm">${tx.datetime}</td>
                        <td class="py-3 pr-4">
                            <span class="${actionClass} px-2 py-1 rounded text-xs font-medium bg-opacity-20">
                                ${tx.action}
                            </span>
                        </td>
                        <td class="py-3 pr-4 font-medium">${tx.symbol}</td>
                        <td class="py-3 pr-4 text-sm">${tx.amount}</td>
                        <td class="py-3 pr-4 text-sm">${tx.price}</td>
                        <td class="py-3 pr-4 text-sm">$${tx.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        <td class="py-3 pr-4 text-sm">
                            <span class="px-2 py-1 rounded-full bg-green-500 bg-opacity-20 text-green-500 text-xs">${tx.status}</span>
                        </td>
                    `;

                    tbody.appendChild(row);
                });
            }

            // Replace loading message with the table
            tableContainer.innerHTML = '';
            tableContainer.appendChild(clonedTable);
        })
        .catch(error => {
            console.error('Error fetching transactions:', error);
            tableContainer.innerHTML = '<div class="py-8 text-center text-red-400">Error loading transactions. Please try again.</div>';
        });

    // Add event listener to close button
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(overlay);
        document.body.removeChild(expandedTable);
    });

    // Add event listener to overlay for closing
    overlay.addEventListener('click', function() {
        document.body.removeChild(overlay);
        document.body.removeChild(expandedTable);
    });
}


async function exportData(currentAssetSymbol) {
    console.log('Export data for asset:', currentAssetSymbol);

    // Close dropdown
    const dropdownMenu = document.getElementById('dropdown-menu');
    if (dropdownMenu) dropdownMenu.classList.add('hidden');

    // Show loading state
    const exportBtn = document.querySelector('[onclick*="exportData"]');
    const originalText = exportBtn ? exportBtn.textContent : '';

    try {
        if (exportBtn) {
            exportBtn.textContent = 'Exporting...';
            exportBtn.disabled = true;
        }

        const exportSymbol = currentAssetSymbol || 'all';
        const downloadUrl = `/export/transactions/${exportSymbol}`;

        // Check if the export is successful first
        const response = await fetch(downloadUrl, { method: 'HEAD' });

        if (response.ok) {
            // If successful, trigger download
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            console.log('Export completed successfully');
        } else {
            throw new Error('Export failed');
        }

    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export data. Please try again.');
    } finally {
        // Reset button
        if (exportBtn) {
            exportBtn.textContent = originalText;
            exportBtn.disabled = false;
        }
    }
}

function deleteAsset(currentAssetSymbol) {
  if (confirm('Are you sure you want to delete this asset from your portfolio?')) {
    console.log('Delete asset:', currentAssetSymbol);
    // Your implementation here
  }
  const dropdownMenu = document.getElementById('dropdown-menu');
  if (dropdownMenu) dropdownMenu.classList.add('hidden');
}