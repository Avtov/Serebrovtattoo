document.addEventListener('DOMContentLoaded', () => {
    const reviewForm = document.getElementById('review-form');
    const reviewList = document.getElementById('review-list');

    reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(reviewForm);

        try {
            const response = await fetch('/add_review', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                const newReview = document.createElement('div');
                newReview.classList.add('review-card');
                newReview.innerHTML = `
                    <p class="review-message">${result.review.message}</p>
                    <p class="review-author">— ${result.review.name}</p>
                `;
                reviewList.prepend(newReview);
                reviewForm.reset();
            } else {
                alert('Ошибка при отправке отзыва');
            }
        } catch (err) {
            console.error(err);
            alert('Ошибка соединения с сервером');
        }
    });
});
