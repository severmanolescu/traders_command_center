    const sidebar = document.getElementById("sidebar");
    const hideBtn = document.getElementById("hideSidebarBtn");
    const showBtn = document.getElementById("showSidebarBtn");
    const main = document.getElementById("mainContent");

    // Save sidebar state in localStorage
    const saveSidebarState = (isOpen) => {
      localStorage.setItem('sidebarOpen', isOpen ? 'true' : 'false');
    };

    // Function to close sidebar
    const closeSidebar = () => {
      sidebar.classList.add("-translate-x-full");
      main.classList.remove("ml-64");
      showBtn.classList.remove("hidden");
      saveSidebarState(false);
    };

    // Function to open sidebar
    const openSidebar = () => {
      sidebar.classList.remove("-translate-x-full");
      main.classList.add("ml-64");
      showBtn.classList.add("hidden");
      saveSidebarState(true);
    };

    // Add event listeners
    hideBtn.addEventListener("click", closeSidebar);
    showBtn.addEventListener("click", openSidebar);

    // Keyboard shortcut for toggle (Alt+S)
    document.addEventListener('keydown', function(e) {
      if (e.altKey && e.key === 's') {
        if (sidebar.classList.contains('-translate-x-full')) {
          openSidebar();
        } else {
          closeSidebar();
        }
        e.preventDefault();
      }
    });

    // Check saved state on page load
    document.addEventListener('DOMContentLoaded', () => {
      const savedState = localStorage.getItem('sidebarOpen');
      if (savedState === 'false') {
        closeSidebar();
      }
    });