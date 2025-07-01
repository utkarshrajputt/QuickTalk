document.addEventListener('DOMContentLoaded', () => {
    // CSRF Token helper
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

    // Like button functionality
    document.querySelectorAll('.like-btn').forEach(btn => {
        const tweetId = btn.dataset.tweetId;
        const heartSvg = btn.querySelector('svg');
        const countSpan = btn.querySelector('.like-count');

        if (!heartSvg || !countSpan) {
            console.error(`Missing SVG or span for tweet ID ${tweetId}`);
            return;
        }

        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            // Disable button during request
            btn.disabled = true;
            btn.classList.add('opacity-50');
            
            try {
                const response = await fetch(`/like/${tweetId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    },
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (data.likes !== undefined && data.is_liked !== undefined) {
                    countSpan.textContent = data.likes;
                    heartSvg.setAttribute('fill', data.is_liked ? 'currentColor' : 'none');
                    
                    // Add animation
                    btn.classList.add('transform', 'scale-110');
                    setTimeout(() => {
                        btn.classList.remove('transform', 'scale-110');
                    }, 150);
                } else {
                    throw new Error('Invalid response format');
                }
                
            } catch (error) {
                console.error('Error liking tweet:', error);
                showNotification('Error liking tweet. Please try again.', 'error');
            } finally {
                // Re-enable button
                btn.disabled = false;
                btn.classList.remove('opacity-50');
            }
        });
    });

    // Bookmark button functionality
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const tweetId = btn.dataset.tweetId;
        const bookmarkSvg = btn.querySelector('svg');
        const countSpan = btn.querySelector('.bookmark-count');

        if (!bookmarkSvg || !countSpan) {
            console.error(`Missing SVG or span for bookmark tweet ID ${tweetId}`);
            return;
        }

        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            // Disable button during request
            btn.disabled = true;
            btn.classList.add('opacity-50');
            
            try {
                const response = await fetch(`/bookmark/${tweetId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    },
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (data.is_bookmarked !== undefined && data.bookmarks_count !== undefined) {
                    countSpan.textContent = data.bookmarks_count;
                    bookmarkSvg.setAttribute('fill', data.is_bookmarked ? 'currentColor' : 'none');
                    
                    // Add animation
                    btn.classList.add('transform', 'scale-110');
                    setTimeout(() => {
                        btn.classList.remove('transform', 'scale-110');
                    }, 150);
                    
                    // Show notification
                    showNotification(
                        data.is_bookmarked ? 'Tweet bookmarked!' : 'Bookmark removed!',
                        'success'
                    );
                } else {
                    throw new Error('Invalid response format');
                }
                
            } catch (error) {
                console.error('Error bookmarking tweet:', error);
                showNotification('Error bookmarking tweet. Please try again.', 'error');
            } finally {
                // Re-enable button
                btn.disabled = false;
                btn.classList.remove('opacity-50');
            }
        });
    });

    // File input helper
    window.updateFileName = function(input) {
        const label = input.nextElementSibling?.querySelector('span') || 
                     document.getElementById('media-label');
        
        if (input.files.length > 0) {
            const file = input.files[0];
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2); // Size in MB
            
            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                showNotification('File size must be less than 5MB', 'error');
                input.value = '';
                label.textContent = 'Choose a file';
                return;
            }
            
            label.textContent = `${fileName} (${fileSize}MB)`;
        } else {
            label.textContent = 'Choose a file';
        }
    };

    // Auto-hide messages after 5 seconds
    document.querySelectorAll('[class*="bg-red-900"], [class*="bg-green-900"], [class*="bg-blue-900"], [class*="bg-yellow-900"]').forEach(msg => {
        if (msg.querySelector('button[onclick*="remove"]')) {
            setTimeout(() => {
                if (msg.parentElement) {
                    msg.style.transition = 'opacity 0.5s ease-out';
                    msg.style.opacity = '0';
                    setTimeout(() => {
                        msg.remove();
                    }, 500);
                }
            }, 5000);
        }
    });

    // Notification helper function
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        const typeClasses = {
            'error': 'bg-red-900 border-red-700 text-red-200',
            'success': 'bg-green-900 border-green-700 text-green-200',
            'info': 'bg-blue-900 border-blue-700 text-blue-200',
            'warning': 'bg-yellow-900 border-yellow-700 text-yellow-200'
        };
        
        notification.className = `fixed top-4 right-4 p-4 rounded-lg border z-50 ${typeClasses[type] || typeClasses.info}`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-white ml-4">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.transition = 'opacity 0.5s ease-out';
                notification.style.opacity = '0';
                setTimeout(() => {
                    notification.remove();
                }, 500);
            }
        }, 5000);
    };

    // Form validation helpers
    window.validateTweetForm = function(form) {
        const content = form.querySelector('[name="content"]').value.trim();
        const mediaInput = form.querySelector('[name="media"]');
        
        if (!content && (!mediaInput || !mediaInput.files.length)) {
            showNotification('Please enter some content or select a media file', 'error');
            return false;
        }
        
        if (content.length > 280) {
            showNotification('Tweet content must be 280 characters or less', 'error');
            return false;
        }
        
        return true;
    };

    // Add form validation to tweet forms
    document.querySelectorAll('form[enctype="multipart/form-data"]').forEach(form => {
        if (form.querySelector('[name="content"]')) {
            form.addEventListener('submit', function(e) {
                if (!validateTweetForm(this)) {
                    e.preventDefault();
                }
            });
        }
    });

    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states for forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('opacity-75');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Processing...';
                
                // Re-enable after 3 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-75');
                    submitBtn.textContent = originalText;
                }, 3000);
            }
        });
    });
});