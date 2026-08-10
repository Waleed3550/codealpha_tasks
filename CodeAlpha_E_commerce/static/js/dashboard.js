document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("[data-admin-sidebar]");
  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => sidebar?.classList.toggle("collapsed"));

  document.querySelectorAll("[data-counter]").forEach((el) => {
    const raw = Number(String(el.dataset.counter).replace(/[^0-9.]/g, "")) || 0;
    const isMoney = el.textContent.trim().startsWith("$");
    const start = performance.now();
    const duration = 900;
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const value = raw * (1 - Math.pow(1 - progress, 3));
      el.textContent = isMoney ? `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : Math.round(value).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  if (window.AOS) AOS.init({ duration: 520, once: true, offset: 60 });
  if (window.gsap) gsap.from(".page-transition", { opacity: 0, y: 16, duration: 0.45 });

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
    plugins: { legend: { display: false } },
    scales: { x: { grid: { color: gridColor } }, y: { grid: { color: gridColor }, beginAtZero: true } },
  };
  const revenueCanvas = document.getElementById("revenueChart");
  if (revenueCanvas) {
    new Chart(revenueCanvas, {
      type: "line",
      data: { labels, datasets: [{ label: "Revenue", data: revenue, borderColor: "#0f766e", backgroundColor: "rgba(15,118,110,.15)", fill: true, tension: 0.42 }] },
      options: chartBase,
    });
  }
  const ordersCanvas = document.getElementById("ordersChart");
  if (ordersCanvas) {
    new Chart(ordersCanvas, {
      type: "bar",
      data: { labels, datasets: [{ label: "Orders", data: orders, backgroundColor: "rgba(37,99,235,.75)", borderRadius: 10 }] },
      options: chartBase,
    });
  }
  const categoryCanvas = document.getElementById("categoryChart");
  if (categoryCanvas) {
    new Chart(categoryCanvas, {
      type: "doughnut",
      data: { labels: categoryLabels, datasets: [{ data: categoryCounts, backgroundColor: ["#0f766e", "#2563eb", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"] }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
    });
  }
  const countryCanvas = document.getElementById("countryChart");
  if (countryCanvas) {
    new Chart(countryCanvas, {
      type: "bar",
      data: {
        labels: countryLabels,
        datasets: [{ label: "Orders", data: countryCounts, backgroundColor: "rgba(124,58,237,.75)", borderRadius: 10 }],
      },
      options: chartBase,
    });
  }

  // Live updates via AJAX polling
  const updateStats = async () => {
    try {
      const res = await fetch("/admin-dashboard/api/stats/", {
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      });
      if (res.ok) {
        const data = await res.json();
        document.querySelectorAll(".admin-kpi").forEach(kpi => {
          const label = kpi.querySelector("span")?.textContent.trim().toLowerCase();
          const strong = kpi.querySelector("strong");
          if (!label || !strong) return;

          let newVal = null;
          if (label === "revenue") newVal = data.revenue;
          else if (label === "today") newVal = data.today_revenue;
          else if (label === "orders") newVal = data.orders_count;
          else if (label === "pending") newVal = data.pending_orders;
          else if (label === "products") newVal = data.products_count;
          else if (label === "delivered") newVal = data.delivered_orders;
          else if (label === "customers") newVal = data.users_count;
          else if (label === "low stock") newVal = data.low_stock_count;
          else if (label === "out of stock") newVal = data.out_of_stock_count;

          if (newVal !== null) {
            const isMoney = strong.textContent.trim().startsWith("$");
            if (isMoney) {
              strong.textContent = "$" + Number(newVal).toLocaleString(undefined, { maximumFractionDigits: 0 });
            } else {
              strong.textContent = Number(newVal).toLocaleString();
            }
          }
        });

        // Update charts if they exist
        if (window.Chart) {
          const revChart = Chart.getChart("revenueChart");
          if (revChart) {
            revChart.data.labels = data.monthly_labels;
            revChart.data.datasets[0].data = data.monthly_revenue;
            revChart.update();
          }

          const ordChart = Chart.getChart("ordersChart");
          if (ordChart) {
            ordChart.data.labels = data.monthly_labels;
            ordChart.data.datasets[0].data = data.monthly_orders;
            ordChart.update();
          }

          const catChart = Chart.getChart("categoryChart");
          if (catChart) {
            catChart.data.labels = data.category_labels;
            catChart.data.datasets[0].data = data.category_counts;
            catChart.update();
          }

          const countChart = Chart.getChart("countryChart");
          if (countChart) {
            countChart.data.labels = data.country_labels;
            countChart.data.datasets[0].data = data.country_counts;
            countChart.update();
          }
        }
      }
    } catch (err) {
      console.warn("Live stats update failed", err);
    }
  };

  // Poll every 10 seconds
  setInterval(updateStats, 10000);
});
