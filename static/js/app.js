document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const tweetId = e.target.dataset.tweetId;
            const response = await fetch(`/like/${tweetId}/`, { method: 'POST' });
            const data = await response.json();
            e.target.textContent = `Like (${data.likes})`;
        });
    });
});