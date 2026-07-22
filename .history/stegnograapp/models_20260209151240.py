<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelSafe - User Profile</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --deep-blue: #0a0f2b;
            --dark-blue: #111827;
            --medium-blue: #1e293b;
            --accent-blue: #3b82f6;
            --light-blue: #60a5fa;
            --bright-blue: #93c5fd;
            --neon-blue: #00d9ff;
            --text-light: #e5e7eb;
            --text-muted: #9ca3af;
            --gradient: linear-gradient(135deg, var(--accent-blue), var(--light-blue));
            --neon-gradient: linear-gradient(135deg, var(--neon-blue), var(--light-blue));
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--deep-blue) 0%, var(--dark-blue) 100%);
            color: var(--text-light);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Header & Navigation */
        .navbar {
            background: rgba(10, 15, 43, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .navbar-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5rem;
            font-weight: 700;
            text-decoration: none;
            color: var(--text-light);
        }
        
        .logo span {
            background: var(--neon-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
        }
        
        .nav-links {
            display: flex;
            gap: 25px;
            list-style: none;
        }
        
        .nav-links a {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .nav-links a:hover {
            color: var(--light-blue);
        }
        
        .nav-links a::after {
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: -5px;
            left: 0;
            background: var(--neon-gradient);
            transition: width 0.3s ease;
        }
        
        .nav-links a:hover::after {
            width: 100%;
        }
        
        /* Main Content */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" opacity="0.03"><polygon fill="%2300d9ff" points="0,1000 0,0 1000,0"/></svg>');
            background-size: cover;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .dashboard-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #fff, var(--bright-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .dashboard-header p {
            color: var(--text-muted);
            font-size: 1.1rem;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        
        /* Profile Card */
        .profile-card {
            background: linear-gradient(135deg, var(--medium-blue), var(--dark-blue));
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            z-index: 1;
        }
        
        .profile-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }
        
        .profile-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .profile-avatar {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid var(--accent-blue);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .profile-avatar:hover {
            border-color: var(--neon-blue);
            box-shadow: 0 0 25px rgba(0, 217, 255, 0.4);
        }
        
        .profile-header h2 {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--text-light);
        }
        
        .profile-header p {
            color: var(--text-muted);
            font-size: 1rem;
        }
        
        .profile-info {
            margin-top: 25px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.1);
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 500;
            color: var(--text-light);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .info-label i {
            color: var(--light-blue);
            width: 20px;
        }
        
        .info-value {
            color: var(--text-muted);
        }
        
        .password-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .password-text {
            font-family: monospace;
        }
        
        .eye-button {
            background: none;
            border: none;
            color: var(--light-blue);
            cursor: pointer;
            font-size: 1rem;
            padding: 5px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        .eye-button:hover {
            color: var(--neon-blue);
            background: rgba(96, 165, 250, 0.1);
        }
        
        /* Stats Card */
        .stats-card {
            background: linear-gradient(135deg, var(--medium-blue), var(--dark-blue));
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            z-index: 1;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }
        
        .stats-header {
            margin-bottom: 25px;
        }
        
        .stats-header h3 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-light);
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        
        .stat-item {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(59, 130, 246, 0.1);
        }
        
        .stat-item:hover {
            background: rgba(30, 41, 59, 0.7);
            border-color: rgba(59, 130, 246, 0.3);
        }
        
        .stat-icon {
            font-size: 2rem;
            color: var(--light-blue);
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-light);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--text-muted);
        }
        
        /* Recent Activity */
        .activity-section {
            margin-top: 30px;
        }
        
        .activity-header {
            margin-bottom: 20px;
        }
        
        .activity-header h3 {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-light);
        }
        
        .activity-list {
            list-style: none;
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            background: rgba(30, 41, 59, 0.5);
            transition: all 0.3s ease;
        }
        
        .activity-item:hover {
            background: rgba(30, 41, 59, 0.7);
        }
        
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--gradient);
            color: white;
            font-size: 1rem;
        }
        
        .activity-content {
            flex: 1;
        }
        
        .activity-title {
            font-weight: 500;
            color: var(--text-light);
            margin-bottom: 5px;
        }
        
        .activity-time {
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        
        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            border: none;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn-primary {
            background: var(--gradient);
            color: white;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
        }
        
        .btn-outline {
            background: transparent;
            color: var(--bright-blue);
            border: 1px solid var(--bright-blue);
        }
        
        .btn-outline:hover {
            background: var(--accent-blue);
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
        }
        
        /* Floating Animation */
        .floating-shapes {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
        }
        
        .floating-shape {
            position: absolute;
            border-radius: 50%;
            background: rgba(96, 165, 250, 0.05);
            animation: float 20s infinite ease-in-out;
        }
        
        .shape-1 {
            width: 200px;
            height: 200px;
            top: 10%;
            left: 5%;
            animation-delay: 0s;
        }
        
        .shape-2 {
            width: 150px;
            height: 150px;
            top: 60%;
            right: 5%;
            animation-delay: 5s;
        }
        
        .shape-3 {
            width: 100px;
            height: 100px;
            bottom: 20%;
            left: 15%;
            animation-delay: 10s;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(10deg); }
        }
        
        /* Footer */
        footer {
            background: var(--deep-blue);
            padding: 20px 0;
            border-top: 1px solid rgba(59, 130, 246, 0.1);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 992px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .navbar-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-links {
                gap: 15px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                flex-direction: column;
            }
        }
        
        @media (max-width: 576px) {
            .container {
                padding: 20px 15px;
            }
            
            .dashboard-header h1 {
                font-size: 2rem;
            }
            
            .profile-card, .stats-card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="navbar">
        <div class="navbar-container">
            <a href="/index/" class="logo">
                <i class="fas fa-user-secret"></i>
                <span>PixelSafe</span>
            </a>
            
            <ul class="nav-links">
                <li><a href="/main/">Home</a></li>
                <li><a href="/content/">Content</a></li>
                <li><a href="/profile/" class="active">Profile</a></li>
                <li><a href="/logout/">Logout</a></li>
            </ul>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container">
        <div class="floating-shapes">
            <div class="floating-shape shape-1"></div>
            <div class="floating-shape shape-2"></div>
            <div class="floating-shape shape-3"></div>
        </div>
        
        <div class="dashboard-header">
            <h1>User Dashboard</h1>
            <p>Manage your PixelSafe account and security settings</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- Profile Card -->
            <div class="profile-card">
                <div class="profile-header">
                    {% if user.image %}
                    <img src="{{user.image.url}}" alt="Profile Picture" class="profile-avatar">
                    {% else %}
                    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdK_dnE_5cezDHypwWCPUwWlUQU0y4pwvyDA&s" alt="Profile Picture" class="profile-avatar">
                    {% endif %} 
                    <h2>{{user.username}}</h2>
                </div>
                
                <div class="profile-info">
                    <div class="info-item">
                        <span class="info-label">
                            <i class="fas fa-user"></i>
                            Username
                        </span>
                        <span class="info-value">{{user.username}}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">
                            <i class="fas fa-key"></i>
                            Password
                        </span>
                        <span class="password-container">
                            <span class="password-text" id="password">{{user.password}}</span>
                            <button class="eye-button" onclick="togglePassword()">
                                <i class="fas fa-eye"></i>
                            </button>
                        </span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">
                            <i class="fas fa-phone"></i>
                            Phone
                        </span>
                        <span class="info-value">{{user.phone}}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">
                            <i class="fas fa-envelope"></i>
                            Email
                        </span>
                        <span class="info-value">{{user.email}}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">
                            <i class="fas fa-clock"></i>
                            Last Login
                        </span>
                        <span class="info-value">Oct 8, 2025, 05:03 PM</span>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="location.href='{% url 'editprofile' %}'">
                        <i class="fas fa-edit"></i> Edit Profile
                    </button>
                    <button class="btn btn-outline">
                        <i class="fas fa-cog"></i> Settings
                    </button>
                </div>
            </div>
            
            <!-- Stats Card -->
            <div class="stats-card">
                <div class="stats-header">
                    <h3>Account Statistics</h3>
                    <p>Your PixelSafe usage and activity</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-icon">
                            <i class="fas fa-file-image"></i>
                        </div>
                        <div class="stat-value">42</div>
                        <div class="stat-label">Files Processed</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <div class="stat-value">28</div>
                        <div class="stat-label">Secure Messages</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-icon">
                            <i class="fas fa-download"></i>
                        </div>
                        <div class="stat-value">15</div>
                        <div class="stat-label">Files Downloaded</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-icon">
                            <i class="fas fa-calendar"></i>
                        </div>
                        <div class="stat-value">7</div>
                        <div class="stat-label">Days Active</div>
                    </div>
                </div>
                
                <div class="activity-section">
                    <div class="activity-header">
                        <h3>Recent Activity</h3>
                    </div>
                    
                    <ul class="activity-list">
                        <li class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-title">Encrypted image file</div>
                                <div class="activity-time">2 hours ago</div>
                            </div>
                        </li>
                        
                        <li class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-download"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-title">Downloaded secure file</div>
                                <div class="activity-time">Yesterday, 3:45 PM</div>
                            </div>
                        </li>
                        
                        <li class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-share"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-title">Shared encrypted content</div>
                                <div class="activity-time">Oct 6, 2025</div>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <div class="navbar-container">
            <p>&copy; 2023 PixelSafe. All rights reserved.</p>
        </div>
    </footer>

    <script>
        function togglePassword() {
            const passwordElement = document.getElementById('password');
            const eyeButton = document.querySelector('.eye-button i');
            const isHidden = passwordElement.textContent === '********';

            passwordElement.textContent = isHidden ? '{{user.password}}' : '********';
            eyeButton.className = isHidden ? 'fas fa-eye-slash' : 'fas fa-eye';
        }
        
        // Add subtle animation to stats
        document.querySelectorAll('.stat-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
        });
    </script>
</body>
</html>