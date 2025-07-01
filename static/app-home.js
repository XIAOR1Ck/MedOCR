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

                });
            });
        });

