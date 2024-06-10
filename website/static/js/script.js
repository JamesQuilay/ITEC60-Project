document.querySelectorAll('.dropdown-item[data-value]').forEach(item => {
    item.addEventListener('click', function() {
        const filterValue = this.getAttribute('data-value');
        document.getElementById('filterInputHome').value = filterValue;
        document.querySelector('.dropdown-toggle').textContent = this.textContent;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Add an event listener for input changes in the search bar
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');

    searchInput.addEventListener('input', function () {
        // Enable or disable the search button based on the search input
        searchButton.disabled = !searchInput.value.trim();
    });
});

function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function deleteNoteAndRestoreConfirmation(noteId) {
    if (confirm("Your note will be deleted. Click 'OK' to confirm deletion")) {
        deleteNote(noteId);
    }
}

function togglePin(noteId) {
    console.log('Toggling pin for note ID:', noteId);
    fetch(`/toggle-pin/${noteId}`, {
        method: 'POST'
    })
    .then((response) => {
        console.log('Received response:', response);
        if (response.ok) {
            // Reload the page to reflect the updated pinned/unpinned status.
            location.reload();
        }
    });
}

$(document).ready(function () {
    setTimeout(function () {
        $(".alert:not(.no-auto-hide)").alert("close");
    }, 2000);
});

