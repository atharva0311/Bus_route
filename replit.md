# BusTrack - Bus Booking and Real-Time Tracking System

## Overview
BusTrack is a production-ready bus booking and real-time GPS tracking system similar to RedBus, built with Django (Python) backend and Bootstrap 5 frontend. The system features three user roles: Admin, Driver, and Passenger.

## Technology Stack
- **Backend**: Django 5.x (Python 3.11)
- **Frontend**: Django Templates, Bootstrap 5, JavaScript
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Maps**: Leaflet.js with OpenStreetMap
- **Charts**: Chart.js for analytics

## User Roles & Features

### 1. Passenger (User)
- User registration and login
- Search buses by source, destination, date
- View bus details with live tracking
- Book tickets with seat selection
- View booking history
- Track booked bus in real-time
- Cancel bookings before departure

### 2. Driver
- Driver login (accounts created by admin)
- View assigned bus and route
- Start/Stop trip functionality
- Send real-time GPS location updates
- Update trip status (Running, Delayed, Completed)
- View route on map

### 3. Admin
- Full dashboard with analytics
- CRUD operations for buses, routes, drivers
- Manage user accounts and bookings
- Monitor all buses on live map
- View performance metrics
- Analytics with charts

## Project Structure
```
bustrack/
├── bustrack/           # Django project settings
├── users/              # User management, auth, profiles
├── buses/              # Bus and route management
├── bookings/           # Booking system
├── tracking/           # GPS tracking and ETA
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── manage.py
```

## Database Models
- **UserProfile**: Extended user with roles
- **Driver**: Driver profiles with license info
- **Bus**: Bus details with route assignment
- **Route**: Source to destination routes
- **Stop**: Intermediate stops on routes
- **Booking**: Ticket bookings
- **Trip**: Daily trip instances
- **LiveLocation**: GPS coordinates
- **ETACalculation**: Arrival estimates
- **PerformanceMetrics**: Analytics data

## Running the Project

### Development
```bash
python manage.py runserver 0.0.0.0:5000
```

### Initial Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

## API Endpoints

### Tracking APIs
- `POST /tracking/api/update-location/` - Update bus GPS location
- `GET /tracking/api/bus/<bus_id>/` - Get bus location
- `GET /tracking/api/active-buses/` - Get all active buses
- `POST /tracking/api/trip/start/` - Start a trip
- `POST /tracking/api/trip/end/` - End a trip
- `POST /tracking/api/trip/status/` - Update trip status

### Bus APIs
- `GET /buses/api/routes/` - Get all routes
- `GET /buses/api/seats/<bus_id>/` - Get available seats

## Key URLs
- `/` - Home page
- `/users/login/` - User/Driver/Admin login
- `/users/register/` - User registration
- `/users/dashboard/` - User dashboard
- `/users/driver/dashboard/` - Driver dashboard
- `/admin-panel/` - Admin dashboard
- `/buses/search/` - Search buses
- `/bookings/` - My bookings

## Environment Variables
- `SESSION_SECRET`: Django secret key

## Future Enhancements (Next Phase)
- PostgreSQL database integration
- Email/SMS notifications
- Seat selection UI
- QR code ticket generation
- REST API with Django REST Framework
- Production deployment configuration
