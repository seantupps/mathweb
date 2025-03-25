# Mental Math Website

This project is a Django web application focused on enhancing mental math skills through interactive exercises and challenges. It utilizes Tailwind CSS for styling and Alpine.js for interactivity, providing a modern and responsive user experience.

## Features

- Interactive mental math exercises
- User-friendly interface with Tailwind CSS
- Dynamic content updates using Alpine.js
- Easy to extend and customize

## Technologies Used

- Django: A high-level Python web framework for rapid development.
- Tailwind CSS: A utility-first CSS framework for styling.
- Alpine.js: A minimal framework for composing JavaScript behavior in HTML.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mental-math-website
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

6. Open your browser and navigate to `http://127.0.0.1:8000/`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.