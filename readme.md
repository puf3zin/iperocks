# Iperocks

A web application for managing and tracking climbing boulders, blocks, and sectors.

## Features

- User authentication and authorization
- Boulder management with grades and tags
- Block and sector organization
- Attempt tracking and logging
- User profiles with climbing statistics

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/iperocks.git
cd iperocks
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```bash
flask db upgrade
```

6. Run the application
```bash
flask run
```

## Technologies Used

- Flask
- SQLAlchemy
- Flask-Migrate
- Bootstrap 5
- DataTables
- jQuery

## License

[Your chosen license]