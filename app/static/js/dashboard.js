(function () {
    const chartPalette = ["#C7A17A", "#7D8F69", "#6D4C41", "#A1887F", "#4E342E", "#9CAF88", "#D7B98E", "#8D6E63"];
    const chartInstances = {};

    document.addEventListener("DOMContentLoaded", () => {
        bindSidebar();
        const dashboard = document.body.dataset.dashboard;
        if (!dashboard) {
            return;
        }
        const form = document.getElementById("filtersForm");
        if (!form) {
            return;
        }
        initializeDashboard(dashboard, form);
    });

    function bindSidebar() {
        const button = document.getElementById("sidebarToggle");
        if (!button) {
            return;
        }
        button.addEventListener("click", () => {
            document.body.classList.toggle("sidebar-collapsed");
        });
    }

    async function initializeDashboard(dashboard, form) {
        showLoader(true);
        try {
            await loadFilters();
            await loadDashboard(dashboard, form);
            form.addEventListener("submit", (event) => {
                event.preventDefault();
                loadDashboard(dashboard, form);
            });
            form.querySelectorAll("select").forEach((input) => {
                input.addEventListener("change", () => loadDashboard(dashboard, form));
            });
        } catch (error) {
            showError(error);
        } finally {
            showLoader(false);
        }
    }

    async function loadFilters() {
        const response = await fetch("/dashboard/api/filtros");
        if (!response.ok) {
            throw new Error("No se pudieron cargar los filtros.");
        }
        const filters = await response.json();
        document.querySelectorAll("select[data-filter]").forEach((select) => {
            const key = select.dataset.filter;
            const values = filters[key] || [];
            select.innerHTML = '<option value="all">Todos</option>';
            values.forEach((value) => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = formatFilterLabel(key, value);
                select.appendChild(option);
            });
        });
    }

    async function loadDashboard(dashboard, form) {
        showLoader(true);
        try {
            const params = new URLSearchParams(new FormData(form));
            const response = await fetch(`/dashboard/api/${dashboard}?${params.toString()}`);
            if (!response.ok) {
                throw new Error("No se pudieron cargar los indicadores.");
            }
            const payload = await response.json();
            renderKpis(payload.kpis || []);
            renderCharts(payload.charts || []);
            window.renderDataTable("#analyticsTable", payload.table.columns || [], payload.table.rows || []);
        } catch (error) {
            showError(error);
        } finally {
            showLoader(false);
        }
    }

    function renderKpis(kpis) {
        const grid = document.getElementById("kpiGrid");
        grid.innerHTML = "";
        kpis.forEach((kpi) => {
            const card = document.createElement("article");
            card.className = `kpi-card tone-${kpi.tone || "coffee"}`;
            card.innerHTML = `
                <div class="kpi-icon"><i class="fa-solid ${kpi.icon}"></i></div>
                <div>
                    <span>${escapeHtml(kpi.title)}</span>
                    <strong>${escapeHtml(kpi.value)}</strong>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    function renderCharts(charts) {
        charts.forEach((chart, index) => {
            const canvas = document.getElementById(`chart-${index}`);
            if (!canvas) {
                return;
            }
            const title = canvas.closest(".chart-card").querySelector("h3");
            title.textContent = chart.title;
            if (chartInstances[index]) {
                chartInstances[index].destroy();
            }
            chartInstances[index] = new Chart(canvas, {
                type: chart.type,
                data: {
                    labels: chart.labels,
                    datasets: [{
                        label: "Ventas netas",
                        data: chart.data,
                        borderColor: "#6D4C41",
                        backgroundColor: chartPalette,
                        borderWidth: 2,
                        tension: 0.35,
                        fill: chart.type === "line"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    resizeDelay: 120,
                    animation: { duration: 450 },
                    layout: { padding: 4 },
                    plugins: {
                        legend: {
                            display: ["pie", "doughnut"].includes(chart.type),
                            position: "bottom"
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => ` ${formatMoney(context.parsed.y ?? context.parsed)}`
                            }
                        }
                    },
                    scales: ["pie", "doughnut"].includes(chart.type) ? {} : {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: (value) => formatShort(value) },
                            grid: { color: "rgba(78,52,46,0.08)" }
                        },
                        x: {
                            ticks: { color: "#6D4C41" },
                            grid: { display: false }
                        }
                    }
                }
            });
        });
    }

    function showLoader(show) {
        const loader = document.getElementById("loaderOverlay");
        if (loader) {
            loader.classList.toggle("visible", show);
        }
    }

    function showError(error) {
        console.error(error);
        const grid = document.getElementById("kpiGrid");
        if (grid) {
            grid.innerHTML = `<div class="alert alert-danger w-100">${escapeHtml(error.message || "Error inesperado")}</div>`;
        }
    }

    function formatMoney(value) {
        return new Intl.NumberFormat("es-BO", { style: "currency", currency: "BOB" }).format(value || 0);
    }

    function formatShort(value) {
        return new Intl.NumberFormat("es-BO", { notation: "compact" }).format(value || 0);
    }

    function formatFilterLabel(key, value) {
        if (key !== "mes") {
            return value;
        }
        const monthNames = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ];
        return monthNames[Number(value) - 1] || value;
    }

    function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, (char) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[char]));
    }
})();
