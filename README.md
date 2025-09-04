# IT Management System (ITMS)

A comprehensive IT Management System built with Django and PostgreSQL, featuring a modern login interface and full CRUD operations for IT asset management.

## Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML, CSS, JavaScript with modern UI design
- **API**: Django REST Framework

## Features

### Authentication System
- Modern ocean-themed login/signup interface
- User registration and authentication
- Session-based authentication
- Password validation

### IT Management Modules
- **Asset Management**: Track hardware assets with full lifecycle management
- **Software License Management**: Monitor software licenses and installations
- **Help Desk System**: Ticket management for IT support
- **Maintenance Records**: Track asset maintenance and repairs
- **Location & Vendor Management**: Organize assets by location and vendor
- **Category Management**: Categorize assets and tickets

### API Endpoints
- RESTful API with full CRUD operations
- Filter and search capabilities
- Dashboard statistics endpoints
- Authentication required for all endpoints

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ITMS
```

### 2. Environment Configuration
The `.env` file is already configured for development. For production, update the following variables:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DB_PASSWORD=your-secure-password
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### 4. Access the Application
- **Web Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

### 5. Create Superuser (First Time Only)
```bash
docker-compose exec web python manage.py createsuperuser
```

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL 13+

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Database Setup
Create PostgreSQL database and update `.env` file with your database credentials.

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## API Documentation

### Authentication Endpoints
- `POST /login/` - User login
- `POST /signup/` - User registration
- `GET /logout/` - User logout

### API Endpoints (Require Authentication)
- `/api/categories/` - Category CRUD operations
- `/api/locations/` - Location CRUD operations
- `/api/vendors/` - Vendor CRUD operations
- `/api/assets/` - Asset CRUD operations
- `/api/maintenance-records/` - Maintenance record CRUD operations
- `/api/software-licenses/` - Software license CRUD operations
- `/api/software-installations/` - Software installation CRUD operations
- `/api/helpdesk-tickets/` - Help desk ticket CRUD operations

### Special API Endpoints
- `GET /api/assets/by_status/` - Get asset counts by status
- `GET /api/software-licenses/expiring_soon/` - Get licenses expiring in 30 days
- `GET /api/helpdesk-tickets/dashboard_stats/` - Get ticket statistics

## Models

### Core Models
- **User** (Extended Django User): Custom user model with additional fields
- **Category**: Asset and ticket categories
- **Location**: Physical locations for assets
- **Vendor**: Supplier information

### Asset Management
- **Asset**: Main asset model with full tracking capabilities
- **MaintenanceRecord**: Asset maintenance history
- **SoftwareLicense**: Software license tracking
- **SoftwareInstallation**: Software installation records

### Help Desk
- **HelpDeskTicket**: IT support ticket system

## Development

### Adding New Features
1. Create/modify models in `itms_app/models.py`
2. Create/update serializers in `itms_app/serializers.py`
3. Add/modify views in `itms_app/views.py`
4. Update URLs in `itms_app/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Admin Interface
All models are registered in the Django admin interface with custom configurations for better management.

## Production Deployment

### Environment Variables
Update the following for production:
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_PASSWORD=secure-password
```

### Docker Production
```bash
# Use production settings
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.