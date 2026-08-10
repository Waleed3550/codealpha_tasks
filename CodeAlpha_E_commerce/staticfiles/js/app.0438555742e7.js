document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("loaded");
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("technest-theme");
  if (savedTheme) root.dataset.theme = savedTheme;

  const header = document.getElementById("siteHeader");
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");
  const themeToggle = document.querySelector("[data-theme-toggle]");

  window.addEventListener("scroll", () => header.classList.toggle("scrolled", window.scrollY > 8), { passive: true });
  navToggle?.addEventListener("click", () => navMenu?.classList.toggle("open"));
  themeToggle?.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("technest-theme", root.dataset.theme);
  });

  if (window.AOS) AOS.init({ duration: 650, easing: "ease-out-cubic", once: true, offset: 80 });
  if (window.Swiper) {
    new Swiper(".hero-swiper", {
      loop: true,
      speed: 900,
      autoplay: { delay: 5200, disableOnInteraction: false },
      pagination: { el: ".swiper-pagination", clickable: true },
      effect: "fade",
    });
  }
  if (window.gsap) {
    gsap.from(".brand", { y: -12, opacity: 0, duration: 0.5 });
    gsap.from(".hero-content > *", { y: 28, opacity: 0, duration: 0.8, stagger: 0.12, delay: 0.2 });
  }

  document.querySelectorAll(".ripple").forEach((button) => {
    button.addEventListener("click", (event) => {
      const dot = document.createElement("span");
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      dot.className = "ripple-dot";
      dot.style.width = dot.style.height = `${size}px`;
      dot.style.left = `${event.clientX - rect.left - size / 2}px`;
      dot.style.top = `${event.clientY - rect.top - size / 2}px`;
      button.appendChild(dot);
      setTimeout(() => dot.remove(), 650);
    });
  });

  document.querySelectorAll(".thumb").forEach((thumb) => {
    thumb.addEventListener("click", () => {
      const main = document.getElementById("mainProductImage");
      if (main) main.src = thumb.dataset.image;
    });
  });

  document.querySelectorAll(".ajax-cart-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      if (!window.fetch) return;
      event.preventDefault();
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) {
        form.submit();
        return;
      }
      const data = await response.json();
      document.querySelectorAll(".cart-count").forEach((el) => (el.textContent = data.count));
      const cart = document.querySelector(".cart-pulse");
      cart?.animate([{ transform: "scale(1)" }, { transform: "scale(1.14)" }, { transform: "scale(1)" }], { duration: 360 });
    });
  });

  setTimeout(() => document.querySelectorAll(".toast").forEach((toast) => toast.remove()), 4200);
});
