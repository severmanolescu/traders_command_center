  // Tooltip functionality
  const infoButton = document.querySelector('.risk-analysis-info-button');
  const tooltip = document.getElementById('riskTooltip');

  infoButton.addEventListener('mouseenter', function() {
      tooltip.classList.remove('hidden');
  });

  infoButton.addEventListener('mouseleave', function() {
      tooltip.classList.add('hidden');
  });

  // For mobile: toggle on click
  infoButton.addEventListener('click', function(e) {
      e.stopPropagation();
      tooltip.classList.toggle('hidden');
  });

  // Close tooltip when clicking elsewhere
  document.addEventListener('click', function() {
      if (!tooltip.classList.contains('hidden')) {
          tooltip.classList.add('hidden');
      }
  });