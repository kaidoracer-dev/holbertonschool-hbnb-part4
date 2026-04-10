function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            await loginUser(email, password);
        });
    }
});

async function loginUser(email, password) {
    const response = await fetch('http://localhost:5000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password})
    });

    if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.href = 'index.html';
        alert('Login good');
    } else {
        alert('Login failed: ' + response.statusText);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('places-list') !== null
        && !document.getElementById('place-details')) {
        checkAuthentication();
    }
});

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

async function fetchPlaces(token) {
    const response = await fetch('http://localhost:5000/api/v1/places/', {
        headers: { 'Authorization': 'Bearer ' + token }
    });

    if (response.ok) {
        const places = await response.json();
        displayPlaces(places);
    } else {
        alert('Failed to fetch places: ' + response.statusText);
    }
}

function displayPlaces(places) {
    const list = document.getElementById('places-list');
    list.innerHTML = '';

    places.forEach(place => {
        const price = place.price_by_night ?? place.price ?? 0;

        const card = document.createElement('div');
        card.classList.add('place-card');
        card.dataset.price = price;

        card.innerHTML = `
            <h3>${place.title}</h3>
            <p>$${price} / night</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>        
        `;

        list.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        priceFilter.addEventListener('change', (event) => {
            const selected = event.target.value;
            const cards = document.querySelectorAll('.place-card');

            cards.forEach(card => {
                const price = parseFloat(card.dataset.price) || 0;
                if (selected === 'all' || price <= parseFloat(selected)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('place-details') !== null) {
        const token = getCookie('token');
        const placeId = getPlaceIdFromURL();

        const loginLink = document.getElementById('login-link');
        if (loginLink) loginLink.style.display = token ? 'none' : 'block';

        const addReviewSection = document.getElementById('add-review');
        if (addReviewSection) {
            if (token) {
                addReviewSection.style.display = 'block';
                document.getElementById('add-review-link').href = 'add_review.html?id=' + placeId;
            } else  {
                addReviewSection.style.display = 'none';
            }
        }

        if (placeId) {
            fetchPlaceDetails(token, placeId);
        }
    }
});

async function fetchPlaceDetails(token, placeId) {
    const headers = token ? { 'Authorization': 'Bearer ' + token } : {};
    const response = await fetch('http://localhost:5000/api/v1/places/' + placeId, {headers});

    if (response.ok) {
        const place = await response.json();
        displayPlaceDetails(place);
    } else {
        alert('Failed to fetch place details: ' + response.statusText)
    }
}

function displayPlaceDetails(place) {
    const detailsSection = document.getElementById('place-details');
    if (!detailsSection) return;

    const price = place.price_by_night ?? place.price ?? 0;
    const host = place.owner
        ? place.owner.first_name + ' ' + place.owner.last_name
        : 'Unknown';

    
    detailsSection.innerHTML = `
        <div class="place-details">
            <div class="place-info">
                <h2>${place.title}</h2>
                <p><strong>Host:</strong> ${host}</p>
                <p><strong>Price</strong> $${price} / night</p>
                <p><strong>Description:</strong> ${place.description || 'No description.'}</p>
                <p><strong>Amenities:</strong> ${
                    place.amenities && place.amenities.length
                        ? place.amenities.map(a => a.name || a).join(', ')
                        : 'None'
                }</p>
            </div>
        </div>
    `;
    
    const reviewSection = document.getElementById('reviews-section');
    reviewSection.innerHTML = '<h3>Reviews</h3>';

    if (place.reviews && place.reviews.length) {
        place.reviews.forEach(review => {
            const card = document.createElement('div');
            card.classList.add('review-card');
            card.innerHTML = `
                <p><strong>${review.user_name || 'Anonymous'}</strong> — ${review.rating ?? ''}/5</p>
                <p>${review.text || review.comment || ''}</p>
            `;
            reviewSection.appendChild(card);
        });
    } else {
        reviewSection.innerHTML += '<p>No reviews yet.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const reviewForm = document.getElementById('review-form');

    if (reviewForm) {

        const token = getCookie('token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }

        const loginLink = document.getElementById('login-link');
        if (loginLink) loginLink.style.display = 'none';

        const placeId = getPlaceIdFromURL();

        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const reviewText = document.getElementById('review-text').value;
            const rating = document.getElementById('rating').value;

            await sumbitReview(token, placeId, reviewText, rating);
        });
    }
});

async function sumbitReview(token, placeId, reviewText, rating) {
    const response = await fetch('http://localhost:5000/api/v1/reviews/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({
            place_id: placeId,
            text: reviewText,
            rating: parseInt(rating)
        })
    });

    const data = await response.json();
    console.log('API response:', data);

    if (response.ok) {
        alert('Review submitted successfully!');
        document.getElementById('review-form').reset();
        window.location.href = 'place.html?id=' + placeId;
    } else {
        alert('Error: ' + JSON.stringify(data));
    }
}


