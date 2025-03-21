// charts.js - Chart.js functionality for dashboard statistics

// Function to initialize the dashboard charts
function initDashboardCharts(employeesByContract, employeesLabels, employeesByStatus, statusLabels) {
    // Contract types distribution chart
    if (document.getElementById('contractTypeChart')) {
        const contractCtx = document.getElementById('contractTypeChart').getContext('2d');
        
        // Extract data from the data attributes
        const contractLabels = [];
        const contractData = [];
        
        for (const key in employeesByContract) {
            if (employeesByContract.hasOwnProperty(key)) {
                contractLabels.push(employeesLabels[key] || key);
                contractData.push(employeesByContract[key]);
            }
        }
        
        const contractChart = new Chart(contractCtx, {
            type: 'doughnut',
            data: {
                labels: contractLabels,
                datasets: [{
                    data: contractData,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgb(200, 200, 200)'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Distribución por Tipo de Contrato',
                        color: 'rgb(200, 200, 200)',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
    
    // Employee status distribution chart
    if (document.getElementById('statusChart')) {
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        
        // Extract data from the data attributes
        const statusChartLabels = [];
        const statusData = [];
        
        for (const key in employeesByStatus) {
            if (employeesByStatus.hasOwnProperty(key)) {
                statusChartLabels.push(statusLabels[key] || key);
                statusData.push(employeesByStatus[key]);
            }
        }
        
        const statusChart = new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: statusChartLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgb(200, 200, 200)'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Distribución por Estado',
                        color: 'rgb(200, 200, 200)',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
    
    // Add more charts as needed for the dashboard
}

// Function to initialize employee history chart
function initEmployeeHistoryChart(historyData) {
    if (!document.getElementById('employeeHistoryChart')) return;
    
    const historyCtx = document.getElementById('employeeHistoryChart').getContext('2d');
    
    // Process history data for chart
    const timestamps = [];
    const changes = [];
    
    // Get last 10 history items
    historyData.slice(0, 10).forEach(item => {
        timestamps.push(new Date(item.timestamp).toLocaleDateString());
        changes.push(1); // Just counting occurrences for a timeline
    });
    
    // Reverse arrays to get chronological order
    timestamps.reverse();
    
    const historyChart = new Chart(historyCtx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Cambios Realizados',
                data: changes,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: 'rgb(200, 200, 200)'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgb(200, 200, 200)'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Historial de Cambios',
                    color: 'rgb(200, 200, 200)',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Function to initialize company employee count chart
function initCompanyEmployeeChart(companyData) {
    if (!document.getElementById('companyEmployeeChart')) return;
    
    const companyCtx = document.getElementById('companyEmployeeChart').getContext('2d');
    
    const companyChart = new Chart(companyCtx, {
        type: 'bar',
        data: {
            labels: ['Empleados Activos', 'Empleados Inactivos'],
            datasets: [{
                label: 'Empleados',
                data: [
                    companyData.activeEmployees || 0,
                    (companyData.totalEmployees || 0) - (companyData.activeEmployees || 0)
                ],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: 'rgb(200, 200, 200)'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgb(200, 200, 200)'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Estado de Empleados',
                    color: 'rgb(200, 200, 200)',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}
