from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import os
import json
import uuid
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import asyncio

app = FastAPI(title="ITMS - IT Management System", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class Token(BaseModel):
    access_token: str
    token_type: str

class SettingsUpdate(BaseModel):
    section: str
    settings: Dict[str, Any]

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    USER = "user"

class Permission(str, Enum):
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Role Management
    MANAGE_ROLES = "manage_roles"
    ASSIGN_ROLES = "assign_roles"
    
    # System Management
    SYSTEM_SETTINGS = "system_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    BACKUP_SYSTEM = "backup_system"
    
    # Asset Management
    CREATE_ASSET = "create_asset"
    READ_ASSET = "read_asset"
    UPDATE_ASSET = "update_asset"
    DELETE_ASSET = "delete_asset"
    
    # Ticket Management
    CREATE_TICKET = "create_ticket"
    READ_TICKET = "read_ticket"
    UPDATE_TICKET = "update_ticket"
    DELETE_TICKET = "delete_ticket"
    ASSIGN_TICKET = "assign_ticket"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    
    # Booking Management
    CREATE_BOOKING = "create_booking"
    READ_BOOKING = "read_booking"
    UPDATE_BOOKING = "update_booking"
    DELETE_BOOKING = "delete_booking"
    APPROVE_BOOKING = "approve_booking"
    MANAGE_RESOURCES = "manage_resources"

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class RolePermissions(BaseModel):
    role: UserRole
    permissions: List[Permission]

class SystemStats(BaseModel):
    servers: int = 24
    users: int = 156
    tickets: int = 8
    assets: int = 342
    total_bookings: int = 0
    pending_bookings: int = 0
    approved_bookings: int = 0
    today_bookings: int = 0
    total_resources: int = 0

# Booking System Models
class ResourceCategory(str, Enum):
    TRANSPORTATION = "transportation"
    MEETING_ROOMS = "meeting_rooms" 
    IT_EQUIPMENT = "it_equipment"
    TOOLS = "tools"
    FACILITIES = "facilities"

class BookingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"
    IN_USE = "in_use"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"

class Resource(BaseModel):
    id: str
    name: str
    category: ResourceCategory
    description: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: ResourceStatus = ResourceStatus.AVAILABLE
    image_url: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class ResourceCreate(BaseModel):
    name: str
    category: ResourceCategory
    description: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ResourceCategory] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: Optional[ResourceStatus] = None
    image_url: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

class Booking(BaseModel):
    id: str
    resource_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.PENDING
    purpose: Optional[str] = None
    attendees: Optional[int] = None
    contact_info: Optional[str] = None
    special_requirements: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class BookingCreate(BaseModel):
    resource_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    purpose: Optional[str] = None
    attendees: Optional[int] = None
    contact_info: Optional[str] = None
    special_requirements: Optional[str] = None

class BookingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    purpose: Optional[str] = None
    attendees: Optional[int] = None
    contact_info: Optional[str] = None
    special_requirements: Optional[str] = None

class BookingApproval(BaseModel):
    booking_id: str
    status: BookingStatus
    notes: Optional[str] = None

# Root endpoint - serve login page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/login.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Mock database for users
MOCK_USERS = {
    "super_admin": {
        "id": str(uuid.uuid4()),
        "username": "super_admin",
        "email": "super@opon.com",
        "password": "super123",
        "full_name": "Super Administrator",
        "role": UserRole.SUPER_ADMIN,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    },
    "admin": {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "email": "admin@opon.com",
        "password": "admin",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    },
    "manager": {
        "id": str(uuid.uuid4()),
        "username": "manager",
        "email": "manager@opon.com",
        "password": "manager123",
        "full_name": "Team Manager",
        "role": UserRole.MANAGER,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    },
    "tech": {
        "id": str(uuid.uuid4()),
        "username": "tech",
        "email": "tech@opon.com",
        "password": "tech123",
        "full_name": "IT Technician",
        "role": UserRole.TECHNICIAN,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    },
    "user": {
        "id": str(uuid.uuid4()),
        "username": "user",
        "email": "user@opon.com",
        "password": "user123",
        "full_name": "Regular User",
        "role": UserRole.USER,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    }
}

# Role permissions mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.CREATE_USER, Permission.READ_USER, Permission.UPDATE_USER, Permission.DELETE_USER,
        Permission.MANAGE_ROLES, Permission.ASSIGN_ROLES,
        Permission.SYSTEM_SETTINGS, Permission.VIEW_AUDIT_LOGS, Permission.BACKUP_SYSTEM,
        Permission.CREATE_ASSET, Permission.READ_ASSET, Permission.UPDATE_ASSET, Permission.DELETE_ASSET,
        Permission.CREATE_TICKET, Permission.READ_TICKET, Permission.UPDATE_TICKET, Permission.DELETE_TICKET, Permission.ASSIGN_TICKET,
        Permission.VIEW_REPORTS, Permission.EXPORT_DATA,
        Permission.CREATE_BOOKING, Permission.READ_BOOKING, Permission.UPDATE_BOOKING, Permission.DELETE_BOOKING,
        Permission.APPROVE_BOOKING, Permission.MANAGE_RESOURCES
    ],
    UserRole.ADMIN: [
        Permission.CREATE_USER, Permission.READ_USER, Permission.UPDATE_USER, Permission.DELETE_USER,
        Permission.MANAGE_ROLES, Permission.ASSIGN_ROLES,
        Permission.SYSTEM_SETTINGS, Permission.VIEW_AUDIT_LOGS, Permission.BACKUP_SYSTEM,
        Permission.CREATE_ASSET, Permission.READ_ASSET, Permission.UPDATE_ASSET, Permission.DELETE_ASSET,
        Permission.CREATE_TICKET, Permission.READ_TICKET, Permission.UPDATE_TICKET, Permission.DELETE_TICKET, Permission.ASSIGN_TICKET,
        Permission.VIEW_REPORTS, Permission.EXPORT_DATA,
        Permission.CREATE_BOOKING, Permission.READ_BOOKING, Permission.UPDATE_BOOKING, Permission.DELETE_BOOKING,
        Permission.APPROVE_BOOKING, Permission.MANAGE_RESOURCES
    ],
    UserRole.MANAGER: [
        Permission.READ_USER, Permission.UPDATE_USER,
        Permission.READ_ASSET, Permission.UPDATE_ASSET,
        Permission.CREATE_TICKET, Permission.READ_TICKET, Permission.UPDATE_TICKET, Permission.ASSIGN_TICKET,
        Permission.VIEW_REPORTS, Permission.EXPORT_DATA,
        Permission.CREATE_BOOKING, Permission.READ_BOOKING, Permission.UPDATE_BOOKING, Permission.APPROVE_BOOKING
    ],
    UserRole.TECHNICIAN: [
        Permission.READ_USER,
        Permission.CREATE_ASSET, Permission.READ_ASSET, Permission.UPDATE_ASSET,
        Permission.CREATE_TICKET, Permission.READ_TICKET, Permission.UPDATE_TICKET,
        Permission.VIEW_REPORTS,
        Permission.CREATE_BOOKING, Permission.READ_BOOKING, Permission.UPDATE_BOOKING
    ],
    UserRole.USER: [
        Permission.READ_ASSET,
        Permission.CREATE_TICKET, Permission.READ_TICKET,
        Permission.CREATE_BOOKING, Permission.READ_BOOKING
    ]
}

