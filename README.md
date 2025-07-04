# 🚀 QuickTalk - Modern Social Media Platform

[![Django](https://img.shields.io/badge/Django-4.2.19-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com)

> A feature-rich social media platform built with Django, featuring real-time interactions, modern UI, and comprehensive social networking capabilities.

## ✨ Key Features

- 🔐 **User Authentication** - Secure login/signup system
- 💬 **Tweet & Comment** - Create posts with media support  
- ❤️ **Real-time Interactions** - AJAX like/unlike system
- 🔖 **Bookmarks** - Save favorite tweets
- 👥 **Follow System** - Connect with other users
- 🔍 **Search & Discovery** - Find users and trending topics
- 📱 **Responsive Design** - Works on all devices
- 🎨 **Modern UI** - Professional dark theme with Tailwind CSS

## 🛠️ Tech Stack

**Backend:** Django 4.2.19, SQLite, Django ORM  
**Frontend:** HTML5, Tailwind CSS, JavaScript (AJAX)  
**Features:** Media uploads, Real-time updates, Professional logging

## 🚀 Quick Setup

1. **Clone & Setup**
   ```bash
   git clone <your-repo-url>
   cd quicktalk
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Database & Run**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Access:** Visit `http://127.0.0.1:8000`

## 📁 Project Structure

```
QuickTalk/
├── authentication/     # User login/signup
├── profiles/          # User profiles & following
├── tweets/            # Posts, comments, likes
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── media/            # User uploads
```

## 🎯 Core Functionality

### **User Features**
- Create account and manage profile
- Post tweets with images/videos
- Like, comment, and bookmark posts
- Follow/unfollow other users
- Search users and discover trending topics

### **Technical Features**
- AJAX interactions for seamless UX
- Responsive design for mobile/desktop
- Professional error handling
- Optimized database queries
- Secure authentication system

## 🎨 UI Highlights

- **Professional Design** - Clean, modern interface
- **Dark Theme** - Easy on the eyes with elegant gradients
- **Interactive Elements** - Smooth animations and hover effects
- **Mobile-First** - Optimized for all screen sizes

## 📱 Main Pages

- **Home** - Timeline with tweet creation
- **Profile** - User profiles with tweets and stats
- **Bookmarks** - Saved tweets collection
- **Search** - Find users and content
- **Trending** - Popular hashtags and topics

## 🔧 Configuration

Create `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key
```

For production: Set `DEBUG=False` and configure PostgreSQL database.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push and create Pull Request

## � License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with Django & Tailwind CSS** • **Mobile-Ready** • **Production-Ready**

<p align="center">⭐ Star this repo if you find it useful! ⭐</p>