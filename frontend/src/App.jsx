import React, { useState } from 'react';
import './App.css';
import StudentProfile from './components/StudentProfile';
import CoursePlanner from './components/CoursePlanner';
import RecommendationPanel from './components/RecommendationPanel';
import PrerequisiteVisualization from './components/PrerequisiteVisualization';

function App() {
  const [activeTab, setActiveTab] = useState('profile');
  const [studentProfile, setStudentProfile] = useState({
    name: '',
    major: '',
    year: 'Freshman',
    completedCourses: [],
    interests: [],
    careerGoals: '',
    creditHoursPerSemester: 15
  });
  const [coursePlan, setCoursePlan] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const tabs = [
    { id: 'profile', label: 'Student Profile', icon: '👤' },
    { id: 'planner', label: 'Course Planner', icon: '📚' },
    { id: 'recommendations', label: 'AI Recommendations', icon: '🤖' },
    { id: 'prerequisites', label: 'Prerequisites Map', icon: '🗺️' }
  ];

 const handleGetRecommendations = async () => {
  try {
    console.log('Sending profile:', studentProfile);
    
    const response = await fetch('http://localhost:8000/api/recommendations', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(studentProfile)
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const recommendations = await response.json();
    console.log('Received recommendations:', recommendations);
    
    setRecommendations(recommendations);
    setActiveTab('recommendations');
    
  } catch (error) {
    console.error('Error details:', error);
    alert(`Error: ${error.message}\n\nMake sure:\n1. Backend is running on port 8000\n2. You filled out the profile form completely`);
  }

    // // This will call the backend API once it's ready
    // console.log('Fetching recommendations for:', studentProfile);
    // // Placeholder recommendations
    // setRecommendations([
    //   {
    //     id: 1,
    //     courseCode: 'CS101',
    //     courseName: 'Introduction to Computer Science',
    //     credits: 3,
    //     semester: 'Fall 2024',
    //     reason: 'Foundation course for your major',
    //     priority: 'high'
    //   },
    //   {
    //     id: 2,
    //     courseCode: 'MATH201',
    //     courseName: 'Calculus I',
    //     credits: 4,
    //     semester: 'Fall 2024',
    //     reason: 'Required prerequisite for advanced CS courses',
    //     priority: 'high'
    //   }
    // ]);
    // setActiveTab('recommendations');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎓 AI Course Planner</h1>
        <p>Personalized academic planning powered by AI</p>
      </header>

      <nav className="tab-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </nav>

      <main className="app-content">
        {activeTab === 'profile' && (
          <StudentProfile
            profile={studentProfile}
            setProfile={setStudentProfile}
            onGetRecommendations={handleGetRecommendations}
          />
        )}
        
        {activeTab === 'planner' && (
          <CoursePlanner
            coursePlan={coursePlan}
            setCoursePlan={setCoursePlan}
            studentProfile={studentProfile}
          />
        )}
        
        {activeTab === 'recommendations' && (
          <RecommendationPanel
            recommendations={recommendations}
            onAddToPlan={(course) => {
              setCoursePlan([...coursePlan, course]);
              setActiveTab('planner');
            }}
          />
        )}
        
        {activeTab === 'prerequisites' && (
          <PrerequisiteVisualization
            completedCourses={studentProfile.completedCourses}
          />
        )}
      </main>
    </div>
  );
}

export default App;