document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("[data-admin-sidebar]");
  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => sidebar?.classList.toggle("collapsed"));

  const parseJson = (id) => {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : [];
  };

  if (!window.Chart) return;

  const labels = parseJson("monthly-labels");
  const revenue = parseJson("monthly-revenue");
  const orders = parseJson("monthly-orders");
  const categoryLabels = parseJson("category-labels");
  const categoryCounts = parseJson("category-counts");
  const countryLabels = parseJson("country-labels");
  const countryCounts = parseJson("country-counts");
  const gridColor = getComputedStyle(document.documentElement).getPropertyValue("--line");

  const chartBase = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 1800, easing: "easeOutQuart" },
    interaction: { mode: 'index', intersect: false },
    plugins: { 
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(8,13,23,0.95)',
        titleColor: '#fff',
        bodyColor: '#e2e8f0',
        padding: 12,
        cornerRadius: 12,
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        boxPadding: 6,
        usePointStyle: true
      }
    },
    scales: {
      x: { grid: { color: gridColor, drawBorder: false } },
      y: { grid: { color: gridColor, drawBorder: false }, beginAtZero: true },
    },
    elements: {
      line: { tension: 0.4 },
      point: { radius: 0, hitRadius: 10, hoverRadius: 6 }
    }
  };

  const revealChart = (canvasId, options) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const render = () => new Chart(canvas, options);

    if (window.gsap && window.ScrollTrigger && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      window.ScrollTrigger.create({
        trigger: canvas,
        start: "top 88%",
        once: true,
        onEnter: () => {
          window.gsap.fromTo(canvas, { y: 24, opacity: 0, scale: 0.98 }, { y: 0, opacity: 1, scale: 1, duration: 0.8, ease: "power3.out" });
          render();
        },
      });
      return;
    }

    render();
  };

  revealChart("revenueChart", {
    type: "line",
    data: {
      labels,
      datasets: [{ label: "Revenue", data: revenue, borderColor: "#0f766e", backgroundColor: "rgba(15,118,110,.15)", fill: true, tension: 0.42 }],
    },
    options: chartBase,
  });

  revealChart("ordersChart", {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Orders", data: orders, backgroundColor: "rgba(37,99,235,.75)", borderRadius: 10 }],
    },
    options: chartBase,
  });

  revealChart("categoryChart", {
    type: "doughnut",
    data: {
      labels: categoryLabels,
      datasets: [{ data: categoryCounts, backgroundColor: ["#0f766e", "#2563eb", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"] }],
    },
    options: { responsive: true, maintainAspectRatio: false, animation: { duration: 1000 }, plugins: { legend: { position: "bottom" } } },
  });

  revealChart("countryChart", {
    type: "bar",
    data: {
      labels: countryLabels,
      datasets: [{ label: "Orders", data: countryCounts, backgroundColor: "rgba(124,58,237,.75)", borderRadius: 10 }],
    },
    options: chartBase,
  });
});


  const timeEl = document.getElementById('adminCurrentTime');
  if(timeEl) {
    setInterval(() => {
      const now = new Date();
      timeEl.textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }, 1000);
    timeEl.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  }

  // GSAP Premium Animations & Animated Counters
  if (window.gsap) {
    gsap.from(".admin-kpi-grid .admin-card", {
      y: 30,
      opacity: 0,
      duration: 0.6,
      stagger: 0.05,
      ease: "back.out(1.2)",
      delay: 0.1
    });
    
    gsap.from(".admin-kpi", {
      y: 40,
      scale: 0.95,
      opacity: 0,
      duration: 0.7,
      stagger: 0.08,
      ease: "power3.out",
      delay: 0.2
    });
    
    document.querySelectorAll("[data-counter]").forEach(el => {
      const targetText = el.textContent.trim();
      const isCurrency = targetText.startsWith("$");
      const targetValue = parseFloat(targetText.replace(/[^0-9.]/g, "")) || 0;
      
      gsap.fromTo(el, 
        { innerHTML: 0 }, 
        {
          innerHTML: targetValue,
          duration: 1.5,
          ease: "power2.out",
          delay: 0.4,
          snap: { innerHTML: 1 },
          onUpdate: function() {
            let val = Math.floor(this.targets()[0].innerHTML).toLocaleString();
            el.textContent = isCurrency ? "$" + val : val;
          }
        }
      );
    });

    // Animate tables and reports
    gsap.from(".admin-grid.three .admin-card", {
      y: 40,
      opacity: 0,
      duration: 0.8,
      stagger: 0.1,
      ease: "power3.out",
      scrollTrigger: {
        trigger: ".admin-grid.three",
        start: "top 85%"
      }
    });

    // Animate Sidebar on load
    gsap.from(".admin-sidebar", {
      x: -30,
      opacity: 0,
      duration: 0.7,
      ease: "power3.out"
    });
    gsap.from(".admin-menu a", {
      x: -15,
      opacity: 0,
      duration: 0.5,
      stagger: 0.03,
      ease: "power2.out",
      delay: 0.1
    });

    // Notifications slide in
    gsap.from(".toast-stack .toast", {
      x: 100,
      opacity: 0,
      duration: 0.6,
      stagger: 0.1,
      ease: "back.out(1.2)"
    });
  }
