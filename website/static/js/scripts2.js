var swiper = new Swiper('.blog-slider', {
    spaceBetween: 30,
    effect: 'fade',
    loop: true,
    mousewheel: {
      invert: false,
    },
    // autoHeight: true,
    pagination: {
      el: '.blog-slider__pagination',
      clickable: true,
    }
  });
  
  document.addEventListener("DOMContentLoaded", function () {
    const filterBtns = document.querySelectorAll(".filter-btn");
    const projects = document.querySelectorAll(".project");
  
    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const filter = btn.getAttribute("data-filter");
  
        projects.forEach(function (project) {
          const projectTeam = project.getAttribute("data-team");
  
          if (filter === "all" || filter === projectTeam) {
            project.style.display = "block";
          } else {
            project.style.display = "none";
          }
        });
      });
    });
  });
  