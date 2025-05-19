document.addEventListener('DOMContentLoaded', function() {
  const viewAllBtn = document.getElementById('viewAllBtn');
  const showMoreBtn = document.getElementById('showMoreBtn');
  const extraRows = document.querySelectorAll('.transaction-extra-row');
  const showMoreLess = document.getElementById('showMoreLess');

  // Only show the "Show more" button if there are more than 5 transactions
  if (extraRows.length === 0) {
    showMoreLess.classList.add('hidden');
  }

  // Function to toggle hidden rows
  showMoreBtn.addEventListener('click', function() {
    extraRows.forEach(row => {
      row.classList.toggle('hidden');
    });

    if (showMoreBtn.textContent.includes('Show more')) {
      showMoreBtn.textContent = 'Show less';
    } else {
      showMoreBtn.textContent = 'Show more';

      // Scroll back to the top of the table when showing less
      document.querySelector('#transactionTable').scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Function to create full-screen version of the table
  viewAllBtn.addEventListener('click', function() {
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
    title.textContent = 'All Transactions';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'text-gray-400 hover:text-white focus:outline-none';
    closeBtn.innerHTML = '&times;';
    closeBtn.style.fontSize = '24px';

    header.appendChild(title);
    header.appendChild(closeBtn);

    // Create container for the table
    const tableContainer = document.createElement('div');
    tableContainer.className = 'expanded-container';

    // Clone the table
    const originalTable = document.querySelector('#transactionTable').closest('table');
    const clonedTable = originalTable.cloneNode(true);

    // Make sure all rows are visible in the cloned table
    const clonedHiddenRows = clonedTable.querySelectorAll('.transaction-extra-row');
    clonedHiddenRows.forEach(row => {
      row.classList.remove('hidden');
    });

    // Add table to container
    tableContainer.appendChild(clonedTable);

    // Add all elements to the expanded table
    expandedTable.appendChild(header);
    expandedTable.appendChild(tableContainer);

    // Add expanded table to body
    document.body.appendChild(expandedTable);

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
  });
});