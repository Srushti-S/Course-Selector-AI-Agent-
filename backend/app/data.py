"""
Course Catalog Data
Complete list of available courses
"""

COURSE_CATALOG = [
    # Level 1 - Foundation
    {
        "code": "CS101",
        "name": "Introduction to Computer Science",
        "credits": 3,
        "level": 1,
        "major": "Computer Science",
        "prerequisites": "None",
        "description": "Fundamental programming concepts"
    },
    {
        "code": "CS102",
        "name": "Programming Fundamentals",
        "credits": 3,
        "level": 1,
        "major": "Computer Science",
        "prerequisites": "None",
        "description": "Basic programming using Python"
    },
    {
        "code": "MATH201",
        "name": "Calculus I",
        "credits": 4,
        "level": 1,
        "major": "General",
        "prerequisites": "None",
        "description": "Differential calculus"
    },
    {
        "code": "MATH202",
        "name": "Calculus II",
        "credits": 4,
        "level": 1,
        "major": "General",
        "prerequisites": "MATH201",
        "description": "Integral calculus"
    },
    {
        "code": "STAT101",
        "name": "Introduction to Statistics",
        "credits": 3,
        "level": 1,
        "major": "General",
        "prerequisites": "None",
        "description": "Basic statistical concepts"
    },
    {
        "code": "COMM101",
        "name": "Technical Communication",
        "credits": 3,
        "level": 1,
        "major": "General",
        "prerequisites": "None",
        "description": "Writing for technical audiences"
    },
    
    # Level 2 - Intermediate
    {
        "code": "CS201",
        "name": "Data Structures and Algorithms",
        "credits": 3,
        "level": 2,
        "major": "Computer Science",
        "prerequisites": "CS101",
        "description": "Arrays, trees, graphs, hash tables"
    },
    {
        "code": "CS202",
        "name": "Object-Oriented Programming",
        "credits": 3,
        "level": 2,
        "major": "Computer Science",
        "prerequisites": "CS101",
        "description": "OOP using Java"
    },
    {
        "code": "CS250",
        "name": "Discrete Mathematics",
        "credits": 3,
        "level": 2,
        "major": "Computer Science",
        "prerequisites": "MATH201",
        "description": "Logic, sets, graph theory"
    },
    {
        "code": "CS260",
        "name": "Computer Architecture",
        "credits": 3,
        "level": 2,
        "major": "Computer Science",
        "prerequisites": "CS101",
        "description": "Hardware and assembly"
    },
    {
        "code": "MATH301",
        "name": "Linear Algebra",
        "credits": 3,
        "level": 2,
        "major": "General",
        "prerequisites": "MATH201",
        "description": "Vectors and matrices"
    },
    {
        "code": "STAT201",
        "name": "Probability Theory",
        "credits": 3,
        "level": 2,
        "major": "General",
        "prerequisites": "STAT101 and MATH201",
        "description": "Probability distributions"
    },
    {
        "code": "DS101",
        "name": "Introduction to Data Science",
        "credits": 3,
        "level": 2,
        "major": "Data Science",
        "prerequisites": "CS101 and STAT101",
        "description": "Data analysis and visualization"
    },
    
    # Level 3 - Advanced
    {
        "code": "CS301",
        "name": "Algorithm Design and Analysis",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS201 and CS250",
        "description": "Advanced algorithms and complexity"
    },
    {
        "code": "CS310",
        "name": "Database Systems",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS201",
        "description": "SQL and database design"
    },
    {
        "code": "CS320",
        "name": "Operating Systems",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS201 and CS260",
        "description": "Process and memory management"
    },
    {
        "code": "CS330",
        "name": "Computer Networks",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS201",
        "description": "TCP/IP and network protocols"
    },
    {
        "code": "CS340",
        "name": "Software Engineering",
        "credits": 3,
        "level": 3,
        "major": "Software Engineering",
        "prerequisites": "CS202",
        "description": "SDLC and Agile methodologies"
    },
    {
        "code": "CS350",
        "name": "Web Development",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS202",
        "description": "Full-stack web development"
    },
    {
        "code": "CS360",
        "name": "Mobile Application Development",
        "credits": 3,
        "level": 3,
        "major": "Computer Science",
        "prerequisites": "CS202",
        "description": "iOS and Android development"
    },
    {
        "code": "DS201",
        "name": "Machine Learning Fundamentals",
        "credits": 3,
        "level": 3,
        "major": "Data Science",
        "prerequisites": "DS101 and MATH301",
        "description": "Supervised and unsupervised learning"
    },
    {
        "code": "DS210",
        "name": "Data Mining",
        "credits": 3,
        "level": 3,
        "major": "Data Science",
        "prerequisites": "DS101 and CS201",
        "description": "Pattern recognition"
    },
    {
        "code": "CY301",
        "name": "Cybersecurity Fundamentals",
        "credits": 3,
        "level": 3,
        "major": "Cybersecurity",
        "prerequisites": "CS330",
        "description": "Security principles"
    },
    {
        "code": "CY310",
        "name": "Cryptography",
        "credits": 3,
        "level": 3,
        "major": "Cybersecurity",
        "prerequisites": "CS250",
        "description": "Encryption algorithms"
    },
    
    # Level 4 - Specialization
    {
        "code": "CS401",
        "name": "Advanced Algorithms",
        "credits": 3,
        "level": 4,
        "major": "Computer Science",
        "prerequisites": "CS301",
        "description": "Advanced algorithmic techniques"
    },
    {
        "code": "CS410",
        "name": "Artificial Intelligence",
        "credits": 3,
        "level": 4,
        "major": "Artificial Intelligence",
        "prerequisites": "CS301",
        "description": "Search and knowledge representation"
    },
    {
        "code": "CS420",
        "name": "Deep Learning",
        "credits": 3,
        "level": 4,
        "major": "Artificial Intelligence",
        "prerequisites": "DS201 and MATH301",
        "description": "Neural networks and CNNs"
    },
    {
        "code": "CS430",
        "name": "Natural Language Processing",
        "credits": 3,
        "level": 4,
        "major": "Artificial Intelligence",
        "prerequisites": "DS201",
        "description": "Text processing and language models"
    },
    {
        "code": "CS440",
        "name": "Computer Vision",
        "credits": 3,
        "level": 4,
        "major": "Artificial Intelligence",
        "prerequisites": "DS201 and MATH301",
        "description": "Image processing"
    },
    {
        "code": "CS450",
        "name": "Distributed Systems",
        "credits": 3,
        "level": 4,
        "major": "Computer Science",
        "prerequisites": "CS320 and CS330",
        "description": "Distributed computing"
    },
    {
        "code": "CS460",
        "name": "Cloud Computing",
        "credits": 3,
        "level": 4,
        "major": "Computer Science",
        "prerequisites": "CS320",
        "description": "AWS, Azure, cloud architectures"
    },
    {
        "code": "SE401",
        "name": "Software Architecture",
        "credits": 3,
        "level": 4,
        "major": "Software Engineering",
        "prerequisites": "CS340",
        "description": "Design patterns and architecture"
    },
    {
        "code": "SE410",
        "name": "DevOps and CI/CD",
        "credits": 3,
        "level": 4,
        "major": "Software Engineering",
        "prerequisites": "CS340",
        "description": "Continuous integration"
    },
    {
        "code": "DS401",
        "name": "Advanced Machine Learning",
        "credits": 3,
        "level": 4,
        "major": "Data Science",
        "prerequisites": "DS201",
        "description": "Ensemble methods and AutoML"
    },
    {
        "code": "DS410",
        "name": "Time Series Analysis",
        "credits": 3,
        "level": 4,
        "major": "Data Science",
        "prerequisites": "DS201 and STAT201",
        "description": "Forecasting techniques"
    },
    {
        "code": "CY401",
        "name": "Network Security",
        "credits": 3,
        "level": 4,
        "major": "Cybersecurity",
        "prerequisites": "CY301",
        "description": "Firewalls and IDS/IPS"
    },
    {
        "code": "CY410",
        "name": "Ethical Hacking",
        "credits": 3,
        "level": 4,
        "major": "Cybersecurity",
        "prerequisites": "CY301",
        "description": "Penetration testing"
    }
]