# Helpline Docker Application

A comprehensive child protection helpline system built with PHP, MySQL, and Docker. This application provides a complete case management system for helplines, including call management, case tracking, AI-powered case analysis, and reporting capabilities.

## 🚀 Features

### Core Functionality
- **Case Management**: Complete case lifecycle management with client, perpetrator, and reporter tracking
- **Call Management**: Integrated SIP-based calling system with call recording and quality assurance
- **Activity Tracking**: Comprehensive activity logging and disposition management
- **User Management**: Multi-role user system with scheduling and permissions
- **Reporting**: Advanced reporting and analytics with dashboard visualization
- **AI Integration**: AI-powered case analysis and insights for improved case management

### Technical Features
- **Dockerized Architecture**: Complete containerization for easy deployment
- **REST API**: RESTful API for external integrations
- **Real-time Communication**: WebSocket support for real-time updates
- **File Management**: Secure file upload and attachment handling
- **Database**: MySQL 8.0 with comprehensive schema
- **Web Interface**: Responsive web interface with modern UI

## 🏗️ Architecture

```
helpline-docker/
├── application/           # Main web application
│   ├── app/              # JavaScript application modules
│   ├── js/               # JavaScript libraries and utilities
│   ├── images/           # Static assets and media files
│   ├── index.php         # Main application entry point
│   └── screen.css        # Application styling
├── rest_api/             # REST API backend
│   ├── api/              # API endpoints
│   ├── lib/              # PHP libraries and utilities
│   ├── config/           # Configuration files and SQL schemas
│   └── services/         # Background services
├── docker/               # Docker configuration
│   ├── nginx/            # Nginx web server configuration
│   ├── php/              # PHP-FPM configuration
│   ├── mysql/            # MySQL initialization scripts
│   └── config/           # Application configuration files
└── docker-compose.yml    # Docker Compose orchestration
```

## 🐳 Docker Services

### 1. Database Service (`helpline-db`)
- **Image**: MySQL 8.0
- **Port**: 3306
- **Features**: 
  - Automated database initialization
  - Persistent volume storage
  - User and permission management

### 2. PHP-FPM Service (`helpline-php-api`)
- **Image**: PHP 8.2-FPM
- **Features**:
  - Optimized for performance
  - MySQL extensions
  - File upload support
  - Image processing capabilities

### 3. Nginx Service (`helpline-nginx`)
- **Ports**: 8087 (HTTP), 8443 (HTTPS)
- **Features**:
  - SSL/TLS termination
  - Static file serving
  - PHP-FPM integration
  - Security headers

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 8087 and 8443 available

### Installation

1. **Clone and Navigate**
   ```bash
   # If you haven't already extracted the archive
   unzip helpline-v1.zip -d helplinev1
   cd helplinev1/helpline-docker
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Verify Installation**
   ```bash
   docker-compose ps
   ```

4. **Access Application**
   - Web Interface: http://localhost:8087/helpline/
   - API Endpoint: http://localhost:8087/helpline/api/

### First Time Setup

1. **Database Initialization**
   The database will be automatically initialized with the required schema and sample data.

2. **Default Credentials**
   - Check the application documentation for default login credentials
   - Change default passwords immediately after first login

3. **Configuration**
   - Review and update configuration files in `docker/config/`
   - Configure email settings, API keys, and other environment-specific settings

## 📊 Application Modules

### Case Management
- **Cases**: Complete case lifecycle management
- **Clients**: Client information and demographics
- **Perpetrators**: Perpetrator tracking and management
- **Reporters**: Reporter information and source tracking
- **Activities**: Case activity logging and timeline

### Communication
- **Calls**: SIP-based calling with recording
- **Messages**: SMS and messaging integration
- **Notifications**: System notifications and alerts

### Administration
- **Users**: User management and role assignment
- **Categories**: Case categorization and subcategories
- **Schedules**: Staff scheduling and availability
- **Quality Assurance**: Call quality monitoring

### AI Features
- **Case Analysis**: AI-powered case insights and recommendations
- **Risk Assessment**: Automated risk scoring and flagging
- **Report Generation**: AI-assisted report creation
- **Trend Analysis**: Pattern recognition and trend identification

## 🔧 Configuration

### Database Configuration
Located in `docker/config/config-docker.php`:
```php
// Database settings
define('DB_HOST', 'database');
define('DB_NAME', 'helpline');
define('DB_USER', 'helpline_user');
define('DB_PASS', 'helpline_pass');
```

### Environment Variables
Set in `docker-compose.yml`:
- `DB_HOST`: Database hostname
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASS`: Database password

