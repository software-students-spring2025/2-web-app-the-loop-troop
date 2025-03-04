# Digital Journal App

## Product vision statement

A digital journal app that makes it easy to write, organize, and share your thoughts, helping you stay creative and productive.

## User stories

[User Stories](https://github.com/software-students-spring2025/2-web-app-the-loop-troop/issues?q=is%3Aissue%20)  

## Steps necessary to run the software

### Prerequisites

Ensure you have the following installed:

- Python 3.x

- Virtual environment

### Setup and Running Instructions

1. **Clone the repository:**

   ```sh
   git clone https://github.com/software-students-spring2025/2-web-app-the-loop-troop.git
   cd 2-web-app-the-loop-troop
   ```

2. **Create and activate a virtual environment:**

   ```shell
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the necessary configurations, such as:

   ```sh
    MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    MONGO_DBNAME="example_db"
    FLASK_PORT="5000"
    FLASK_ENV="development" 
   ```

5. **Run the Flask app:**

   ```sh
   flask run
   ```

   The application should now be running at `http://127.0.0.1:5000/`.

## Task boards

[Task Boards](https://github.com/orgs/software-students-spring2025/projects/81)  

## Wireframes

[Wireframes](https://www.figma.com/design/GIYJwpE0LwiLDQ80Oo4iev/The-Loop-Troop?node-id=0-1&t=pa8Ij5MgOJJbVu81-1)  
