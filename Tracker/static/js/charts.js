class ExpenseCharts {
    /* ------------------------  SETUP  ----------------------------- */
    constructor() {
        this.charts        = {};                 // bar, pie, reports
        this.colors        = [
            '#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#ef4444',
            '#8b5cf6', '#06b6d4', '#84cc16', '#f97316', '#ec4899'
        ];
        this.currentPeriod = 'daily';            // default filter
    }

    /* ---------------------  BAR + PIE (dashboard) ----------------- */
    initDashboardCharts() {
        this.initBarChart();
        this.initPieChart();
        this.loadDashboardData(this.currentPeriod);   // first load
    }

    initBarChart() {
        const ctx = document.getElementById('barChart');
        if (!ctx) return;

        this.charts.bar = new Chart(ctx, {
            type : 'bar',
            data : {
                labels  : [],
                datasets: [{
                    label          : 'Total Expenses (₹)',
                    data           : [],
                    backgroundColor: this.colors[0],
                    borderColor    : this.colors[0],
                    borderWidth    : 1
                }]
            },
            options : {
                responsive         : false,
                maintainAspectRatio: false,
                plugins : {
                    legend: { display: false },
                    title : {               // <- we fill text dynamically
                        display : true,
                        text    : '',
                        padding : { top: 0, bottom: 10 },
                        font    : { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + v.toLocaleString() }
                    }
                },
                animation: { duration: 0 },
                layout   : { padding: { top: 20, bottom: 20 } }
            }
        });
    }

    initPieChart() {
        const ctx = document.getElementById('pieChart');
        if (!ctx) return;

        this.charts.pie = new Chart(ctx, {
            type : 'pie',
            data : {
                labels  : ['No data'],
                datasets: [{
                    data           : [1],
                    backgroundColor: ['#e5e7eb']
                }]
            },
            options: {
                responsive         : false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom',
                              labels  : { padding: 20, usePointStyle: true } }
                },
                animation: { duration: 0 },
                layout   : { padding: { top: 20, bottom: 20 } }
            }
        });
    }

    /* ------------------  AJAX (dashboard) ------------------------- */
    async loadDashboardData(period = 'daily') {
        try {
            const resp = await fetch(`/api/chart-data/?period=${period}`);
            const data = await resp.json();

            const today     = new Date();
            const monthName = today.toLocaleString('default', { month: 'short' });

            const barLabels = period === 'daily'
                ? data.labels.map(d => `${monthName} ${d}`) // “Jul 14”
                : data.labels;                               // “Jan Feb …”

            this.updateBarChart(barLabels, data.totals, data.title);
            this.updatePieChart(data.category_labels, data.category_totals);
        } catch (err) {
            console.error('Dashboard data error →', err);
        }
    }

    /* ----------------  REPORTS PAGE ------------------------------- */
    initReportsChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;

        this.charts.reports = new Chart(ctx, {
            type : 'bar',
            data : {
                labels  : ['No data'],
                datasets: [{
                    label          : 'Total Amount (₹)',
                    data           : [0],
                    backgroundColor: 'rgba(79,70,229,0.6)',
                    borderColor    : 'rgba(79,70,229,1)',
                    borderWidth    : 1
                }]
            },
            options: {
                responsive         : false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title : { display:true, text:'', padding:{top:0,bottom:10},
                              font:{ size:14, weight:'bold' } }
                },
                scales: {
                    y: { beginAtZero: true,
                         ticks: { callback: v => '₹' + v.toLocaleString() } }
                },
                animation: { duration: 0 },
                layout   : { padding: { top: 20, bottom: 20 } }
            }
        });

        this.loadReportsData();  // daily default
    }

    async loadReportsData(rangeType = 'daily') {
        try {
            const resp = await fetch(`/api/reports-chart-data/?range=${rangeType}`);
            const data = await resp.json();

            if (this.charts.reports) {
                this.charts.reports.data.labels                 = data.category_labels;
                this.charts.reports.data.datasets[0].data       = data.category_totals;
                this.charts.reports.options.plugins.title.text  = data.title ?? '';
                this.charts.reports.update('none');
            }
        } catch (err) {
            console.error('Reports data error →', err);
        }
    }

    /* -----------------  REUSABLE UPDATERS ------------------------- */
    updateBarChart(labels, data, titleTxt = '') {
        if (!this.charts.bar) return;
        this.charts.bar.data.labels                = labels;
        this.charts.bar.data.datasets[0].data      = data;
        this.charts.bar.options.plugins.title.text = titleTxt;
        this.charts.bar.update('none');
    }

    updatePieChart(labels, data) {
        if (!this.charts.pie) return;

        const lbls = labels.length ? labels : ['No data'];
        const vals = data.length   ? data   : [1];

        this.charts.pie.data.labels                      = lbls;
        this.charts.pie.data.datasets[0].data            = vals;
        this.charts.pie.data.datasets[0].backgroundColor = this.getColors(lbls.length);
        this.charts.pie.update('none');
    }

    getColors(n) {       // cycle through brand palette
        return Array.from({ length: n }, (_, i) => this.colors[i % this.colors.length]);
    }

    /* -----------------  REFRESH / RESIZE -------------------------- */
    refreshCharts() {
        this.loadDashboardData(this.currentPeriod);

        if (this.charts.reports) {
            const sel = document.getElementById('rangeSelect');
            if (sel) this.loadReportsData(sel.value);
        }
    }

    forceStaticSize() {
        Object.values(this.charts).forEach(c => c && c.resize());
    }
}

/* =================  CREATE GLOBAL INSTANCE  ===================== */
const expenseCharts = new ExpenseCharts();

/* ----------------  AUTO‑REFRESH EVERY 30 s  ---------------------- */
let refreshTimer = null;
function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => expenseCharts.refreshCharts(), 30_000);
}

/* ----------------  DOM INITIALISATION --------------------------- */
document.addEventListener('DOMContentLoaded', () => {

    /* DASHBOARD PAGE (bar + pie) */
    if (document.getElementById('barChart') && document.getElementById('pieChart')) {
        expenseCharts.initDashboardCharts();

        /* daily / monthly dropdown */
        const periodSel = document.getElementById('periodSelect');
        if (periodSel) {
            periodSel.addEventListener('change', function () {
                expenseCharts.currentPeriod = this.value;        // update state
                expenseCharts.loadDashboardData(this.value);     // reload
            });
        }
    }

    /* REPORTS PAGE */
    if (document.getElementById('categoryChart')) {
        expenseCharts.initReportsChart();

        const rangeSel = document.getElementById('rangeSelect');
        if (rangeSel) {
            rangeSel.addEventListener('change', function () {
                expenseCharts.loadReportsData(this.value);
            });
        }
    }

    /* shared listeners */
    startAutoRefresh();

    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) expenseCharts.refreshCharts();
    });

    window.addEventListener('resize', () => {
        setTimeout(() => expenseCharts.forceStaticSize(), 100);
    });

    setTimeout(() => expenseCharts.forceStaticSize(), 500);  // initial sizing
});