# Helper functions
def get_user_permissions(role: UserRole) -> List[Permission]:
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
    user_permissions = get_user_permissions(user_role)
    return required_permission in user_permissions

def get_current_user_from_token(token: str) -> Optional[Dict]:
    # Simple token validation - in production use JWT
    if token.startswith("token_"):
        user_id = token.replace("token_", "")
        for user_data in MOCK_USERS.values():
            if user_data["id"] == user_id:
                return user_data
    return None

# Mock data for Resources
MOCK_RESOURCES = {
    # Transportation
    "resource_1": {
        "id": "resource_1",
        "name": "Toyota Camry (ABC-1234)",
        "category": ResourceCategory.TRANSPORTATION,
        "description": "รถยนต์นั่ง 4 ประตู สำหรับงานนอกสถานที่",
        "capacity": 4,
        "location": "ลานจอดรถ A1",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/car1.jpg",
        "specifications": {"fuel_type": "Gasoline", "year": "2022", "color": "Silver"},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "resource_2": {
        "id": "resource_2", 
        "name": "Honda CRV (DEF-5678)",
        "category": ResourceCategory.TRANSPORTATION,
        "description": "รถ SUV สำหรับเดินทางไกลและขนของ",
        "capacity": 5,
        "location": "ลานจอดรถ A2",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/car2.jpg",
        "specifications": {"fuel_type": "Gasoline", "year": "2023", "color": "Black"},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    
    # Meeting Rooms
    "resource_3": {
        "id": "resource_3",
        "name": "ห้องประชุม Executive",
        "category": ResourceCategory.MEETING_ROOMS,
        "description": "ห้องประชุมขนาดใหญ่ พร้อมอุปกรณ์ครบครัน",
        "capacity": 20,
        "location": "ชั้น 5 ห้อง 501",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/meeting1.jpg",
        "specifications": {"projector": True, "whiteboard": True, "ac": True, "wifi": True},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "resource_4": {
        "id": "resource_4",
        "name": "ห้องประชุม Small Team",
        "category": ResourceCategory.MEETING_ROOMS,
        "description": "ห้องประชุมขนาดเล็ก สำหรับประชุมทีม",
        "capacity": 6,
        "location": "ชั้น 3 ห้อง 302",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/meeting2.jpg", 
        "specifications": {"tv_screen": True, "whiteboard": True, "ac": True, "wifi": True},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    
    # IT Equipment
    "resource_5": {
        "id": "resource_5",
        "name": "โปรเจคเตอร์ EPSON EB-X41",
        "category": ResourceCategory.IT_EQUIPMENT,
        "description": "โปรเจคเตอร์ขนาด 3600 lumens พร้อมสาย HDMI",
        "capacity": 1,
        "location": "ห้องเก็บอุปกรณ์ IT",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/projector.jpg",
        "specifications": {"resolution": "XGA", "brightness": "3600 lumens", "connections": ["HDMI", "VGA", "USB"]},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "resource_6": {
        "id": "resource_6",
        "name": "MacBook Pro 16-inch",
        "category": ResourceCategory.IT_EQUIPMENT,
        "description": "แลปทอปสำหรับงานออกแบบและพรีเซนเทชั่น",
        "capacity": 1,
        "location": "ห้องเก็บอุปกรณ์ IT",
        "status": ResourceStatus.AVAILABLE,
        "image_url": "/static/images/laptop.jpg",
        "specifications": {"ram": "32GB", "storage": "1TB SSD", "processor": "M2 Pro"},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

# Mock data for Bookings
# Extended booking with more sample data
MOCK_BOOKINGS = {
    "booking_1": {
        "id": "booking_1",
        "resource_id": "resource_3",
        "user_id": list(MOCK_USERS.values())[1]["id"],  # admin user
        "title": "Monthly Team Meeting",
        "description": "ประชุมรายเดือนของทีมพัฒนา",
        "start_time": datetime.now() + timedelta(days=1, hours=9),
        "end_time": datetime.now() + timedelta(days=1, hours=11),
        "status": BookingStatus.APPROVED,
        "purpose": "ประชุมทีม",
        "attendees": 15,
        "contact_info": "admin@opon.com",
        "special_requirements": "ต้องการ microphone และ projector",
        "approved_by": list(MOCK_USERS.values())[0]["id"],  # super_admin
        "approved_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "recurring": False,
        "priority": "high",
        "cost_center": "IT-001",
        "tags": ["meeting", "team", "monthly"]
    },
    "booking_2": {
        "id": "booking_2", 
        "resource_id": "resource_1",
        "user_id": list(MOCK_USERS.values())[2]["id"],  # manager user
        "title": "Client Visit",
        "description": "รับลูกค้าจากสนามบิน",
        "start_time": datetime.now() + timedelta(days=2, hours=14),
        "end_time": datetime.now() + timedelta(days=2, hours=18),
        "status": BookingStatus.PENDING,
        "purpose": "รับ-ส่งลูกค้า", 
        "attendees": 2,
        "contact_info": "manager@opon.com",
        "special_requirements": None,
        "approved_by": None,
        "approved_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "recurring": False,
        "priority": "medium",
        "cost_center": "SALES-002",
        "tags": ["client", "transport"]
    },
    "booking_3": {
        "id": "booking_3",
        "resource_id": "resource_5",  # Projector
        "user_id": list(MOCK_USERS.values())[3]["id"],  # technician user
        "title": "Product Demo",
        "description": "นำเสนอผลิตภัณฑ์ให้กับลูกค้า",
        "start_time": datetime.now() + timedelta(hours=3),
        "end_time": datetime.now() + timedelta(hours=5),
        "status": BookingStatus.CONFIRMED,
        "purpose": "การนำเสนอ",
        "attendees": 8,
        "contact_info": "tech@opon.com",
        "special_requirements": "ต้องการ laptop ที่เชื่อมต่อได้",
        "approved_by": list(MOCK_USERS.values())[1]["id"],  # admin
        "approved_at": datetime.now() - timedelta(hours=2),
        "created_at": datetime.now() - timedelta(days=1),
        "updated_at": datetime.now() - timedelta(hours=1),
        "recurring": False,
        "priority": "high",
        "cost_center": "MARKETING-003",
        "tags": ["demo", "presentation", "client"]
    },
    "booking_4": {
        "id": "booking_4",
        "resource_id": "resource_4",  # Small meeting room
        "user_id": list(MOCK_USERS.values())[4]["id"],  # regular user
        "title": "Weekly Standup",
        "description": "ประชุมประจำสัปดาห์ของทีม",
        "start_time": datetime.now() + timedelta(days=7, hours=10),
        "end_time": datetime.now() + timedelta(days=7, hours=11),
        "status": BookingStatus.APPROVED,
        "purpose": "ประชุมทีม",
        "attendees": 5,
        "contact_info": "user@opon.com",
        "special_requirements": "ต้องการ whiteboard",
        "approved_by": list(MOCK_USERS.values())[2]["id"],  # manager
        "approved_at": datetime.now() - timedelta(minutes=30),
        "created_at": datetime.now() - timedelta(hours=3),
        "updated_at": datetime.now() - timedelta(minutes=30),
        "recurring": True,
        "recurring_pattern": "weekly",
        "recurring_end_date": datetime.now() + timedelta(days=90),
        "priority": "low",
        "cost_center": "DEV-004",
        "tags": ["standup", "weekly", "team"]
    }
}

# Login endpoint
@app.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    # Check if user exists and password is correct
    for username, user_data in MOCK_USERS.items():
        if user_data["username"] == user.username and user_data["password"] == user.password:
            if not user_data["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            # Update last login
            MOCK_USERS[username]["last_login"] = datetime.now()
            
            # Create token with user info
            token_data = {
                "user_id": user_data["id"],
                "username": user_data["username"],
                "role": user_data["role"],
                "permissions": get_user_permissions(user_data["role"])
            }
            
            return {
                "access_token": f"token_{user_data['id']}",
                "token_type": "bearer",
                "user": token_data
            }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

# Register endpoint
@app.post("/register")
async def register(user: UserRegister):
    # Check if username already exists
    for existing_user in MOCK_USERS.values():
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Create new user
    new_user_id = str(uuid.uuid4())
    new_user_key = f"user_{len(MOCK_USERS) + 1}"
    
    MOCK_USERS[new_user_key] = {
        "id": new_user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None
    }
    
    return {"message": f"User {user.username} registered successfully", "user_id": new_user_id}

# User Management Endpoints
@app.get("/api/users")
async def get_users(token: str = None):
    # Simple authorization check
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not has_permission(current_user["role"], Permission.READ_USER):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    users_list = []
    for user_data in MOCK_USERS.values():
        users_list.append({
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "role": user_data["role"],
            "is_active": user_data["is_active"],
            "created_at": user_data["created_at"].isoformat(),
            "last_login": user_data["last_login"].isoformat() if user_data["last_login"] else None
        })
    
    return {"users": users_list}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not has_permission(current_user["role"], Permission.READ_USER):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    for user_data in MOCK_USERS.values():
        if user_data["id"] == user_id:
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"].isoformat(),
                "last_login": user_data["last_login"].isoformat() if user_data["last_login"] else None
            }
    
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate, token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not has_permission(current_user["role"], Permission.UPDATE_USER):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Find user to update
    user_key = None
    for key, user_data in MOCK_USERS.items():
        if user_data["id"] == user_id:
            user_key = key
            break
    
    if not user_key:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user data
    if user_update.username:
        MOCK_USERS[user_key]["username"] = user_update.username
    if user_update.email:
        MOCK_USERS[user_key]["email"] = user_update.email
    if user_update.full_name:
        MOCK_USERS[user_key]["full_name"] = user_update.full_name
    if user_update.role:
        # Only super_admin can change roles to super_admin
        if user_update.role == UserRole.SUPER_ADMIN and current_user["role"] != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Only super admin can assign super admin role")
        MOCK_USERS[user_key]["role"] = user_update.role
    if user_update.is_active is not None:
        MOCK_USERS[user_key]["is_active"] = user_update.is_active
    
    return {"message": "User updated successfully"}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not has_permission(current_user["role"], Permission.DELETE_USER):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Don't allow deleting self
    if current_user["id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Find and delete user
    user_key = None
    for key, user_data in MOCK_USERS.items():
        if user_data["id"] == user_id:
            user_key = key
            break
    
    if not user_key:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting the last super admin
    if MOCK_USERS[user_key]["role"] == UserRole.SUPER_ADMIN:
        super_admin_count = sum(1 for user in MOCK_USERS.values() 
                               if user["role"] == UserRole.SUPER_ADMIN and user["is_active"])
        if super_admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last super admin")
    
    del MOCK_USERS[user_key]
    return {"message": "User deleted successfully"}

# Role Management Endpoints
@app.get("/api/roles")
async def get_roles(token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not has_permission(current_user["role"], Permission.MANAGE_ROLES):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    roles_data = []
    for role, permissions in ROLE_PERMISSIONS.items():
        roles_data.append({
            "role": role,
            "permissions": permissions,
            "description": {
                UserRole.SUPER_ADMIN: "Full system access with all permissions",
                UserRole.ADMIN: "Administrative access to most system functions",
                UserRole.MANAGER: "Team management and reporting capabilities",
                UserRole.TECHNICIAN: "Asset and ticket management access",
                UserRole.USER: "Basic user access for tickets and assets"
            }.get(role, "")
        })
    
    return {"roles": roles_data}

@app.get("/api/roles/{role}/permissions")
async def get_role_permissions(role: UserRole, token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    current_user = get_current_user_from_token(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    permissions = get_user_permissions(role)
    return {"role": role, "permissions": permissions}

# Settings endpoints
@app.get("/api/settings/{section}")
async def get_settings(section: str):
    """Get settings for a specific section"""
    # Mock settings data - in real app, fetch from database
    settings_data = {
        "users": {
            "password_policy": {
                "min_length": 8,
                "require_uppercase": True,
                "require_numbers": True,
                "require_special": False
            },
            "session_timeout": 30,
            "max_login_attempts": 5
        },
        "system": {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "itms_db"
            },
            "smtp": {
                "server": "",
                "port": 587,
                "from_email": ""
            }
        },
        "security": {
            "max_login_attempts": 5,
            "lockout_duration": 15,
            "enable_2fa": False,
            "log_login_attempts": True,
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90
        },
        "notifications": {
            "system_down": True,
            "new_user": True,
            "security_breach": True,
            "backup_complete": False
        },
        "integrations": {
            "ldap_enabled": False,
            "ldap_server": "",
            "ldap_base_dn": "",
            "api_rate_limit": 100,
            "api_logging": True
        },
        "backup": {
            "schedule": "daily",
            "time": "02:00",
            "retention_days": 30,
            "auto_clean_logs": True,
            "auto_optimize_db": False
        }
    }
    
    if section not in settings_data:
        raise HTTPException(status_code=404, detail="Settings section not found")
    
    return settings_data[section]

@app.put("/api/settings/{section}")
async def update_settings(section: str, settings: SettingsUpdate):
    """Update settings for a specific section"""
    # Mock update - in real app, save to database
    return {"message": f"{section} settings updated successfully", "settings": settings.settings}

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    import random
    
    # Calculate booking stats
    total_bookings = len(MOCK_BOOKINGS)
    pending_bookings = len([b for b in MOCK_BOOKINGS.values() if b["status"] == BookingStatus.PENDING])
    approved_bookings = len([b for b in MOCK_BOOKINGS.values() if b["status"] == BookingStatus.APPROVED])
    
    # Calculate today's bookings
    today = datetime.now().date()
    today_bookings = len([
        b for b in MOCK_BOOKINGS.values() 
        if b["start_time"].date() == today and b["status"] in [BookingStatus.APPROVED, BookingStatus.CONFIRMED, BookingStatus.IN_USE]
    ])
    
    total_resources = len(MOCK_RESOURCES)
    
    return SystemStats(
        servers=random.randint(20, 50),
        users=random.randint(100, 200),
        tickets=random.randint(5, 25),
        assets=random.randint(200, 500),
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        today_bookings=today_bookings,
        total_resources=total_resources
    )

@app.get("/api/audit-logs")
async def get_audit_logs(limit: int = 10):
    """Get audit logs"""
    from datetime import datetime, timedelta
    import random
    
    actions = ["Login", "Logout", "Settings", "User Created", "User Updated", "Backup", "System Restart"]
    users = ["admin", "john.doe", "jane.smith", "system"]
    
    logs = []
    for i in range(limit):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        logs.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "user": random.choice(users),
            "action": random.choice(actions),
            "details": f"Action performed successfully",
            "ip_address": f"192.168.1.{random.randint(100, 200)}"
        })
    
    return {"logs": logs}

@app.post("/api/backup/create")
async def create_backup():
    """Create system backup"""
    # Mock backup creation
    from datetime import datetime
    return {
        "message": "Backup created successfully",
        "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/system/test-connection")
async def test_database_connection():
    """Test database connection"""
    # Mock connection test
    return {"status": "success", "message": "Database connection successful"}

@app.post("/api/system/test-email")
async def test_email_settings():
    """Test email configuration"""
    # Mock email test
    return {"status": "success", "message": "Test email sent successfully"}

# === BOOKING SYSTEM APIs ===

# Resources APIs
@app.get("/api/resources")
async def get_resources(category: Optional[ResourceCategory] = None):
    """Get all resources, optionally filtered by category"""
    resources = list(MOCK_RESOURCES.values())
    
    if category:
        resources = [r for r in resources if r["category"] == category]
    
    return {"resources": resources}

@app.get("/api/resources/{resource_id}")
async def get_resource(resource_id: str):
    """Get a specific resource by ID"""
    if resource_id not in MOCK_RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    return {"resource": MOCK_RESOURCES[resource_id]}

@app.post("/api/resources")
async def create_resource(resource: ResourceCreate):
    """Create a new resource (Admin only)"""
    # In a real app, check user permissions here
    resource_id = f"resource_{len(MOCK_RESOURCES) + 1}"
    
    new_resource = {
        "id": resource_id,
        "name": resource.name,
        "category": resource.category,
        "description": resource.description,
        "capacity": resource.capacity,
        "location": resource.location,
        "status": ResourceStatus.AVAILABLE,
        "image_url": resource.image_url,
        "specifications": resource.specifications,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    MOCK_RESOURCES[resource_id] = new_resource
    return {"message": "Resource created successfully", "resource": new_resource}

@app.put("/api/resources/{resource_id}")
async def update_resource(resource_id: str, resource: ResourceUpdate):
    """Update a resource (Admin only)"""
    if resource_id not in MOCK_RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    existing_resource = MOCK_RESOURCES[resource_id]
    
    # Update only provided fields
    if resource.name:
        existing_resource["name"] = resource.name
    if resource.category:
        existing_resource["category"] = resource.category
    if resource.description:
        existing_resource["description"] = resource.description
    if resource.capacity:
        existing_resource["capacity"] = resource.capacity
    if resource.location:
        existing_resource["location"] = resource.location
    if resource.status:
        existing_resource["status"] = resource.status
    if resource.image_url:
        existing_resource["image_url"] = resource.image_url
    if resource.specifications:
        existing_resource["specifications"] = resource.specifications
        
    existing_resource["updated_at"] = datetime.now()
    
    return {"message": "Resource updated successfully", "resource": existing_resource}

# Bookings APIs
@app.get("/api/bookings")
async def get_bookings(
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: Optional[BookingStatus] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get bookings with optional filters"""
    bookings = list(MOCK_BOOKINGS.values())
    
    # Apply filters
    if resource_id:
        bookings = [b for b in bookings if b["resource_id"] == resource_id]
    if user_id:
        bookings = [b for b in bookings if b["user_id"] == user_id]
    if status:
        bookings = [b for b in bookings if b["status"] == status]
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            bookings = [b for b in bookings if b["start_time"] >= start_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            bookings = [b for b in bookings if b["end_time"] <= end_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    # Add resource info to each booking
    for booking in bookings:
        if booking["resource_id"] in MOCK_RESOURCES:
            booking["resource"] = MOCK_RESOURCES[booking["resource_id"]]
        
        # Add user info
        user_found = None
        for user_data in MOCK_USERS.values():
            if user_data["id"] == booking["user_id"]:
                user_found = {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "full_name": user_data.get("full_name", user_data["username"])
                }
                break
        booking["user"] = user_found
    
    return {"bookings": bookings}

@app.get("/api/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get a specific booking by ID"""
    if booking_id not in MOCK_BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking = MOCK_BOOKINGS[booking_id].copy()
    
    # Add resource and user info
    if booking["resource_id"] in MOCK_RESOURCES:
        booking["resource"] = MOCK_RESOURCES[booking["resource_id"]]
    
    for user_data in MOCK_USERS.values():
        if user_data["id"] == booking["user_id"]:
            booking["user"] = {
                "id": user_data["id"],
                "username": user_data["username"],
                "full_name": user_data.get("full_name", user_data["username"])
            }
            break
    
    return {"booking": booking}

@app.post("/api/bookings")
async def create_booking(booking: BookingCreate):
    """Create a new booking"""
    # Check if resource exists
    if booking.resource_id not in MOCK_RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if resource is available
    resource = MOCK_RESOURCES[booking.resource_id]
    if resource["status"] != ResourceStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Resource not available")
    
    # Check for time conflicts
    for existing_booking in MOCK_BOOKINGS.values():
        if (existing_booking["resource_id"] == booking.resource_id and 
            existing_booking["status"] in [BookingStatus.APPROVED, BookingStatus.CONFIRMED] and
            not (booking.end_time <= existing_booking["start_time"] or 
                 booking.start_time >= existing_booking["end_time"])):
            raise HTTPException(status_code=400, detail="Time slot already booked")
    
    booking_id = f"booking_{len(MOCK_BOOKINGS) + 1}"
    
    new_booking = {
        "id": booking_id,
        "resource_id": booking.resource_id,
        "user_id": "temp_user_id",  # In real app, get from token
        "title": booking.title,
        "description": booking.description,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "status": BookingStatus.PENDING,
        "purpose": booking.purpose,
        "attendees": booking.attendees,
        "contact_info": booking.contact_info,
        "special_requirements": booking.special_requirements,
        "approved_by": None,
        "approved_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    MOCK_BOOKINGS[booking_id] = new_booking
    return {"message": "Booking created successfully", "booking": new_booking}

@app.put("/api/bookings/{booking_id}")
async def update_booking(booking_id: str, booking: BookingUpdate):
    """Update a booking"""
    if booking_id not in MOCK_BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    existing_booking = MOCK_BOOKINGS[booking_id]
    
    # Update only provided fields
    if booking.title:
        existing_booking["title"] = booking.title
    if booking.description:
        existing_booking["description"] = booking.description
    if booking.start_time:
        existing_booking["start_time"] = booking.start_time
    if booking.end_time:
        existing_booking["end_time"] = booking.end_time
    if booking.status:
        existing_booking["status"] = booking.status
    if booking.purpose:
        existing_booking["purpose"] = booking.purpose
    if booking.attendees:
        existing_booking["attendees"] = booking.attendees
    if booking.contact_info:
        existing_booking["contact_info"] = booking.contact_info
    if booking.special_requirements:
        existing_booking["special_requirements"] = booking.special_requirements
        
    existing_booking["updated_at"] = datetime.now()
    
    return {"message": "Booking updated successfully", "booking": existing_booking}

@app.post("/api/bookings/{booking_id}/approve")
async def approve_booking(booking_id: str, approval: BookingApproval):
    """Approve or reject a booking (Manager+ only)"""
    if booking_id not in MOCK_BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking = MOCK_BOOKINGS[booking_id]
    booking["status"] = approval.status
    booking["approved_by"] = "temp_approver_id"  # In real app, get from token
    booking["approved_at"] = datetime.now()
    booking["updated_at"] = datetime.now()
    
    return {"message": f"Booking {approval.status.value} successfully", "booking": booking}

@app.delete("/api/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    """Cancel/delete a booking"""
    if booking_id not in MOCK_BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    del MOCK_BOOKINGS[booking_id]
    return {"message": "Booking cancelled successfully"}

# Calendar/availability APIs
@app.get("/api/resources/{resource_id}/availability")
async def get_resource_availability(
    resource_id: str,
    start_date: str,
    end_date: str
):
    """Get resource availability for a date range"""
    if resource_id not in MOCK_RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Get all bookings for this resource in the date range
    bookings = []
    for booking in MOCK_BOOKINGS.values():
        if (booking["resource_id"] == resource_id and 
            booking["status"] in [BookingStatus.APPROVED, BookingStatus.CONFIRMED] and
            not (booking["end_time"] <= start_dt or booking["start_time"] >= end_dt)):
            bookings.append({
                "id": booking["id"],
                "title": booking["title"],
                "start_time": booking["start_time"],
                "end_time": booking["end_time"],
                "status": booking["status"]
            })
    
    return {
        "resource_id": resource_id,
        "start_date": start_date,
        "end_date": end_date,
        "bookings": bookings
    }

@app.get("/api/calendar")
async def get_calendar_events(
    start_date: str,
    end_date: str,
    resource_id: Optional[str] = None
):
    """Get calendar events (bookings) for a date range"""
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    events = []
    for booking in MOCK_BOOKINGS.values():
        # Filter by resource if specified
        if resource_id and booking["resource_id"] != resource_id:
            continue
            
        # Filter by date range
        if not (booking["end_time"] <= start_dt or booking["start_time"] >= end_dt):
            resource_name = MOCK_RESOURCES.get(booking["resource_id"], {}).get("name", "Unknown")
            
            events.append({
                "id": booking["id"],
                "title": f"{booking['title']} ({resource_name})",
                "start": booking["start_time"].isoformat(),
                "end": booking["end_time"].isoformat(),
                "status": booking["status"],
                "resource_id": booking["resource_id"],
                "resource_name": resource_name,
                "description": booking.get("description", ""),
                "attendees": booking.get("attendees", 0)
            })
    
    return {"events": events}

# === NOTIFICATIONS SYSTEM ===

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BOOKING_APPROVED = "booking_approved"
    BOOKING_REJECTED = "booking_rejected"
    BOOKING_REMINDER = "booking_reminder"
    SYSTEM_ALERT = "system_alert"

class Notification(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    read: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None

# Mock notifications storage
MOCK_NOTIFICATIONS = {}

def create_notification(user_id: str, notification_type: NotificationType, title: str, message: str, expires_hours: int = 24):
    """Create a new notification"""
    notification_id = f"notif_{len(MOCK_NOTIFICATIONS) + 1}"
    notification = {
        "id": notification_id,
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "read": False,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=expires_hours)
    }
    MOCK_NOTIFICATIONS[notification_id] = notification
    return notification

# Initialize some sample notifications
def init_sample_notifications():
    # Sample notifications for admin user
    admin_id = list(MOCK_USERS.values())[1]["id"]  # admin user
    
    create_notification(
        admin_id,
        NotificationType.BOOKING_APPROVED,
        "การจองได้รับการอนุมัติ",
        "การจองห้องประชุม Executive ของคุณได้รับการอนุมัติแล้ว"
    )
    
    create_notification(
        admin_id,
        NotificationType.SYSTEM_ALERT,
        "การอัปเดตระบบ", 
        "ระบบจะมีการอัปเดตในวันที่ 25 สิงหาคม เวลา 02:00 น."
    )
    
    create_notification(
        admin_id,
        NotificationType.WARNING,
        "ทรัพยากรใกล้หมด",
        "อุปกรณ์ IT มีจำนวนคงเหลือน้อย กรุณาตรวจสอบ"
    )

# Initialize notifications
init_sample_notifications()

@app.get("/api/notifications")
async def get_notifications(user_id: Optional[str] = None, unread_only: bool = False):
    """Get notifications for user"""
    notifications = list(MOCK_NOTIFICATIONS.values())
    
    # Filter by user if specified
    if user_id:
        notifications = [n for n in notifications if n["user_id"] == user_id]
    
    # Filter unread only
    if unread_only:
        notifications = [n for n in notifications if not n["read"]]
    
    # Filter out expired notifications
    now = datetime.now()
    notifications = [n for n in notifications if not n["expires_at"] or n["expires_at"] > now]
    
    # Sort by created_at descending
    notifications.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"notifications": notifications, "unread_count": len([n for n in notifications if not n["read"]])}

@app.put("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    if notification_id not in MOCK_NOTIFICATIONS:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    MOCK_NOTIFICATIONS[notification_id]["read"] = True
    return {"message": "Notification marked as read"}

@app.put("/api/notifications/mark-all-read")
async def mark_all_notifications_read(user_id: str):
    """Mark all notifications as read for a user"""
    count = 0
    for notification in MOCK_NOTIFICATIONS.values():
        if notification["user_id"] == user_id and not notification["read"]:
            notification["read"] = True
            count += 1
    
    return {"message": f"Marked {count} notifications as read"}

@app.delete("/api/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete a notification"""
    if notification_id not in MOCK_NOTIFICATIONS:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    del MOCK_NOTIFICATIONS[notification_id]
    return {"message": "Notification deleted"}

# === ANALYTICS & REPORTING SYSTEM ===

class AnalyticsData(BaseModel):
    period: str
    bookings_by_day: Dict[str, int]
    popular_resources: List[Dict[str, Any]]
    user_activity: Dict[str, int]
    resource_utilization: Dict[str, float]
    booking_status_distribution: Dict[str, int]

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get analytics data for dashboard"""
    
    # Mock analytics data
    current_date = datetime.now()
    
    # Bookings by day (last 7 days)
    bookings_by_day = {}
    for i in range(7):
        day = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
        bookings_by_day[day] = len([b for b in MOCK_BOOKINGS.values() if b["start_time"].date().strftime("%Y-%m-%d") == day])
    
    # Popular resources
    resource_booking_count = {}
    for booking in MOCK_BOOKINGS.values():
        resource_id = booking["resource_id"]
        if resource_id in resource_booking_count:
            resource_booking_count[resource_id] += 1
        else:
            resource_booking_count[resource_id] = 1
    
    popular_resources = []
    for resource_id, count in sorted(resource_booking_count.items(), key=lambda x: x[1], reverse=True):
        if resource_id in MOCK_RESOURCES:
            popular_resources.append({
                "name": MOCK_RESOURCES[resource_id]["name"],
                "category": MOCK_RESOURCES[resource_id]["category"],
                "booking_count": count
            })
    
    # User activity (mock data)
    user_activity = {
        "daily_active_users": 45,
        "weekly_active_users": 156,
        "total_sessions": 324,
        "average_session_duration": "12m 34s"
    }
    
    # Resource utilization
    resource_utilization = {}
    for resource_id, resource in MOCK_RESOURCES.items():
        # Mock utilization percentage
        resource_utilization[resource["name"]] = round(len([b for b in MOCK_BOOKINGS.values() if b["resource_id"] == resource_id]) / max(len(MOCK_BOOKINGS), 1) * 100, 1)
    
    # Booking status distribution
    status_distribution = {}
    for status in BookingStatus:
        status_distribution[status.value] = len([b for b in MOCK_BOOKINGS.values() if b["status"] == status])
    
    return AnalyticsData(
        period="last_7_days",
        bookings_by_day=bookings_by_day,
        popular_resources=popular_resources,
        user_activity=user_activity,
        resource_utilization=resource_utilization,
        booking_status_distribution=status_distribution
    )

@app.get("/api/analytics/reports/{report_type}")
async def get_analytics_report(report_type: str, start_date: str, end_date: str):
    """Generate analytics reports"""
    
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Filter data by date range
    filtered_bookings = [
        b for b in MOCK_BOOKINGS.values()
        if start_dt <= b["start_time"] <= end_dt
    ]
    
    if report_type == "booking_summary":
        return {
            "report_type": "booking_summary",
            "period": f"{start_date} to {end_date}",
            "total_bookings": len(filtered_bookings),
            "approved_bookings": len([b for b in filtered_bookings if b["status"] == BookingStatus.APPROVED]),
            "cancelled_bookings": len([b for b in filtered_bookings if b["status"] == BookingStatus.CANCELLED]),
            "revenue": len(filtered_bookings) * 1000,  # Mock revenue
            "popular_resources": popular_resources[:5] if 'popular_resources' in locals() else []
        }
    
    elif report_type == "resource_utilization":
        return {
            "report_type": "resource_utilization", 
            "period": f"{start_date} to {end_date}",
            "resources": [
                {
                    "name": resource["name"],
                    "category": resource["category"],
                    "total_hours_booked": len([b for b in filtered_bookings if b["resource_id"] == resource_id]) * 2,  # Mock hours
                    "utilization_rate": round(len([b for b in filtered_bookings if b["resource_id"] == resource_id]) / max(len(filtered_bookings), 1) * 100, 1)
                }
                for resource_id, resource in MOCK_RESOURCES.items()
            ]
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

# === DATA EXPORT SYSTEM ===

@app.get("/api/export/{data_type}")
async def export_data(data_type: str, format: str = "json"):
    """Export data in various formats"""
    
    if data_type == "bookings":
        data = list(MOCK_BOOKINGS.values())
    elif data_type == "resources":
        data = list(MOCK_RESOURCES.values())
    elif data_type == "users":
        # Remove sensitive data
        data = [
            {k: v for k, v in user.items() if k != "password"}
            for user in MOCK_USERS.values()
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid data type")
    
    if format.lower() == "csv":
        # For CSV, we'll return instructions since FastAPI doesn't handle CSV directly
        return {
            "message": "CSV export",
            "data": data,
            "format": "csv",
            "instructions": "Convert this JSON to CSV using your preferred method"
        }
    
    return {
        "data": data,
        "format": format,
        "exported_at": datetime.now().isoformat(),
        "total_records": len(data)
    }

# === SYSTEM HEALTH MONITORING ===

@app.get("/api/system/health")
async def get_system_health():
    """Get comprehensive system health status"""
    
    import psutil
    import random
    
    # Mock system metrics (in real app, get from actual system)
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": {
                "status": "healthy",
                "response_time": f"{random.randint(5, 20)}ms",
                "connections": random.randint(5, 50)
            },
            "api": {
                "status": "healthy", 
                "response_time": f"{random.randint(1, 10)}ms",
                "requests_per_minute": random.randint(50, 200)
            },
            "storage": {
                "status": "healthy",
                "disk_usage": f"{random.randint(45, 75)}%",
                "available_space": f"{random.randint(50, 200)}GB"
            }
        },
        "performance": {
            "cpu_usage": f"{random.randint(20, 60)}%",
            "memory_usage": f"{random.randint(40, 80)}%",
            "active_users": random.randint(20, 100),
            "total_requests_today": random.randint(1000, 5000)
        },
        "alerts": [
            {
                "level": "warning",
                "message": "High memory usage detected",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()
            }
        ] if random.choice([True, False]) else []
    }
    
    return health_data

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get detailed system metrics"""
    
    import random
    
    # Mock metrics data
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "application": {
            "total_bookings": len(MOCK_BOOKINGS),
            "total_resources": len(MOCK_RESOURCES), 
            "total_users": len(MOCK_USERS),
            "active_sessions": random.randint(10, 50),
            "api_calls_last_hour": random.randint(100, 1000)
        },
        "performance": {
            "average_response_time": f"{random.randint(50, 200)}ms",
            "requests_per_second": random.randint(10, 100),
            "error_rate": f"{random.uniform(0.1, 2.5):.2f}%",
            "uptime": "99.9%"
        },
        "resources": {
            "most_popular": "ห้องประชุม Executive",
            "least_used": "MacBook Pro 16-inch",
            "peak_hours": "09:00-11:00, 14:00-16:00",
            "average_booking_duration": "2.5 hours"
        }
    }
    
    return metrics

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "from_email": os.getenv("FROM_EMAIL", "noreply@itms.local"),
    "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true"
}

# Email Models
class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    is_html: bool = False

class BulkEmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    template: str
    data: Dict[str, Any] = {}

class EmailTemplate(BaseModel):
    name: str
    subject: str
    html_template: str
    text_template: Optional[str] = None

# Email Templates
EMAIL_TEMPLATES = {
    "booking_approved": {
        "subject": "การจองได้รับการอนุมัติ - ITMS",
        "html_template": """
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">การจองได้รับการอนุมัติ</h2>
                <p>สวัสดี {{ user_name }},</p>
                <p>การจอง <strong>{{ resource_name }}</strong> ของคุณได้รับการอนุมัติแล้ว</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">รายละเอียดการจอง:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>ทรัพยากร:</strong> {{ resource_name }}</li>
                        <li><strong>วันที่:</strong> {{ booking_date }}</li>
                        <li><strong>เวลา:</strong> {{ start_time }} - {{ end_time }}</li>
                        <li><strong>สถานะ:</strong> <span style="color: #28a745;">อนุมัติ</span></li>
                    </ul>
                </div>
                <p>กรุณาไปใช้ทรัพยากรตามเวลาที่กำหนด</p>
                <p>ขอบคุณ,<br>ระบบ ITMS</p>
            </div>
        </body>
        </html>
        """
    },
    "booking_rejected": {
        "subject": "การจองไม่ได้รับการอนุมัติ - ITMS",
        "html_template": """
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #dc3545;">การจองไม่ได้รับการอนุมัติ</h2>
                <p>สวัสดี {{ user_name }},</p>
                <p>ขออภัย การจอง <strong>{{ resource_name }}</strong> ของคุณไม่ได้รับการอนุมัติ</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">รายละเอียดการจอง:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>ทรัพยากร:</strong> {{ resource_name }}</li>
                        <li><strong>วันที่:</strong> {{ booking_date }}</li>
                        <li><strong>เวลา:</strong> {{ start_time }} - {{ end_time }}</li>
                        <li><strong>สถานะ:</strong> <span style="color: #dc3545;">ไม่อนุมัติ</span></li>
                    </ul>
                </div>
                <p><strong>เหตุผล:</strong> {{ reason }}</p>
                <p>คุณสามารถสร้างการจองใหม่ได้ที่ระบบ ITMS</p>
                <p>ขอบคุณ,<br>ระบบ ITMS</p>
            </div>
        </body>
        </html>
        """
    },
    "system_notification": {
        "subject": "การแจ้งเตือนจากระบบ - ITMS",
        "html_template": """
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">{{ title }}</h2>
                <p>{{ message }}</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>วันที่:</strong> {{ date }}</p>
                    <p><strong>ประเภท:</strong> {{ notification_type }}</p>
                </div>
                <p>ขอบคุณ,<br>ระบบ ITMS</p>
            </div>
        </body>
        </html>
        """
    }
}

# Email Service
class EmailService:
    def __init__(self):
        self.config = EMAIL_CONFIG
    
    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None):
        """Send a single email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.config["from_email"]
            msg["To"] = to_email
            
            # Add text part if provided
            if text_body:
                text_part = MIMEText(text_body, "plain")
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.config["smtp_server"],
                port=self.config["smtp_port"],
                start_tls=self.config["use_tls"],
                username=self.config["username"] if self.config["username"] else None,
                password=self.config["password"] if self.config["password"] else None,
            )
            
            return {"status": "sent", "to": to_email}
        
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return {"status": "failed", "to": to_email, "error": str(e)}
    
    async def send_template_email(self, to_email: str, template_name: str, data: Dict[str, Any]):
        """Send email using a predefined template"""
        if template_name not in EMAIL_TEMPLATES:
            raise ValueError(f"Template {template_name} not found")
        
        template = EMAIL_TEMPLATES[template_name]
        
        # Render templates
        subject_template = Template(template["subject"])
        html_template = Template(template["html_template"])
        
        subject = subject_template.render(**data)
        html_body = html_template.render(**data)
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_bulk_email(self, recipients: List[str], template_name: str, data: Dict[str, Any]):
        """Send bulk emails using a template"""
        results = []
        
        for recipient in recipients:
            result = await self.send_template_email(recipient, template_name, data)
            results.append(result)
            # Small delay to avoid overwhelming the SMTP server
            await asyncio.sleep(0.1)
        
        return results

# Initialize email service
email_service = EmailService()

# Email API Endpoints
@app.post("/api/email/send")
async def send_email(email_request: EmailRequest, token: str):
    """Send a single email"""
    user = get_current_user_from_token(token)
    if not user or not check_permission(user, Permission.SEND_NOTIFICATIONS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        result = await email_service.send_email(
            to_email=email_request.to,
            subject=email_request.subject,
            html_body=email_request.body if email_request.is_html else f"<p>{email_request.body}</p>",
            text_body=email_request.body if not email_request.is_html else None
        )
        
        # Log the email activity
        log_activity(user["username"], "Email Sent", f"Email sent to {email_request.to}: {email_request.subject}")
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/api/email/template")
async def send_template_email(template_name: str, to_email: EmailStr, data: Dict[str, Any], token: str):
    """Send email using a predefined template"""
    user = get_current_user_from_token(token)
    if not user or not check_permission(user, Permission.SEND_NOTIFICATIONS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        result = await email_service.send_template_email(to_email, template_name, data)
        
        # Log the email activity
        log_activity(user["username"], "Template Email Sent", f"Template '{template_name}' sent to {to_email}")
        
        return {"status": "success", "result": result}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send template email: {str(e)}")

@app.post("/api/email/bulk")
async def send_bulk_email(bulk_request: BulkEmailRequest, token: str):
    """Send bulk emails using a template"""
    user = get_current_user_from_token(token)
    if not user or not check_permission(user, Permission.SEND_NOTIFICATIONS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        results = await email_service.send_bulk_email(
            recipients=bulk_request.recipients,
            template_name=bulk_request.template,
            data=bulk_request.data
        )
        
        # Log the bulk email activity
        success_count = len([r for r in results if r["status"] == "sent"])
        log_activity(user["username"], "Bulk Email Sent", f"Bulk email sent to {success_count}/{len(bulk_request.recipients)} recipients")
        
        return {"status": "success", "results": results, "summary": {
            "total": len(bulk_request.recipients),
            "sent": success_count,
            "failed": len(bulk_request.recipients) - success_count
        }}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send bulk email: {str(e)}")

@app.get("/api/email/templates")
async def get_email_templates(token: str):
    """Get available email templates"""
    user = get_current_user_from_token(token)
    if not user or not check_permission(user, Permission.READ_NOTIFICATIONS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    templates = {}
    for name, template in EMAIL_TEMPLATES.items():
        templates[name] = {
            "name": name,
            "subject": template["subject"],
            "description": f"Template for {name.replace('_', ' ').title()}"
        }
    
    return {"templates": templates}

@app.post("/api/email/test")
async def test_email_configuration(token: str):
    """Test email configuration"""
    user = get_current_user_from_token(token)
    if not user or not check_permission(user, Permission.SYSTEM_CONFIG):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        # Try to send a test email to the admin
        test_data = {
            "title": "การทดสอบระบบอีเมล",
            "message": "นี่คืออีเมลทดสอบจากระบบ ITMS เพื่อตรวจสอบการตั้งค่าอีเมล",
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "notification_type": "ทดสอบระบบ"
        }
        
        admin_email = user.get("email", "admin@itms.local")
        result = await email_service.send_template_email(admin_email, "system_notification", test_data)
        
        log_activity(user["username"], "Email Test", "Email configuration test completed")
        
        return {"status": "success", "message": "Test email sent successfully", "result": result}
    
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# Helper function to send notification emails
async def send_notification_email(user_email: str, notification_type: str, data: Dict[str, Any]):
    """Helper function to send notification emails"""
    try:
        if notification_type in EMAIL_TEMPLATES:
            await email_service.send_template_email(user_email, notification_type, data)
    except Exception as e:
        print(f"Failed to send notification email: {str(e)}")

# API Documentation will be available at /docs
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ITMS API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)