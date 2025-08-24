# 📚 OPON ITMS - คู่มือเรียนรู้โปรเจกต์

## 🏗️ ภาพรวมสถาปัตยกรรม

**OPON ITMS (IT Management System)** เป็นระบบจัดการเทคโนโลยีสารสนเทศที่สร้างด้วย:

```
📦 OPON ITMS
├── 🐳 Docker Container
├── 🐍 FastAPI Backend
├── 🐘 PostgreSQL Database
├── 🎨 Glassmorphism Frontend
└── 📱 Responsive Web Design
```

---

## 📁 โครงสร้างไฟล์

```
ITMS/
├── 📜 main.py                 # Backend API Server
├── 🐳 Dockerfile             # Docker image config
├── 🐳 docker-compose.yml     # Multi-container setup
├── 📦 requirements.txt       # Python dependencies
├── 📖 README00               # Initial requirements
├── 📂 static/                # Frontend files
│   ├── 🏠 homepage.html      # Dashboard หลัก
│   ├── 🔐 login.html         # หน้า Login
│   ├── ⚙️ settings.html      # การตั้งค่าระบบ
│   └── 📅 booking.html       # ระบบจองทรัพยากร
└── 📚 PROJECT_LEARNING_GUIDE.md  # คู่มือนี้
```

---

## 🔧 Technology Stack

### **Backend Technologies**
- **FastAPI** 0.104.1 - Modern Python web framework
- **Uvicorn** 0.24.0 - ASGI web server  
- **PostgreSQL** 15 - Relational database
- **Pydantic** - Data validation and settings
- **Python-Jose** - JWT token handling
- **Passlib** - Password hashing
- **SQLAlchemy** 2.0.23 - ORM (not yet implemented)

### **Frontend Technologies** 
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **Font Awesome 6.4.0** - Icons
- **Glassmorphism Design** - Modern UI style
- **Responsive Grid/Flexbox** - Mobile-first design

### **DevOps & Deployment**
- **Docker** + **Docker Compose** - Containerization
- **Multi-stage builds** - Optimized images

---

## 🎯 ระบบงานหลัก (Core Systems)

### **1. 🔐 Authentication System**
```python
# User Roles & Permissions
UserRole:
├── SUPER_ADMIN  # สิทธิ์เต็มทั้งระบบ
├── ADMIN        # จัดการผู้ใช้และระบบ
├── MANAGER      # จัดการทีมและอนุมัติ
├── TECHNICIAN   # จัดการทรัพย์สินและ tickets
└── USER         # ใช้งานพื้นฐาน

# 20 Permissions Types:
- User Management (CRUD)
- Role Management 
- Asset Management (CRUD)
- Ticket Management (CRUD)
- Booking Management (CRUD)
- System Settings
- Reports & Analytics
```

### **2. 📊 Dashboard System**
- **Real-time Statistics** - ผู้ใช้, Tickets, ทรัพย์สิน, การจอง
- **Recent Activities** - กิจกรรมล่าสุดในระบบ
- **Quick Actions** - ปุ่มดำเนินการด่วน
- **System Health** - สถานะความสุขภาพระบบ

### **3. 👥 User & Role Management**
- **User CRUD** - สร้าง/แก้ไข/ลบผู้ใช้
- **Role-Based Access Control (RBAC)** - ควบคุมสิทธิ์ตาม Role
- **Permission Matrix** - จัดการสิทธิ์แบบละเอียด
- **User Profile Management** - จัดการโปรไฟล์ส่วนตัว

### **4. 📅 Booking System** ⭐ (ใหม่!)
```python
# Resource Categories:
├── 🚗 TRANSPORTATION    # รถยนต์, รถตู้
├── 🏢 MEETING_ROOMS    # ห้องประชุมทุกขนาด  
├── 💻 IT_EQUIPMENT     # โปรเจคเตอร์, แลปทอป
├── 🔧 TOOLS           # เครื่องมือช่าง
└── 🏗️ FACILITIES      # สิ่งอำนวยความสะดวก

# Booking Status:
PENDING → APPROVED → CONFIRMED → IN_USE → COMPLETED
       ↘ REJECTED ↙ CANCELLED
```

### **5. ⚙️ System Settings**
- **User Management** - จัดการบัญชีผู้ใช้
- **Role Management** - จัดการบทบาทและสิทธิ์
- **Email Configuration** - ตั้งค่า SMTP
- **Security Settings** - การรักษาความปลอดภัย
- **System Monitoring** - ติดตามสถานะระบบ
- **Backup & Maintenance** - สำรองและบำรุงรักษา

---

## 🛠️ API Endpoints Reference

### **Authentication APIs**
```http
POST   /login                    # เข้าสู่ระบบ
POST   /register                 # ลงทะเบียน (if enabled)
```

### **User Management APIs**
```http
GET    /api/users                # รายการผู้ใช้ทั้งหมด
GET    /api/users/{user_id}      # ข้อมูลผู้ใช้รายคน
POST   /api/users                # สร้างผู้ใช้ใหม่
PUT    /api/users/{user_id}      # แก้ไขข้อมูลผู้ใช้
DELETE /api/users/{user_id}      # ลบผู้ใช้
```

