// Dashboard task filtering & search helpers
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('tableSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const query = this.value.toLowerCase();
            const rows = document.querySelectorAll('.searchable-table tbody tr');
            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    const priorityFilter = document.getElementById('priorityFilter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', function () {
            const selected = this.value;
            const taskItems = document.querySelectorAll('.task-item');
            taskItems.forEach(function (item) {
                const itemPriority = item.getAttribute('data-priority');
                if (selected === 'all' || itemPriority === selected) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});
