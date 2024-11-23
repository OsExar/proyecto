### `Recipy Project:`
Project Overview
Recipy is a dynamic web application designed to help users explore, create, and share recipes. Users can log in to their personal accounts, browse recipes by categories, add new recipes, and edit their profiles. This application serves as a central hub for culinary enthusiasts to store their favorite recipes and discover new ones.

### `Features:`

User Authentication:

Users can register and log in using secure password hashing.
Terms and conditions must be accepted during registration.
Recipe Management:

Users can add new recipes with detailed information, such as category, difficulty level, and cooking time.
Recipes are displayed by categories.
Profile Management:

Users can view and edit their profile information, including biography and preferences.
Search Functionality:

Users can search for recipes or categories using keywords.
Dynamic Categorization:

Recipes are grouped into predefined categories (e.g., Breakfast, Lunch, Dinner, Snacks, Desserts, and Appetizers).
Tech Stack
Backend:

Python (Flask framework)
SQLite database
CS50 library for database interaction
Frontend:

HTML, CSS, Bootstrap for responsive design
Jinja2 templating for dynamic content rendering
Dependencies:

Flask: Web framework
Werkzeug: Secure password hashing
CS50: Simplified database interactions

### `Setup Instructions:`
Clone the Repository:
git clone https://github.com/OsExar/proyecto
cd recipy

Install Dependencies: Ensure Python is installed on your system. Then, install the required dependencies:
pip install flask cs50
Setup Database: The project includes a preconfigured SQLite database (RecetasDB.db).

Ensure the database file is placed in the project root directory.
Run the Application: Start the Flask development server:
python app.py

The application will be accessible at http://127.0.0.1:5000.

### `routes:`


| Route                 | Method   | Description                           |
|-----------------------|----------|---------------------------------------|
| `/`                   | GET/POST | Sign in or Sign up page               |
| `/index`              | GET      | Home page showing categories          |
| `/categories-grid`    | GET      | Grid view of all categories           |
| `/add`                | GET/POST | Add a new recipe                     |
| `/add-category`       | GET/POST | Add a new recipe category            |
| `/category/<int:id>`  | GET      | View recipes in a specific category   |
| `/single-post/<int:id>` | GET    | View details of a single recipe       |
| `/search`             | GET      | Search recipes or categories          |
| `/edit-profile`       | GET/POST | Edit user profile                    |
| `/profile`            | GET      | View user profile                    |







### `Acknowledgments:`
<a href="https://github.com/OsExar"><img src="https://github.com/OsExar.png" width="200" height="200" alt="Exar"/></a>
<a href="https://github.com/Johannson27"><img src="https://github.com/Johannson27.png" width="200" height="200" alt="Exar"/></a>
