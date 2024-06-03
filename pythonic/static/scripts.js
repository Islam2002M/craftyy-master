document.addEventListener('DOMContentLoaded', function () {
    const rateBtn = document.getElementById('rateBtn');
    const rateModal = document.getElementById('rateModal');
    const closeBtn = document.querySelector('.close');
    const stars = document.querySelectorAll('.star');
    const submitBtn = document.getElementById('submitBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    let selectedRating = 0;

    rateBtn.onclick = function () {
        rateModal.style.display = 'block';
    }

    closeBtn.onclick = function () {
        rateModal.style.display = 'none';
    }

    cancelBtn.onclick = function () {
        rateModal.style.display = 'none';
    }

    stars.forEach(star => {
        star.onclick = function () {
            selectedRating = this.getAttribute('data-value');
            stars.forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            submitBtn.disabled = false;
        }
    });

    submitBtn.onclick = function () {
        if (selectedRating > 0) {
            fetch('/rate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ rating: selectedRating })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    rateModal.style.display = 'none';
                } else {
                    alert(data.message);
                }
            });
        }
    }

    window.onclick = function (event) {
        if (event.target == rateModal) {
            rateModal.style.display = 'none';
        }
    }
});
