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

    // 4. Live Unread Notifications Polling & Pop-Up Toasts for Student Dashboard
    const path = window.location.pathname;
    const isStudentPath = path.startsWith('/student/') || path === '/student';
    if (isStudentPath && document.getElementById('notifDropdownBtn')) {
        let seenNotifIds = new Set(JSON.parse(localStorage.getItem('seenNotifIds') || '[]'));

        function checkNotifications() {
            fetch('/student/api/notifications/unread')
                .then(response => response.json())
                .then(data => {
                    const badge = document.getElementById('notification-bell-badge');
                    const dashboardBadge = document.getElementById('notification-badge-count');
                    const bannerCard = document.getElementById('notification-banner-card');
                    const dropdownList = document.getElementById('dropdown-notif-list');
                    const dashboardList = document.getElementById('notification-list');
                    const toastEl = document.getElementById('reminderToast');

                    if (data.notifications && data.notifications.length > 0) {
                        const count = data.notifications.length;
                        
                        if (badge) {
                            badge.textContent = count;
                            badge.style.display = 'inline-block';
                        }
                        if (dashboardBadge) dashboardBadge.textContent = count;
                        if (bannerCard) bannerCard.style.display = 'block';

                        // Check for brand new notifications to trigger pop-up
                        let latestNewNotif = null;
                        data.notifications.forEach(n => {
                            if (!seenNotifIds.has(n.id)) {
                                seenNotifIds.add(n.id);
                                latestNewNotif = n;
                            }
                        });

                        // Save updated seen notification IDs
                        localStorage.setItem('seenNotifIds', JSON.stringify(Array.from(seenNotifIds)));

                        // Show pop-up toast for new notification
                        if (latestNewNotif && toastEl) {
                            const toastTitle = document.getElementById('toastHeaderTitle');
                            const toastMsg = document.getElementById('toastMessage');
                            const toastTime = document.getElementById('toastTimeAgo');

                            if (latestNewNotif.type === 'assignment' || (latestNewNotif.message && latestNewNotif.message.includes('New task assigned'))) {
                                if (toastTitle) toastTitle.textContent = '🔔 NEW TASK ASSIGNED';
                            } else {
                                if (toastTitle) toastTitle.textContent = '🔔 TASK REMINDER';
                            }

                            if (toastMsg) toastMsg.textContent = latestNewNotif.message;
                            if (toastTime) toastTime.textContent = latestNewNotif.created_at || 'Just now';

                            const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl);
                            bsToast.show();
                        }

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
        }

        checkNotifications();
        setInterval(checkNotifications, 30000); // Check every 30 seconds
    }
});


function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}
