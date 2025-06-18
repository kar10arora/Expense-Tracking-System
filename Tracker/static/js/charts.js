// Chart.js configuration and utilities - STATIC SIZES
class ExpenseCharts {
    constructor() {
        this.charts = {};
        this.colors = [
            '#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#ef4444',
            '#8b5cf6', '#06b6d4', '#84cc16', '#f97316', '#ec4899'
        ];
    }

    // Initialize dashboard charts
    initDashboardCharts() {
        this.initBarChart();
        this.initPieChart();
        this.loadDashboardData();
    }

    // Initialize bar chart with static size
    initBarChart() {
        const ctx = document.getElementById('barChart');
        if (!ctx) return;

        this.charts.bar = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Total Expenses (₹)',
                    data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: this.colors[0],
                    borderColor: this.colors[0],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: false, // Disable responsive behavior
                maintainAspectRatio: false, // Don't maintain aspect ratio
                plugins: { 
                    legend: { display: false } 
                },
                scales: {
                    y: { 
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                },
                animation: {
                    duration: 0 // Disable animations to prevent size changes
                },
                layout: {
                    padding: {
                        top: 20,
                        bottom: 20
                    }
                }
            }
        });
    }

    // Initialize pie chart with static size
    initPieChart() {
        const ctx = document.getElementById('pieChart');
        if (!ctx) return;

        this.charts.pie = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['No data'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#e5e7eb']
                }]
            },
            options: {
                responsive: false, // Disable responsive behavior
                maintainAspectRatio: false, // Don't maintain aspect ratio
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                animation: {
                    duration: 0 // Disable animations to prevent size changes
                },
                layout: {
                    padding: {
                        top: 20,
                        bottom: 20
                    }
                }
            }
        });
    }

    // Load dashboard data from API
    async loadDashboardData() {
        try {
            const response = await fetch('/api/chart-data/');
            const data = await response.json();
            
            this.updateBarChart(data.month_labels, data.monthly_totals);
            this.updatePieChart(data.category_labels, data.category_totals);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    // Update bar chart data without changing size
    updateBarChart(labels, data) {
        if (this.charts.bar) {
            this.charts.bar.data.labels = labels;
            this.charts.bar.data.datasets[0].data = data;
            this.charts.bar.update('none'); // Update without animation
        }
    }

    // Update pie chart data without changing size
    updatePieChart(labels, data) {
        if (this.charts.pie) {
            this.charts.pie.data.labels = labels;
            this.charts.pie.data.datasets[0].data = data;
            this.charts.pie.data.datasets[0].backgroundColor = this.getColors(labels.length);
            this.charts.pie.update('none'); // Update without animation
        }
    }

    // Get colors for pie chart
    getColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(this.colors[i % this.colors.length]);
        }
        return colors;
    }

    // Initialize reports chart with static size
    initReportsChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;

        this.charts.reports = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['No data'],
                datasets: [{
                    label: 'Total Amount (₹)',
                    data: [0],
                    backgroundColor: 'rgba(79, 70, 229, 0.6)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: false, // Disable responsive behavior
                maintainAspectRatio: false, // Don't maintain aspect ratio
                scales: {
                    y: { 
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                animation: {
                    duration: 0 // Disable animations to prevent size changes
                },
                layout: {
                    padding: {
                        top: 20,
                        bottom: 20
                    }
                }
            }
        });

        this.loadReportsData();
    }

    // Load reports data from API
    async loadReportsData(rangeType = 'daily') {
        try {
            const response = await fetch(`/api/reports-chart-data/?range=${rangeType}`);
            const data = await response.json();
            
            if (this.charts.reports) {
                this.charts.reports.data.labels = data.category_labels;
                this.charts.reports.data.datasets[0].data = data.category_totals;
                this.charts.reports.update('none'); // Update without animation
            }
        } catch (error) {
            console.error('Error loading reports data:', error);
        }
    }

    // Refresh all charts without size changes
    refreshCharts() {
        this.loadDashboardData();
        if (this.charts.reports) {
            const rangeSelect = document.getElementById('rangeSelect');
            if (rangeSelect) {
                this.loadReportsData(rangeSelect.value);
            }
        }
    }

    // Force resize charts to maintain static size
    forceStaticSize() {
        const charts = [this.charts.bar, this.charts.pie, this.charts.reports];
        charts.forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }
}

// Global chart instance
const expenseCharts = new ExpenseCharts();

// Auto-refresh functionality
function setupAutoRefresh() {
    // Refresh every 30 seconds
    setInterval(() => {
        expenseCharts.refreshCharts();
    }, 30000);

    // Refresh when page becomes visible
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            expenseCharts.refreshCharts();
        }
    });

    // Force static size on window resize
    window.addEventListener('resize', function() {
        setTimeout(() => {
            expenseCharts.forceStaticSize();
        }, 100);
    });
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard charts if on dashboard page
    if (document.getElementById('barChart') && document.getElementById('pieChart')) {
        expenseCharts.initDashboardCharts();
    }

    // Initialize reports chart if on reports page
    if (document.getElementById('categoryChart')) {
        expenseCharts.initReportsChart();
        
        // Add event listener for range changes
        const rangeSelect = document.getElementById('rangeSelect');
        if (rangeSelect) {
            rangeSelect.addEventListener('change', function() {
                expenseCharts.loadReportsData(this.value);
            });
        }
    }

    setupAutoRefresh();
    
    // Force static size after initialization
    setTimeout(() => {
        expenseCharts.forceStaticSize();
    }, 500);
}); 