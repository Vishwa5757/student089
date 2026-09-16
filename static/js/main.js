// Smart Student Reminder System - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto dismiss alert messages after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Mobile sidebar toggle functionality
  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // Select / Deselect All Students Helper on Create Task page
  const selectAllBtn = document.getElementById('selectAllStudents');
  const deselectAllBtn = document.getElementById('deselectAllStudents');
  const studentCheckboxes = document.querySelectorAll('.student-checkbox');

  if (selectAllBtn && studentCheckboxes.length > 0) {
    selectAllBtn.addEventListener('click', function () {
      studentCheckboxes.forEach(cb => cb.checked = true);
    });
  }

  if (deselectAllBtn && studentCheckboxes.length > 0) {
    deselectAllBtn.addEventListener('click', function () {
      studentCheckboxes.forEach(cb => cb.checked = false);
    });
  }
});
