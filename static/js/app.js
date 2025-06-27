document.addEventListener('DOMContentLoaded', () => {
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
        const tweetId = btn.dataset.tweetId;
        const heartSvg = btn.querySelector('svg');
        const countSpan = btn.querySelector('.like-count');

        // Ensure initial elements exist
        if (!heartSvg || !countSpan) {
            console.error(`Missing SVG or span for tweet ID ${tweetId}`);
            return;
        }

        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const response = await fetch(`/like/${tweetId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            if (data.likes !== undefined && data.is_liked !== undefined) {
                countSpan.textContent = data.likes;
                heartSvg.setAttribute('fill', data.is_liked ? 'currentColor' : 'none');
            } else {
                console.error('Error in response:', data.error);
            }
        });
    });

    window.updateFileName = function(input) {
        const label = input.nextElementSibling.querySelector('span');
        const fileName = input.files.length > 0 ? input.files[0].name : 'Choose a file';
        label.textContent = fileName;
    };
});