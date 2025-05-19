    // Form animation setup
    const addAssetBtn = document.getElementById("addAssetBtn");
    const assetForm = document.getElementById("assetForm");
    const cancelAddAsset = document.getElementById("cancelAddAsset");

    // Initially hide the form with the same animation style from history.html
    assetForm.style.maxHeight = '0px';
    assetForm.style.overflow = 'hidden';
    assetForm.style.padding = '0';
    assetForm.style.margin = '0';
    assetForm.style.opacity = '0';
    assetForm.style.transition = 'all 0.5s ease-in-out';

    const showForm = () => {
      assetForm.style.maxHeight = '3000px'; // A large value to allow expansion
      assetForm.style.overflow = 'visible';
      assetForm.style.padding = '1.5rem';
      assetForm.style.marginBottom = '2.5rem';
      assetForm.style.opacity = '1';

      // Change button text
      addAssetBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Hide Form
      `;

      // Scroll to form
      assetForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const hideForm = () => {
      assetForm.style.maxHeight = '0px';
      assetForm.style.overflow = 'hidden';
      assetForm.style.padding = '0';
      assetForm.style.margin = '0';
      assetForm.style.opacity = '0';

      // Change button text back
      addAssetBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Add Asset
      `;
    };

    addAssetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (assetForm.style.maxHeight === '0px') {
        showForm();
      } else {
        hideForm();
      }
    });

    cancelAddAsset.addEventListener("click", () => {
      hideForm();
    });

    // Keyboard shortcut (Alt+J) for toggling form just like in history.html
    document.addEventListener('keydown', function(e) {
      if (e.altKey && e.key === 'j') {
        if (assetForm.style.maxHeight === '0px') {
          showForm();
        } else {
          hideForm();
        }
        e.preventDefault();
      }
    });

    // Portfolio Options toggle
    const portfolioOptionsBtn = document.getElementById("portfolioOptionsBtn");
    const portfolioOptions = document.getElementById("portfolioOptions");

    portfolioOptionsBtn.addEventListener("click", () => {
      portfolioOptions.classList.toggle("hidden");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (!portfolioOptionsBtn.contains(e.target) && !portfolioOptions.contains(e.target)) {
        portfolioOptions.classList.add("hidden");
      }
    });