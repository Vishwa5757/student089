// Main UI & Navigation JS
document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle Drawer
    const sidebar = document.getElementById('mainSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('show');
        if (overlay) overlay.classList.add('show');
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
    }

    if (toggleBtn) toggleBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 4. Live Unread Notifications Polling for Student Dashboard & Top Bell Dropdown
    const path = window.location.pathname;
    const isStudentPath = path.startsWith('/student/') || path === '/student';
    if (isStudentPath && document.getElementById('notifDropdownBtn')) {
        setInterval(function() {
            fetch('/student/api/notifications/unread')
                .then(response => response.json())
                .then(data => {
                    const badge = document.getElementById('notification-bell-badge');
                    const dashboardBadge = document.getElementById('notification-badge-count');
                    const bannerCard = document.getElementById('notification-banner-card');
                    const dropdownList = document.getElementById('dropdown-notif-list');
                    const dashboardList = document.getElementById('notification-list');

                    if (data.notifications && data.notifications.length > 0) {
                        const count = data.notifications.length;
                        
                        if (badge) {
                            badge.textContent = count;
                            badge.style.display = 'inline-block';
                        }
                        if (dashboardBadge) dashboardBadge.textContent = count;
                        if (bannerCard) bannerCard.style.display = 'block';

                        // Render in top bell dropdown
                        if (dropdownList) {
                            dropdownList.innerHTML = '';
                            data.notifications.forEach(n => {
                                const li = document.createElement('li');
                                li.className = 'notif-item';
                                li.innerHTML = `<div class="small text-white font-weight-medium">${n.message}</div>
                                                <div class="text-slate-400" style="font-size: 0.7rem;">${n.created_at}</div>`;
                                dropdownList.appendChild(li);
                            });
                        }

                        // Render in dashboard banner list if available
                        if (dashboardList) {
                            dashboardList.innerHTML = '';
                            data.notifications.forEach(n => {
                                const li = document.createElement('li');
                                li.innerHTML = `${n.message} (${n.created_at})`;
                                dashboardList.appendChild(li);
                            });
                        }
                    } else {
                        if (badge) badge.style.display = 'none';
                        if (bannerCard) bannerCard.style.display = 'none';
                        if (dropdownList) {
                            dropdownList.innerHTML = '<li class="p-3 text-center text-slate-400 small">No unread notifications</li>';
                        }
                    }
                })
                .catch(err => console.log('Notification polling error:', err));
        }, 15000); // Poll every 15 seconds
    }
});

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}
