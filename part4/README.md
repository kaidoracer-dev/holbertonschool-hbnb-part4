HBnB - Part 4: Simple Web Client
Description
Front-end web client for the HBnB application using HTML5, CSS3 and JavaScript ES6.
Pages

index.html — List of places with price filter
login.html — User login form
place.html — Place details and reviews
add_review.html — Add a review (authenticated users only)

Files
part4/
├── index.html
├── login.html
├── place.html
├── add_review.html
├── scripts.js
├── styles.css
└── images/
    └── icon.png
How to run
1. Start the API (part3)
bashcd part3
source venv/bin/activate
python3 run.py
2. Start the front-end
bashcd part4
python3 -m http.server 8080
3. Open in browser
http://localhost:8080
Features

JWT authentication stored in cookies
Dynamic place listing fetched from API
Client-side price filtering
Place details with reviews
Add review form (authenticated users only)

Login

Go to login.html
Enter your email and password
On success, the JWT token is stored in a cookie and you are redirected to the main page
On failure, an error message is displayed

Once logged in, the login button is hidden and you get access to the add review form.
Add a Review

Go to a place and click Add a Review (only visible if logged in)
Select a rating from 1 to 5
Write your comment
Click Submit Review

The review is sent to the API with your JWT token in the Authorization header.
If you are not logged in, you are automatically redirected to the main page.