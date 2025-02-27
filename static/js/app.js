document.addEventListener('DOMContentLoaded', () => {
    // Function to get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent any default behavior
            const tweetId = btn.dataset.tweetId;
            const response = await fetch(`/like/${tweetId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            if (data.likes !== undefined) {
                const countSpan = btn.querySelector('.like-count');
                countSpan.textContent = data.likes;
            } else {
                console.error('Error:', data.error);
            }
        });
    });

    window.updateFileName = function(input) {
        const label = input.nextElementSibling.querySelector('span');
        const fileName = input.files.length > 0 ? input.files[0].name : 'Choose a file';
        label.textContent = fileName;
    };
});