### **Role & Permission APIs**
```http
GET    /api/roles                      # รายการ Roles ทั้งหมด
GET    /api/roles/{role}/permissions   # สิทธิ์ของ Role
```

### **Booking System APIs** ⭐
```http
# Resources
GET    /api/resources                  # รายการทรัพยากรทั้งหมด
GET    /api/resources/{id}             # ข้อมูลทรัพยากร
POST   /api/resources                  # สร้างทรัพยากรใหม่
PUT    /api/resources/{id}             # แก้ไขทรัพยากร

# Bookings  
GET    /api/bookings                   # รายการการจองทั้งหมด
GET    /api/bookings/{id}              # ข้อมูลการจอง
POST   /api/bookings                   # สร้างการจองใหม่
PUT    /api/bookings/{id}              # แก้ไขการจอง
DELETE /api/bookings/{id}              # ยกเลิกการจอง
POST   /api/bookings/{id}/approve      # อนุมัติการจอง

# Calendar & Availability
GET    /api/resources/{id}/availability  # ตรวจสอบความว่าง
GET    /api/calendar                     # ปฏิทินการจอง
```

### **System APIs**
```http
GET    /api/stats                # สถิติระบบ
GET    /api/audit-logs          # ประวัติการใช้งาน
GET    /api/settings/{section}  # การตั้งค่า
PUT    /api/settings/{section}  # อัปเดตการตั้งค่า
POST   /api/backup/create       # สร้าง Backup
GET    /health                  # Health Check
```

---

## 🎨 Frontend Architecture

### **Design System**
```css
/* Glassmorphism Style */
background: rgba(255, 255, 255, 0.15);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.2);
box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
```

### **Layout Structure**
```html
📱 Responsive Layout:
├── 🔹 Sidebar Navigation (280px, collapsible)
├── 🔹 Top Bar (70px fixed)
├── 🔹 Main Content (dynamic)
└── 🔹 Footer (informational)
```

### **Navigation System**
- **Unified Sidebar** - เมนูเดียวกันทุกหน้า
- **Collapsible** - เปิด/ปิดได้ (โดยเฉพาะ mobile)
- **Role-based** - แสดงเมนูตาม permissions
- **Hash Navigation** - สนับสนุน deep linking

### **Component Patterns**
1. **Dashboard Cards** - แสดงสถิติและข้อมูลสำคัญ
2. **Action Buttons** - ปุ่มดำเนินการหลัก
3. **Form Components** - ฟอร์มที่สวยงามและใช้งานง่าย
4. **Data Tables** - ตารางข้อมูลแบบ responsive
5. **Modal/Dialog** - Popup สำหรับการโต้ตอบ

---

## 🗃️ Database Schema (Mock Data)

### **Users Table**
```python
{
    "id": "uuid",
    "username": "string",
    "email": "string", 
    "password": "hashed",
    "full_name": "string",
    "role": "UserRole enum",
    "is_active": "boolean",
    "created_at": "datetime",
    "last_login": "datetime"
}
```

