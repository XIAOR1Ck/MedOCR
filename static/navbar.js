document.addEventListener("DOMContentLoaded", function () {
        const navItems = document.querySelectorAll(".nav-item");

        navItems.forEach((item) => {
          item.addEventListener("click", function () {
            // Remove active class from all items and sections
            navItems.forEach((nav) => nav.classList.remove("active"));
            document.querySelectorAll(".content-section").forEach((section) => {
              section.classList.remove("active");
            });

            // Add active class to clicked item
            this.classList.add("active");
            const target = this.getAttribute('data-target');
            if (target == "history-content"){
                window.location.href = "/history"
            } else if (target == "search-content"){
                window.location.href = "/search"

            } else {
                window.location.href = "/profile"
            }
          });
        });
      });

