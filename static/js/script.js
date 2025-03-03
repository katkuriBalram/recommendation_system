// Ensure the script runs after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('interests-form');
    if (!form) {
        console.error('Error: Form with ID "interests-form" not found.');
        return;
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const nameInput = document.getElementById('name');
        const interestsInput = document.getElementById('interests');
        const errorDiv = document.getElementById('error-message');
        const loadingDiv = document.getElementById('loading');

        if (!nameInput || !interestsInput || !errorDiv || !loadingDiv) {
            console.error('Error: One or more DOM elements not found.');
            return;
        }

        const name = nameInput.value.trim();
        const interests = interestsInput.value.trim();

        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        if (!name) {
            errorDiv.textContent = 'Name cannot be empty!';
            errorDiv.style.display = 'block';
            console.log('Validation failed: Empty name');
            return;
        }
        if (!interests || !/^[a-zA-Z0-9,\s]+$/.test(interests)) {
            errorDiv.textContent = 'Interests must be comma-separated letters and numbers!';
            errorDiv.style.display = 'block';
            console.log('Validation failed: Invalid interests');
            return;
        }

        loadingDiv.style.display = 'block';

        const formData = new FormData();
        formData.append('name', name);
        formData.append('interests', interests);

        fetch('/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingDiv.style.display = 'none';
            console.log('Received data:', data);

            if (data.error_message) {
                errorDiv.textContent = data.error_message;
                errorDiv.style.display = 'block';
                return;
            }

            const usersList = document.getElementById('users-list');
            if (!usersList) {
                console.error('Error: users-list not found');
                return;
            }
            usersList.innerHTML = '';
            if (data.users && data.users.length > 0) {
                data.users.forEach(user => {
                    const li = document.createElement('li');
                    const img = document.createElement('img');
                    img.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&size=50&background=random`;
                    img.alt = `${user.name} Avatar`;
                    img.className = 'avatar';
                    li.appendChild(img);
                    li.appendChild(document.createTextNode(` ${user.name}: ${user.interests}`));
                    usersList.appendChild(li);
                });
            } else {
                usersList.innerHTML = '<p>No users yet!</p>';
            }

            const recSection = document.getElementById('recommendations-section');
            if (!recSection) {
                console.error('Error: recommendations-section not found');
                return;
            }
            recSection.innerHTML = '';
            if (data.users.length < 2) {
                recSection.innerHTML = '<p>At least 2 users are required for recommendations.</p>';
            } else if (data.recommendations && Object.keys(data.recommendations).length > 0) {
                for (const [user, recs] of Object.entries(data.recommendations)) {
                    const h3 = document.createElement('h3');
                    h3.textContent = user;
                    recSection.appendChild(h3);
                    const ul = document.createElement('ul');
                    recs.forEach(([recUser, similarity]) => {
                        const li = document.createElement('li');
                        const img = document.createElement('img');
                        img.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(recUser)}&size=50&background=random`;
                        img.alt = `${recUser} Avatar`;
                        img.className = 'avatar';
                        li.appendChild(img);
                        li.appendChild(document.createTextNode(` ${recUser} (Similarity: ${similarity.toFixed(2)})`));
                        ul.appendChild(li);
                    });
                    recSection.appendChild(ul);
                }
            } else {
                recSection.innerHTML = '<p>No recommendations yet! Add more users.</p>';
            }

            nameInput.value = '';
            interestsInput.value = '';
        })
        .catch(error => {
            loadingDiv.style.display = 'none';
            errorDiv.textContent = 'An error occurred. Please try again.';
            errorDiv.style.display = 'block';
            console.error('Fetch error:', error);
        });
    });
});