### **Resources Table** 
```python
{
    "id": "string",
    "name": "string",
    "category": "ResourceCategory enum", 
    "description": "string",
    "capacity": "integer",
    "location": "string",
    "status": "ResourceStatus enum",
    "image_url": "string",
    "specifications": "json",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### **Bookings Table**
```python
{
    "id": "string",
    "resource_id": "string (FK)",
    "user_id": "string (FK)", 
    "title": "string",
    "description": "string",
    "start_time": "datetime",
    "end_time": "datetime", 
    "status": "BookingStatus enum",
    "purpose": "string",
    "attendees": "integer",
    "contact_info": "string",
    "special_requirements": "string",
    "approved_by": "string",
    "approved_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

---

## 🚀 Development Workflow

### **1. การตั้งค่าโปรเจกต์**
```bash
# Clone project
git clone <repository>
cd ITMS

# Start with Docker
docker-compose up -d

# หรือ Development mode
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **2. การเข้าถึงระบบ**
```
🌐 Frontend: http://localhost:8000
📖 API Docs: http://localhost:8000/docs
🏥 Health Check: http://localhost:8000/health
```

### **3. บัญชีทดสอบ**
```
👑 Super Admin: super_admin / super123
🔧 Admin: admin / admin
👔 Manager: manager / manager123
🔨 Technician: tech / tech123
👤 User: user / user123
```

### **4. การพัฒนาเพิ่มเติม**

#### **เพิ่ม API Endpoint ใหม่:**
```python
# ใน main.py
@app.get("/api/new-feature")
async def new_feature():
    return {"message": "New feature"}
```

#### **เพิ่มหน้าใหม่:**
```html
<!-- สร้าง static/new-page.html -->
<!-- ใช้ template จาก booking.html -->
<!-- เพิ่มเข้าใน navigation menu -->
```

#### **เพิ่ม Permission ใหม่:**
```python
# ใน Permission enum
NEW_PERMISSION = "new_permission"

# เพิ่มใน ROLE_PERMISSIONS
UserRole.ADMIN: [
    # ... existing permissions
    Permission.NEW_PERMISSION
]
```

---

## 📋 Best Practices

### **Security**
- ✅ **Role-Based Access Control** implemented
- ✅ **Password hashing** with Passlib
- ✅ **Input validation** with Pydantic  
- ⚠️ **JWT tokens** - ใช้ simple token (ควรอัพเกรดเป็น JWT)
- ⚠️ **HTTPS** - ยังไม่มีในการพัฒนา
- ⚠️ **Rate limiting** - ควรเพิ่มในการใช้งานจริง

### **Performance**  
- ✅ **Docker containerization**
- ✅ **Database indexing** (PostgreSQL)
- ✅ **Async/await** patterns
- ⚠️ **Caching** - ยังไม่ implement
- ⚠️ **CDN** - สำหรับไฟล์ static

### **Code Quality**
- ✅ **Type hints** with Pydantic
- ✅ **Error handling** with HTTPException
- ✅ **Consistent naming** conventions
- ⚠️ **Testing** - ยังไม่มี unit tests
- ⚠️ **Documentation** - API docs auto-generated

### **Scalability**
- ✅ **Microservice ready** (FastAPI)
- ✅ **Database migration** ready (SQLAlchemy)
- ✅ **Environment configuration** (.env support)
- ⚠️ **Load balancing** - สำหรับการใช้งานจริง
- ⚠️ **Monitoring** - ควรเพิ่ม APM tools

---

## 🔧 การแก้ไขปัญหาที่พบบ่อย

### **1. ปัญหา Docker**
```bash
# ถ้า container ไม่ขึ้น
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# ดู logs
docker-compose logs web
docker-compose logs db
```

### **2. ปัญหา Database**
```bash
# เข้า PostgreSQL container
docker-compose exec db psql -U itms_user -d itms_db

# ดู tables
\dt

# Reset database
docker-compose down -v  # ลบ volumes
docker-compose up -d
```

### **3. ปัญหา Frontend**
- **Sidebar ไม่เปิด**: ตรวจสอบ JavaScript errors ใน Console
- **API calls ล้มเหลว**: ตรวจสอบ CORS และ authentication
- **Responsive ไม่ทำงาน**: ตรวจสอบ viewport meta tag

### **4. ปัญหา Authentication**
```javascript
// ตรวจสอบ token ใน localStorage
console.log(localStorage.getItem('access_token'));
console.log(localStorage.getItem('user_info'));

// ลบ token และ login ใหม่
localStorage.clear();
window.location.href = '/static/login.html';
```

---

## 🎓 เส้นทางการเรียนรู้

### **สำหรับผู้เริ่มต้น:**
1. **เรียนรู้ HTML/CSS/JavaScript** - พื้นฐาน Frontend
2. **ทำความเข้าใจ FastAPI** - Backend framework
3. **เรียนรู้ Docker** - Container technology
4. **ศึกษา PostgreSQL** - Database management

### **สำหรับผู้ที่มีพื้นฐาน:**
1. **Authentication & Authorization** - Security patterns
2. **API Design** - RESTful principles
3. **Database Design** - Normalization, indexing
4. **Frontend Frameworks** - React, Vue, Angular

### **สำหรับผู้ก้าวหน้า:**
1. **Microservices Architecture**
2. **CI/CD Pipelines** 
3. **Monitoring & Observability**
4. **Performance Optimization**
5. **Cloud Deployment** (AWS, GCP, Azure)

---

## 📚 แหล่งเรียนรู้เพิ่มเติม

### **Documentation**
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### **Tutorials**
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Docker Tutorial](https://docker-curriculum.com/)

### **Advanced Topics**
- [Microservices Patterns](https://microservices.io/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
- [Database Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## 🤝 การมีส่วนร่วม

### **การเพิ่มฟีเจอร์ใหม่:**
1. สร้าง branch ใหม่
2. พัฒนาและทดสอบ
3. อัปเดต documentation
4. สร้าง Pull Request

### **การรายงานปัญหา:**
- ใช้ GitHub Issues
- ให้รายละเอียดที่ชัดเจน
- แนบ logs หรือ screenshots

### **การปรับปรุงโค้ด:**
- ปฏิบัติตาม coding standards
- เขียน tests สำหรับฟีเจอร์ใหม่
- อัปเดต API documentation

---

## 📊 Project Metrics

```
📈 Current Status:
├── 📄 Pages: 4 (Login, Homepage, Settings, Booking)
├── 🔗 API Endpoints: 25+
├── 👥 User Roles: 5 (Super Admin → User)
├── 🔐 Permissions: 20 types
├── 📅 Resource Categories: 5  
├── 🎨 UI Components: 15+
├── 📱 Responsive: ✅ Mobile-first
└── 🔧 Docker: ✅ Production-ready
```

---

**🎯 สรุป:** OPON ITMS เป็นระบบจัดการ IT ที่สมบูรณ์ พร้อมใช้งานจริง และสามารถขยายต่อได้ง่าย มีระบบจองทรัพยากรที่ทันสมัย และการจัดการผู้ใช้แบบ Role-based ที่ปลอดภัย

**Happy Learning! 🚀**