### Nginx Configuration
- Main config: `docker/nginx/nginx.conf`
- Site config: `docker/nginx/helpline.conf`
- SSL certificates: Configure in production

## 🔍 API Documentation

### Authentication
Most API endpoints require authentication. Include session tokens in requests.

### Key Endpoints
- `GET /helpline/api/cases/` - List cases
- `POST /helpline/api/cases/` - Create new case
- `GET /helpline/api/calls/` - List calls
- `POST /helpline/api/activities/` - Log activity
- `GET /helpline/api/reports/` - Generate reports

### AI Endpoints
- `POST /helpline/api/case-analysis/` - AI case analysis
- `GET /helpline/api/insights/` - Case insights

## 📁 File Structure Details

### Application Files
- `index.php` - Main application entry point
- `app/` - JavaScript modules for different features
- `js/` - External libraries and utilities
- `screen.css` - Application styling

### API Files
- `api/index.php` - API router and handler
- `lib/` - PHP libraries and utilities
- `services/` - Background services and workers

### Configuration Files
- `config/` - Database schemas and configuration
- `docker/` - Container configuration files

## 🚨 Security Considerations

### Production Deployment
1. **Change Default Passwords**
   - Database passwords
   - Application user passwords
   - API keys and secrets

2. **SSL/TLS Configuration**
   - Obtain valid SSL certificates
   - Configure HTTPS-only access
   - Enable HSTS headers

3. **Database Security**
   - Use strong passwords
   - Restrict database access
   - Regular security updates

4. **File Permissions**
   - Secure file upload directories
   - Restrict executable permissions
   - Regular security audits

## 📈 Monitoring and Logs

### Container Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f helpline-nginx
docker-compose logs -f helpline-php-api
docker-compose logs -f helpline-db
```

### Application Logs
- PHP error logs in container
- Nginx access and error logs
- Database query logs

### Performance Monitoring
- Monitor container resource usage
- Database performance metrics
- API response times

## 🛠️ Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check database container
docker-compose exec database mysql -u helpline_user -p helpline

# Verify database initialization
docker-compose logs helpline-db
```

**Permission Issues**
```bash
# Fix file permissions
docker-compose exec php-api chown -R www-data:www-data /var/www/html
```

**Port Conflicts**
```bash
# Check port usage
netstat -an | grep :8087

# Modify ports in docker-compose.yml if needed
```

### Performance Optimization
1. **Database Optimization**
   - Regular VACUUM and ANALYZE
   - Index optimization
   - Query performance monitoring

2. **PHP Configuration**
   - Memory limits
   - Upload limits
   - OPcache configuration

3. **Nginx Optimization**
   - Static file caching
   - Gzip compression
   - Connection pooling

## 🔄 Updates and Maintenance

### Regular Maintenance
1. **Database Backups**
   ```bash
   docker-compose exec database mysqldump -u helpline_user -p helpline > backup.sql
   ```

2. **Log Rotation**
   Configure log rotation for container logs

3. **Security Updates**
   ```bash
   # Update container images
   docker-compose pull
   docker-compose up -d
   ```

### Version Updates
- Check for application updates
- Review changelog and breaking changes
- Test in staging environment first
- Backup data before updates

## 📞 Support and Documentation

### Additional Resources
- Application user manual (check `application/README.md`)
- API documentation (check `rest_api/README.md`)
- Configuration examples in `config/` directory

### Community and Support
- GitHub issues for bug reports
- Community forums for discussions
- Professional support options

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
5. Follow coding standards and best practices

---

**Note**: This is a comprehensive child protection helpline system designed for organizations managing child safety cases. Ensure proper training and protocols are in place before deploying in production environments.
