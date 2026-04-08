import React, { useState, useEffect } from 'react';
import './App.css';
import StudentProfile from './components/StudentProfile';
import CoursePlanner from './components/CoursePlanner';
import RecommendationPanel from './components/RecommendationPanel';
import PrerequisiteVisualization from './components/PrerequisiteVisualization';

///const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = process.env.REACT_APP_API_URL || 'https://course-planner-api-xxxx.onrender.com';

function App() {
  const [activeTab, setActiveTab] = useState('profile');
  const [studentProfile, setStudentProfile] = useState({
    name: '',
    major: '',
    year: 'Freshman',
    completedCourses: [],
    interests: [],
    careerGoals: '',
    creditHoursPerSemester: 15,
  });
  const [recommendations, setRecommendations] = useState([]);
  const [courseCatalog, setCourseCatalog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [planSemesters, setPlanSemesters] = useState([
    { id: 1, name: 'Fall 2025', courses: [] },
    { id: 2, name: 'Spring 2026', courses: [] },
    { id: 3, name: 'Fall 2026', courses: [] },
    { id: 4, name: 'Spring 2027', courses: [] },
  ]);

  useEffect(() => {
    fetch(`${API}/api/courses`)
      .then((r) => r.json())
      .then((data) => setCourseCatalog(data.courses || []))
      .catch(() => {});
  }, []);

  const handleGetRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentProfile),
      });
      if (!res.ok) throw new Error(`Server error (${res.status})`);
      const data = await res.json();
      setRecommendations(data);
      setActiveTab('recommendations');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToPlan = (rec) => {

    const targetSem = planSemesters.find((s) => s.name === rec.semester) || planSemesters[0];
    if (!targetSem) return;
    if (targetSem.courses.some((c) => c.courseCode === rec.courseCode)) return;
    setPlanSemesters((prev) =>
      prev.map((s) =>
        s.id === targetSem.id
          ? { ...s, courses: [...s.courses, { id: Date.now(), ...rec }] }
          : s
      )
    );
    setActiveTab('planner');
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '◉' },
    { id: 'planner', label: 'Planner', icon: '▦' },
    { id: 'recommendations', label: 'AI Recs', icon: '◈' },
    { id: 'prerequisites', label: 'Prereq Map', icon: '◎' },
  ];

  return (
    <div className="App">
      <header className="app-header">
        <h1>
          <span>●</span> Course Planner
        </h1>
        <p>AI-powered academic planning</p>
      </header>

      <nav className="tab-navigation">
        {tabs.map((tab) => (
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
        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <p>Generating recommendations…</p>
          </div>
        )}

        {!loading && activeTab === 'profile' && (
          <StudentProfile
            profile={studentProfile}
            setProfile={setStudentProfile}
            onGetRecommendations={handleGetRecommendations}
            courseCatalog={courseCatalog}
            error={error}
          />
        )}

        {!loading && activeTab === 'planner' && (
          <CoursePlanner
            semesters={planSemesters}
            setSemesters={setPlanSemesters}
            studentProfile={studentProfile}
          />
        )}

        {!loading && activeTab === 'recommendations' && (
          <RecommendationPanel
            recommendations={recommendations}
            onAddToPlan={handleAddToPlan}
          />
        )}

        {!loading && activeTab === 'prerequisites' && (
          <PrerequisiteVisualization
            completedCourses={studentProfile.completedCourses}
            courseCatalog={courseCatalog}
          />
        )}
      </main>
    </div>
  );
}

export default App;
