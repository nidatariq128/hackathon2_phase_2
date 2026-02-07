# 📝 Todo App - Full-Stack Task Manager

A modern, full-stack Todo application built with Next.js, FastAPI, and PostgreSQL. Features a beautiful gradient UI design with glassmorphism effects.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user authentication
- ✅ **Task Management** - Create, read, update, delete tasks
- 🎨 **Modern UI** - Beautiful gradient design with smooth animations
- 🔄 **Real-time Updates** - Optimistic UI updates
- 📱 **Responsive Design** - Works on all devices
- 🌈 **Glassmorphism** - Frosted glass effects throughout
- 🎯 **Task Filters** - Filter by All, Pending, or Completed

## 🛠️ Tech Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Jose** - JWT token handling
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM
- **PostgreSQL** - Database (Neon)
- **Python-Jose** - JWT token generation/validation
- **Uvicorn** - ASGI server

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL database (or Neon account)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd phase2
```

2. **Set up environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# - Add your PostgreSQL DATABASE_URL
# - Generate a secure BETTER_AUTH_SECRET
```

3. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

4. **Install Backend Dependencies**
```bash
cd ../backend
pip install -r requirements.txt
```

### Running the Application

**Start Backend (Terminal 1):**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

**Access the app:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
phase2/
├── frontend/              # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/             # Utilities and API clients
│   └── package.json
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── api/        # API routes
│   │   ├── models/     # Database models
│   │   └── main.py     # App entry point
│   └── requirements.txt
├── specs/               # Feature specifications
├── history/             # Development history
└── README.md
```

## 🎨 UI Features

- **Gradient Theme** - Blue to purple gradient throughout
- **Glassmorphism Cards** - Frosted glass effect with backdrop blur
- **Smooth Animations** - Hover effects and transitions
- **Custom Checkboxes** - Circular gradient checkboxes
- **Status Badges** - Color-coded task status
- **Responsive Layout** - Mobile-friendly design

## 🔐 Authentication

The app uses JWT (JSON Web Tokens) for authentication:
- Tokens are signed with HS256 algorithm
- Stored in browser localStorage
- Automatically injected in API requests
- 7-day expiration

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Tasks
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get task details
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🌐 Deployment

### Frontend (Vercel)
1. Push to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

### Backend (Railway/Render)
1. Push to GitHub
2. Create new service
3. Set environment variables
4. Deploy

## 📄 License

MIT License - feel free to use this project for learning or production.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Built with ❤️ using Next.js and FastAPI
