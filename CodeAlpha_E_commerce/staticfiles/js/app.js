document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("loaded");
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("technest-theme");
  if (savedTheme) root.dataset.theme = savedTheme;

  const header = document.getElementById("siteHeader");
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");
  const themeToggle = document.querySelector("[data-theme-toggle]");
  const authModal = document.querySelector("[data-auth-modal]");
  const authModalOpeners = document.querySelectorAll("[data-auth-modal-open]");
  const googleClientId = document.body.dataset.googleClientId || "";
  const googleLoginUrl = document.body.dataset.googleLoginUrl || "";
  const googleRegisterUrl = document.body.dataset.googleRegisterUrl || "";
  const authNextUrl = document.body.dataset.authNextUrl || window.location.pathname + window.location.search;
  let googleInitialized = false;

  window.addEventListener("scroll", () => header.classList.toggle("scrolled", window.scrollY > 8), { passive: true });
  navToggle?.addEventListener("click", () => navMenu?.classList.toggle("open"));
  function updateThemeIcon() {
    const icon = themeToggle?.querySelector("i");
    if (icon) {
      if (root.dataset.theme === "dark") {
        icon.className = "fa-solid fa-sun";
      } else {
        icon.className = "fa-solid fa-moon";
      }
    }
  }

  themeToggle?.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("technest-theme", root.dataset.theme);
    updateThemeIcon();
  });
  
  if (themeToggle) {
    updateThemeIcon();
  }

  function setGoogleStatus(message) {
    document.querySelectorAll("[data-google-auth-status]").forEach((statusEl) => {
      if (!statusEl) return;
      if (message) {
        statusEl.hidden = false;
        statusEl.textContent = message;
      } else {
        statusEl.hidden = true;
        statusEl.textContent = "";
      }
    });
  }

  function openAuthModal() {
    if (!authModal) return;
    authModal.hidden = false;
    authModal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
    renderGoogleButtons(true);
  }

  function closeAuthModal() {
    if (!authModal) return;
    authModal.hidden = true;
    authModal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    setGoogleStatus("");
  }

  authModalOpeners.forEach((button) => button.addEventListener("click", openAuthModal));
  authModal?.querySelectorAll("[data-auth-modal-close]").forEach((button) => button.addEventListener("click", closeAuthModal));
  authModal?.addEventListener("click", (event) => {
    if (event.target === authModal || event.target.matches?.("[data-auth-modal-close]")) {
      closeAuthModal();
    }
  });

  async function submitGoogleCredential(credential) {
    const endpoint = googleLoginUrl || authModal?.dataset.googleLoginUrl || "";
    if (!endpoint) {
      setGoogleStatus("Google sign-in is not available right now.");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("credential", credential);
      formData.append("next", authNextUrl);
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        setGoogleStatus(payload.error || "Google sign-in failed.");
        return;
      }
      setGoogleStatus("");
      window.location.href = payload.redirect_url || authNextUrl;
    } catch (error) {
      setGoogleStatus("Google sign-in failed.");
    }
  }

  function buttonOptions(slot) {
    const width = Math.max(280, slot?.clientWidth || 0);
    return {
      theme: "outline",
      size: "large",
      text: "continue_with",
      shape: "pill",
      logo_alignment: "left",
      width,
    };
  }

  function renderGoogleButtons(force = false) {
    if (!googleClientId || !window.google?.accounts?.id) return;
    if (!googleInitialized) {
      google.accounts.id.initialize({
        client_id: googleClientId,
        callback: (response) => {
          if (response?.credential) {
            submitGoogleCredential(response.credential);
          }
        },
      });
      googleInitialized = true;
    }
    document.querySelectorAll("[data-google-signin-button]").forEach((slot) => {
      if (!force && slot.dataset.renderedGoogleButton === "true") return;
      if (!force) {
        const modal = slot.closest("[data-auth-modal]");
        if (modal && modal.hidden) return;
      }
      slot.innerHTML = "";
      google.accounts.id.renderButton(slot, buttonOptions(slot));
      slot.dataset.renderedGoogleButton = "true";
    });
  }

  let googleRenderAttempts = 0;
  function scheduleGoogleButtons(force = false) {
    if (!googleClientId || window.google?.accounts?.id) {
      renderGoogleButtons(force);
      return;
    }
    if (googleRenderAttempts < 20) {
      googleRenderAttempts += 1;
      window.setTimeout(() => scheduleGoogleButtons(force), 150);
    }
  }

  scheduleGoogleButtons(false);
  window.addEventListener("resize", () => renderGoogleButtons(false), { passive: true });

  if (window.AOS) AOS.init({ duration: 650, easing: "ease-out-cubic", once: true, offset: 80 });
  if (window.Swiper) {
    new Swiper(".hero-swiper", {
      loop: true,
      speed: 900,
      autoplay: { delay: 5200, disableOnInteraction: false },
      pagination: { el: ".swiper-pagination", clickable: true },
      effect: "fade",
    });

    new Swiper(".featured-swiper", {
      loop: true,
      speed: 800,
      slidesPerView: 1,
      spaceBetween: 20,
      grabCursor: true,
      autoplay: { delay: 4000, disableOnInteraction: false, pauseOnMouseEnter: true },
      pagination: { el: ".swiper-pagination", clickable: true, dynamicBullets: true },
      navigation: { nextEl: ".swiper-next", prevEl: ".swiper-prev" },
      breakpoints: {
        640: { slidesPerView: 2 },
        980: { slidesPerView: 3 },
        1200: { slidesPerView: 4 }
      }
    });
  }
  if (window.gsap) {
    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

    // Elegant page load sequence
    const tl = gsap.timeline();
    tl.from("#siteHeader", { y: -100, opacity: 0, duration: 0.8, ease: "power3.out", clearProps: "all" })
      .from(".brand", { scale: 0.9, opacity: 0, duration: 0.5, ease: "back.out(1.5)", clearProps: "all" }, "-=0.4")
      .from(".nav-actions > *", { scale: 0.8, opacity: 0, duration: 0.4, stagger: 0.1, ease: "back.out(1.2)", clearProps: "all" }, "-=0.3");
    
    if (document.querySelector(".hero-content")) {
      tl.from(".hero-content > *", { y: 40, opacity: 0, duration: 0.8, stagger: 0.15, ease: "power3.out" }, "-=0.5");
    }

    // Magnetic Button Effect
    const magnets = document.querySelectorAll(".primary-btn, .pill-btn, .nav-pill, .icon-btn");
    magnets.forEach((btn) => {
      btn.addEventListener("mousemove", (e) => {
        const rect = btn.getBoundingClientRect();
        const h = rect.width / 2;
        const x = e.clientX - rect.left - h;
        const y = e.clientY - rect.top - rect.height / 2;
        gsap.to(btn, { x: x * 0.35, y: y * 0.35, duration: 0.4, ease: "power2.out" });
      });
      btn.addEventListener("mouseleave", () => {
        gsap.to(btn, { x: 0, y: 0, duration: 0.7, ease: "elastic.out(1, 0.3)" });
      });
    });

    // Custom Cursor tracking
    const cursor = document.getElementById("customCursor");
    if (cursor) {
      window.addEventListener("mousemove", (e) => {
        gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0.15, ease: "power2.out" });
      });
      document.querySelectorAll("a, button, input, select").forEach((el) => {
        el.addEventListener("mouseenter", () => gsap.to(cursor, { scale: 1.8, opacity: 0.5, duration: 0.2 }));
        el.addEventListener("mouseleave", () => gsap.to(cursor, { scale: 1, opacity: 1, duration: 0.2 }));
      });
    }

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
      const formData = new FormData(form);
      if (event.submitter?.name) {
        formData.set(event.submitter.name, event.submitter.value);
      }
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) {
        form.submit();
        return;
      }
      const data = await response.json();
      if (data.login_required && data.login_url) {
        window.location.href = data.login_url;
        return;
      }
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
        return;
      }
      document.querySelectorAll(".cart-count").forEach((el) => (el.textContent = data.count));
      const cart = document.querySelector(".cart-pulse");
      cart?.animate([{ transform: "scale(1)" }, { transform: "scale(1.14)" }, { transform: "scale(1)" }], { duration: 360 });
    });
  });

  setTimeout(() => document.querySelectorAll(".toast").forEach((toast) => toast.remove()), 4200);
});
