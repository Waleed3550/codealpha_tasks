(() => {
  const ready = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  };

  const escapeHtml = (value) =>
    String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

  ready(() => {
    const root = document.documentElement;
    const body = document.body;
    const header = document.getElementById("siteHeader");
    const navToggle = document.querySelector("[data-nav-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");
    const themeToggle = document.querySelector("[data-theme-toggle]");
    const hero = document.querySelector(".hero");
    const loadingScreen = document.querySelector(".loading-screen");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const hasGsap = Boolean(window.gsap);
    const hasScrollTrigger = Boolean(window.ScrollTrigger);
    const hasLenis = Boolean(window.Lenis);

    let lenis = null;

    body.classList.add("js-ready");

    const savedTheme = localStorage.getItem("technest-theme");
    if (savedTheme) {
      root.dataset.theme = savedTheme;
    }

    const syncHeaderState = () => {
      const scrolled = (window.scrollY || 0) > 8;
      header?.classList.toggle("scrolled", scrolled);
      header?.classList.toggle("is-compact", scrolled);
    };

    const setTheme = (nextTheme) => {
      root.dataset.theme = nextTheme;
      localStorage.setItem("technest-theme", nextTheme);
    };

    const initLenis = () => {
      if (!hasLenis || prefersReducedMotion || !hasGsap || !hasScrollTrigger) {
        return;
      }

      lenis = new window.Lenis({
        duration: 1.08,
        smoothWheel: true,
        smoothTouch: false,
        easing: (t) => 1 - Math.pow(1 - t, 3),
      });

      lenis.on("scroll", window.ScrollTrigger.update);
      window.gsap.ticker.add((time) => {
        lenis?.raf(time * 1000);
      });
      window.gsap.ticker.lagSmoothing(0);
      document.documentElement.classList.add("lenis-supported");
    };

    const splitWords = (selector) => {
      document.querySelectorAll(selector).forEach((el) => {
        if (el.dataset.splitWords === "true") return;
        const raw = (el.textContent || "").trim();
        if (!raw) return;
        const words = raw.split(/\s+/).map((word) => `<span class="split-word"><span class="split-word__inner">${escapeHtml(word)}</span></span>`);
        el.dataset.splitWords = "true";
        el.setAttribute("aria-label", raw);
        el.innerHTML = words.join(" ");
      });
    };

    const animateWordGroups = (selector, triggerOffset = "top 82%") => {
      if (!hasGsap || !hasScrollTrigger || prefersReducedMotion) return;
      document.querySelectorAll(selector).forEach((el) => {
        const words = el.querySelectorAll(".split-word__inner");
        if (!words.length || el.dataset.wordAnimated === "true") return;
        el.dataset.wordAnimated = "true";
        window.gsap.set(words, { yPercent: 120, opacity: 0, rotateX: -65, transformOrigin: "50% 100%" });
        window.ScrollTrigger.create({
          trigger: el,
          start: triggerOffset,
          once: true,
          onEnter: () => {
            window.gsap.to(words, {
              yPercent: 0,
              opacity: 1,
              rotateX: 0,
              duration: 0.85,
              stagger: 0.03,
              ease: "power3.out",
              clearProps: "transform",
            });
          },
        });
      });
    };

    const initTypographyMotion = () => {
      splitWords(
        [
          ".hero h1",
          ".section-head h1",
          ".section-head h2",
          ".page-hero h1",
          ".compact-hero h1",
          ".admin-page-head h1",
          ".card-head h2",
          ".footer h3",
          ".auth-panel h1",
          ".auth-panel h2",
          ".detail-info h1",
          ".success-card h1",
          ".ai-assistant__brand strong",
        ].join(",")
      );

      animateWordGroups(
        [
          ".hero h1",
          ".section-head h1",
          ".section-head h2",
          ".page-hero h1",
          ".compact-hero h1",
          ".admin-page-head h1",
          ".card-head h2",
          ".footer h3",
          ".auth-panel h1",
          ".auth-panel h2",
          ".detail-info h1",
          ".success-card h1",
        ].join(",")
      );

      if (hasGsap && hasScrollTrigger && !prefersReducedMotion && document.querySelector(".hero")) {
        window.ScrollTrigger.create({
          trigger: ".hero",
          start: "top top",
          end: "bottom top",
          scrub: 0.6,
          onUpdate: (self) => {
            const activeContent = document.querySelector(".swiper-slide-active .hero-content");
            if (activeContent) {
              window.gsap.to(activeContent, {
                x: self.progress * 10,
                y: self.progress * 8,
                duration: 0.18,
                ease: "none",
                overwrite: "auto",
              });
            }
          },
        });
      }
    };

    const animateCounter = (el) => {
      if (!hasGsap || !hasScrollTrigger || el.dataset.counterAnimated === "true") return;
      const rawValue = String(el.dataset.counter || "0");
      const numericValue = Number(rawValue.replace(/[^0-9.\-]/g, "")) || 0;
      const prefix = (el.textContent || "").trim().match(/^[^\d-]+/)?.[0] || "";
      const isDecimal = rawValue.includes(".");
      el.dataset.counterAnimated = "true";

      const state = { value: 0 };
      window.ScrollTrigger.create({
        trigger: el,
        start: "top 88%",
        once: true,
        onEnter: () => {
          window.gsap.to(state, {
            value: numericValue,
            duration: 1.2,
            ease: "power3.out",
            onUpdate: () => {
              const value = state.value;
              const formatted = new Intl.NumberFormat(undefined, {
                minimumFractionDigits: isDecimal ? 0 : 0,
                maximumFractionDigits: isDecimal ? 2 : 0,
              }).format(value);
              el.textContent = `${prefix}${formatted}`;
            },
          });
        },
      });
    };

    const initCounters = () => {
      document.querySelectorAll("[data-counter]").forEach(animateCounter);
    };

    const initLoadIntro = () => {
      if (!hasGsap || prefersReducedMotion) {
        loadingScreen?.remove();
        body.classList.add("loaded");
        return;
      }

      const intro = window.gsap.timeline({
        defaults: { ease: "power3.out" },
        onComplete: () => {
          loadingScreen?.remove();
          body.classList.add("loaded");
        },
      });

      intro
        .fromTo(
          ".loading-screen span",
          { scale: 0.6, opacity: 0, rotate: -90 },
          { scale: 1, opacity: 1, rotate: 0, duration: 0.35 },
          0
        )
        .to(".loading-screen", { opacity: 0, duration: 0.45 }, 0.2)
        .from(
          "#siteHeader .brand, .admin-topbar .brand",
          { y: -18, opacity: 0, duration: 0.75, clearProps: "transform,opacity" },
          0.22
        )
        .from(
          ".nav-links > *, .nav-actions > *, .admin-top-actions > *",
          { y: -16, opacity: 0, stagger: 0.05, duration: 0.42, clearProps: "transform,opacity" },
          0.28
        );

      if (document.querySelector(".hero-content")) {
        intro.from(
          ".hero-content > *",
          { y: 30, opacity: 0, stagger: 0.12, duration: 0.75, clearProps: "transform,opacity" },
          0.45
        );
      }

      if (document.querySelector(".page-hero")) {
        intro.from(
          ".page-hero .container > *",
          { y: 24, opacity: 0, stagger: 0.08, duration: 0.6, clearProps: "transform,opacity" },
          0.35
        );
      }

      if (document.querySelector(".admin-page-head")) {
        intro.from(
          ".admin-page-head > *",
          { y: 24, opacity: 0, stagger: 0.08, duration: 0.6, clearProps: "transform,opacity" },
          0.35
        );
      }
    };

    const initSectionReveals = () => {
      if (!hasGsap || !hasScrollTrigger || prefersReducedMotion) return;

      const revealConfigs = [
        { selector: ".section", y: 34, stagger: 0.12 },
        { selector: ".page-hero", y: 26 },
        { selector: ".compact-hero", y: 24 },
        { selector: ".auth-shell", y: 24 },
        { selector: ".success-page", y: 24 },
        { selector: ".admin-page-head", y: 22 },
        { selector: ".filters", x: -26 },
        { selector: ".gallery", x: -24 },
        { selector: ".detail-info", x: 24 },
        { selector: ".summary-card", x: 20 },
        { selector: ".cart-table", y: 24 },
        { selector: ".checkout-form", y: 24 },
        { selector: ".auth-panel", scale: 0.98 },
        { selector: ".success-card", scale: 0.98 },
        { selector: ".premium-category-card", y: 34, stagger: 0.14 },
        { selector: ".product-card", y: 34, stagger: 0.12 },
        { selector: ".admin-kpi", y: 28, stagger: 0.08, scale: 0.98 },
        { selector: ".admin-card", y: 26, stagger: 0.1 },
        { selector: ".cart-row", y: 18, stagger: 0.08 },
        { selector: ".customer-card", y: 18, stagger: 0.08 },
        { selector: ".timeline-step", y: 18, stagger: 0.08 },
        { selector: ".toast", y: 12, stagger: 0.06 },
        { selector: ".footer", y: 22 },
      ];

      revealConfigs.forEach((config) => {
        window.gsap.utils.toArray(config.selector).forEach((el) => {
          if (el.dataset.revealed === "true") return;
          if (el.closest(".swiper-slide-duplicate")) return;
          el.dataset.revealed = "true";
          window.gsap.fromTo(
            el,
            {
              opacity: 0,
              y: config.y ?? 0,
              x: config.x ?? 0,
              scale: config.scale ?? 1,
            },
            {
              opacity: 1,
              y: 0,
              x: 0,
              scale: 1,
              duration: 0.85,
              ease: "power3.out",
              scrollTrigger: {
                trigger: el,
                start: "top 86%",
                once: true,
              },
            }
          );
        });
      });

      const heroCards = document.querySelectorAll(".hero-slide .primary-btn, .hero-slide .hero-content span, .hero-slide .hero-content p");
      if (heroCards.length) {
        window.ScrollTrigger.create({
          trigger: ".hero",
          start: "top top",
          once: true,
          onEnter: () => {
            window.gsap.fromTo(
              heroCards,
              { y: 18, opacity: 0 },
              { y: 0, opacity: 1, stagger: 0.08, duration: 0.7, ease: "power3.out" }
            );
          },
        });
      }

      const footerChildren = document.querySelectorAll(".footer-grid > *");
      if (footerChildren.length) {
        window.ScrollTrigger.create({
          trigger: ".footer",
          start: "top 88%",
          once: true,
          onEnter: () => {
            window.gsap.fromTo(
              footerChildren,
              { y: 18, opacity: 0 },
              { y: 0, opacity: 1, stagger: 0.11, duration: 0.65, ease: "power3.out" }
            );
            window.gsap.fromTo(
              ".footer-bottom > *",
              { y: 10, opacity: 0 },
              { y: 0, opacity: 1, stagger: 0.08, duration: 0.55, ease: "power2.out" }
            );
          },
        });
      }
    };

    const initProductMicroMotion = () => {
      if (!hasGsap || prefersReducedMotion) return;

      document.querySelectorAll(".product-card").forEach((card) => {
        const media = card.querySelector(".product-media img");
        const overlayButton = card.querySelector(".add-to-cart-overlay .primary-btn");
        const actionIcons = card.querySelectorAll(".action-icon");

        card.addEventListener("mouseenter", () => {
          window.gsap.to(card, {
            y: -10,
            rotateX: 0.4,
            rotateY: 0.6,
            scale: 1.01,
            duration: 0.35,
            ease: "power2.out",
            overwrite: true,
          });
          if (media) {
            window.gsap.to(media, { scale: 1.08, duration: 0.6, ease: "power2.out", overwrite: true });
          }
          if (overlayButton) {
            window.gsap.to(overlayButton, { y: 0, opacity: 1, duration: 0.35, ease: "power2.out", overwrite: true });
          }
          if (actionIcons.length) {
            window.gsap.fromTo(
              actionIcons,
              { y: -6, opacity: 0 },
              { y: 0, opacity: 1, stagger: 0.05, duration: 0.28, ease: "power2.out", overwrite: true }
            );
          }
        });

        card.addEventListener("mouseleave", () => {
          window.gsap.to(card, {
            y: 0,
            rotateX: 0,
            rotateY: 0,
            scale: 1,
            duration: 0.45,
            ease: "power3.out",
            overwrite: true,
          });
          if (media) {
            window.gsap.to(media, { scale: 1, duration: 0.45, ease: "power2.out", overwrite: true });
          }
        });
      });
    };

    const initMagneticButtons = () => {
      if (!hasGsap || prefersReducedMotion) return;
      const selectors = [
        "a",
        "button",
        ".nav-pill",
        ".icon-btn",
        ".pill-btn",
        ".primary-btn",
        ".ghost-btn",
        ".action-icon",
        ".thumb",
        ".ai-assistant__toggle",
        ".ai-send-btn",
        ".ai-voice-btn",
        ".whatsapp-fab__button",
        ".dropdown-menu a",
        ".admin-menu a",
        ".admin-list-row",
        ".profile-menu summary",
        ".pagination a",
      ].join(",");

      document.querySelectorAll(selectors).forEach((el) => {
        if (el.dataset.magnetized === "true") return;
        el.dataset.magnetized = "true";

        el.addEventListener("pointerenter", () => {
          window.gsap.to(el, {
            scale: 1.02,
            duration: 0.24,
            ease: "power2.out",
            overwrite: true,
          });
        });

        el.addEventListener("pointermove", (event) => {
          const rect = el.getBoundingClientRect();
          const dx = (event.clientX - rect.left - rect.width / 2) * 0.12;
          const dy = (event.clientY - rect.top - rect.height / 2) * 0.12;
          window.gsap.to(el, {
            x: dx,
            y: dy,
            duration: 0.25,
            ease: "power2.out",
            overwrite: true,
          });
        });

        el.addEventListener("pointerleave", () => {
          window.gsap.to(el, {
            x: 0,
            y: 0,
            scale: 1,
            duration: 0.55,
            ease: "elastic.out(1, 0.35)",
            overwrite: true,
          });
        });
      });
    };

    const initParallax = () => {
      if (!hasGsap || !hasScrollTrigger || prefersReducedMotion) return;

      window.gsap.utils.toArray(".zoom-wrap img, .category-card img, .product-media img, .card-bg").forEach((el) => {
        const trigger = el.closest(".product-card, .premium-category-card, .gallery, .hero-slide, .category-card, .section") || el;
        window.gsap.to(el, {
          yPercent: -6,
          scale: 1.04,
          ease: "none",
          scrollTrigger: {
            trigger,
            start: "top bottom",
            end: "bottom top",
            scrub: 0.6,
          },
        });
      });

      if (!hero) return;
      const heroContent = hero.querySelector(".swiper-slide-active .hero-content");
      const heroSlide = hero.querySelector(".swiper-slide-active");

      const resetHero = () => {
        if (heroContent) {
          window.gsap.to(heroContent, { x: 0, y: 0, duration: 0.6, ease: "power3.out", overwrite: true });
        }
        if (heroSlide) {
          window.gsap.to(heroSlide, { backgroundPosition: "50% 50%", duration: 0.6, ease: "power3.out", overwrite: true });
        }
      };

      hero.addEventListener("pointermove", (event) => {
        const rect = hero.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        const active = hero.querySelector(".swiper-slide-active .hero-content");
        const activeSlide = hero.querySelector(".swiper-slide-active");
        if (active) {
          window.gsap.to(active, { x: x * 20, y: y * 12, duration: 0.45, ease: "power2.out", overwrite: true });
        }
        if (activeSlide) {
          window.gsap.to(activeSlide, {
            backgroundPosition: `${50 + x * 5}% ${50 + y * 5}%`,
            duration: 0.45,
            ease: "power2.out",
            overwrite: true,
          });
        }
      });

      hero.addEventListener("pointerleave", resetHero);
    };

    const initHeroSwiperMotion = () => {
      if (!window.Swiper) return;

      const animateSlide = (swiper) => {
        if (!swiper) return;
        const slide = swiper.slides?.[swiper.activeIndex] || swiper.el?.querySelector(".swiper-slide-active");
        if (!slide || prefersReducedMotion || !hasGsap) return;
        const content = slide.querySelector(".hero-content");
        if (!content) return;
        const parts = content.querySelectorAll("span, h1, p, a");
        window.gsap.fromTo(
          parts,
          { y: 28, opacity: 0, filter: "blur(4px)" },
          { y: 0, opacity: 1, filter: "blur(0px)", stagger: 0.08, duration: 0.7, ease: "power3.out" }
        );
      };

      const heroEl = document.querySelector(".hero-swiper");
      const featuredEl = document.querySelector(".featured-swiper");

      if (!heroEl && !featuredEl) return;

      const heroSwiper = heroEl
        ? new Swiper(heroEl, {
            loop: true,
            speed: 1000,
            autoplay: { delay: 5200, disableOnInteraction: false },
            pagination: { el: ".hero .swiper-pagination", clickable: true },
            effect: "fade",
            fadeEffect: { crossFade: true },
            on: {
              init(swiper) {
                animateSlide(swiper);
              },
              slideChangeTransitionStart(swiper) {
                animateSlide(swiper);
              },
            },
          })
        : null;

      const featuredSwiper = featuredEl
        ? new Swiper(featuredEl, {
            loop: true,
            speed: 900,
            slidesPerView: 1,
            spaceBetween: 20,
            grabCursor: true,
            autoplay: { delay: 4200, disableOnInteraction: false, pauseOnMouseEnter: true },
            pagination: { el: ".featured-swiper .swiper-pagination", clickable: true, dynamicBullets: true },
            navigation: { nextEl: ".swiper-next", prevEl: ".swiper-prev" },
            breakpoints: {
              640: { slidesPerView: 2 },
              980: { slidesPerView: 3 },
              1200: { slidesPerView: 4 },
            },
          })
        : null;

      [heroSwiper, featuredSwiper].forEach((swiper) => {
        if (!swiper || !hasGsap || prefersReducedMotion) return;
        swiper.on("transitionEnd", () => {
          const activeCards = swiper.el.querySelectorAll(".swiper-slide-active .product-card, .swiper-slide-active .hero-slide");
          if (activeCards.length) {
            window.gsap.fromTo(
              activeCards,
              { y: 20, opacity: 0.65 },
              { y: 0, opacity: 1, stagger: 0.08, duration: 0.45, ease: "power2.out" }
            );
          }
        });
      });
    };

    const initInputFocusMotion = () => {
      document.querySelectorAll("input, select, textarea").forEach((field) => {
        field.addEventListener("focus", () => field.closest("label, .form-field, .admin-search, .search-bar, .ai-assistant__field")?.classList.add("is-focused"));
        field.addEventListener("blur", () => field.closest("label, .form-field, .admin-search, .search-bar, .ai-assistant__field")?.classList.remove("is-focused"));
      });
    };

    const initAjaxCart = () => {
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
          document.querySelectorAll(".cart-count").forEach((el) => {
            el.textContent = data.count;
          });

          const cart = document.querySelector(".cart-pulse");
          cart?.animate([{ transform: "scale(1)" }, { transform: "scale(1.14)" }, { transform: "scale(1)" }], { duration: 360, easing: "ease-out" });
        });
      });
    };

    const initThumbs = () => {
      document.querySelectorAll(".thumb").forEach((thumb) => {
        thumb.addEventListener("click", () => {
          const main = document.getElementById("mainProductImage");
          if (main) main.src = thumb.dataset.image || main.src;
        });
      });
    };

    const initRipple = () => {
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
    };

    const initToasts = () => {
      const toasts = document.querySelectorAll(".toast");
      if (!toasts.length) return;
      if (hasGsap && !prefersReducedMotion) {
        window.gsap.fromTo(
          toasts,
          { x: 32, opacity: 0, y: 12 },
          { x: 0, opacity: 1, y: 0, stagger: 0.08, duration: 0.5, ease: "power3.out" }
        );
      }
      setTimeout(() => {
        toasts.forEach((toast) => toast.remove());
      }, 4200);
    };

    const initHeaderScroll = () => {
      syncHeaderState();
      window.addEventListener("scroll", syncHeaderState, { passive: true });
    };

    const initNavigation = () => {
      navToggle?.addEventListener("click", () => {
        navMenu?.classList.toggle("open");
        if (hasGsap && !prefersReducedMotion && navMenu) {
          window.gsap.fromTo(
            navMenu,
            { y: -10, opacity: 0 },
            { y: 0, opacity: 1, duration: 0.28, ease: "power2.out" }
          );
        }
      });

      themeToggle?.addEventListener("click", () => {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        setTheme(nextTheme);
      });
    };

    const initReducedMotionFallbacks = () => {
      if (!prefersReducedMotion) return;
      body.classList.add("reduced-motion");
      loadingScreen?.remove();
      body.classList.add("loaded");
    };

    initReducedMotionFallbacks();
    initNavigation();
    initHeaderScroll();
    initLenis();
    initTypographyMotion();
    initSectionReveals();
    initProductMicroMotion();
    initMagneticButtons();
    initParallax();
    initHeroSwiperMotion();
    initInputFocusMotion();
    initAjaxCart();
    initThumbs();
    initRipple();
    initCounters();
    initToasts();

    if (window.gsap && hasScrollTrigger && !prefersReducedMotion) {
      window.ScrollTrigger.refresh();
    }

    window.addEventListener(
      "load",
      () => {
        initLoadIntro();
        if (window.gsap && hasScrollTrigger && !prefersReducedMotion) {
          window.ScrollTrigger.refresh(true);
        }
      },
      { once: true }
    );
  });
})();
