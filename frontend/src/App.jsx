import React, { useState, useEffect } from 'react';
import './App.css';
import StudentProfile from './components/StudentProfile';
import CoursePlanner from './components/CoursePlanner';
import RecommendationPanel from './components/RecommendationPanel';
import PrerequisiteVisualization from './components/PrerequisiteVisualization';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const upcomingSemesters = (count = 4) => {
  const now = new Date();
  let term = now.getMonth() <= 6 ? 'Fall' : 'Spring';
  let year = now.getMonth() <= 6 ? now.getFullYear() : now.getFullYear() + 1;
  const labels = [];
  for (let i = 0; i < count; i += 1) {
    labels.push(`${term} ${year}`);
    if (term === 'Fall') {
      term = 'Spring';
      year += 1;
    } else {
      term = 'Fall';
    }
  }
  return labels;
};

const newCourseId = () =>
  `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

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
  const [recSource, setRecSource] = useState(null);
  const [courseCatalog, setCourseCatalog] = useState([]);
  const [catalogError, setCatalogError] = useState(false);
  const [majors, setMajors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState(null);
  const [planSource, setPlanSource] = useState(null);
  const [planSemesters, setPlanSemesters] = useState(() =>
    upcomingSemesters().map((name, i) => ({ id: i + 1, name, courses: [] }))
  );

  useEffect(() => {
    fetch(`${API}/api/courses`)
      .then((r) => {
        if (!r.ok) throw new Error(`Server error (${r.status})`);
        return r.json();
      })
      .then((data) => {
        setCourseCatalog(data.courses || []);
        setCatalogError(false);
      })
      .catch(() => setCatalogError(true));

    fetch(`${API}/api/majors`)
      .then((r) => {
        if (!r.ok) throw new Error(`Server error (${r.status})`);
        return r.json();
      })
      .then((data) => setMajors(data.majors || []))
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
      setRecommendations(data.recommendations || []);
      setRecSource(data.source || null);
      setActiveTab('recommendations');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    setPlanLoading(true);
    setPlanError(null);
    try {
      const res = await fetch(`${API}/api/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentProfile),
      });
      if (res.status === 422) {
        throw new Error('Complete your profile (name, major, career goals) first');
      }
      if (!res.ok) throw new Error(`Server error (${res.status})`);
      const data = await res.json();
      const returned = data.plan || [];
      const names = [...new Set([
        ...returned.map((p) => p.semester),
        ...upcomingSemesters(),
      ])].slice(0, Math.max(4, returned.length));
      setPlanSemesters(
        names.map((name, i) => {
          const sem = returned.find((p) => p.semester === name);
          return {
            id: i + 1,
            name,
            courses: (sem ? sem.courses : []).map((c) => ({
              ...c,
              id: newCourseId(),
            })),
          };
        })
      );
      setPlanSource(data.source || null);
    } catch (e) {
      setPlanError(e.message);
    } finally {
      setPlanLoading(false);
    }
  };

  const handleAddToPlan = (rec) => {
    const targetSem = planSemesters.find((s) => s.name === rec.semester) || planSemesters[0];
    if (!targetSem) return;
    if (targetSem.courses.some((c) => c.courseCode === rec.courseCode)) return;
    setPlanSemesters((prev) =>
      prev.map((s) =>
        s.id === targetSem.id
          ? { ...s, courses: [...s.courses, { ...rec, id: newCourseId() }] }
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
        {catalogError && (
          <div className="error-message">
            ⚠ Could not load the course catalog from {API}. Course search, the
            prerequisite map, and recommendations need the backend to be running.
          </div>
        )}

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
            majors={majors}
            error={error}
          />
        )}

        {!loading && activeTab === 'planner' && (
          <CoursePlanner
            semesters={planSemesters}
            setSemesters={setPlanSemesters}
            studentProfile={studentProfile}
            onGeneratePlan={handleGeneratePlan}
            planLoading={planLoading}
            planError={planError}
            planSource={planSource}
            profileComplete={!!(studentProfile.name && studentProfile.major && studentProfile.careerGoals)}
          />
        )}

        {!loading && activeTab === 'recommendations' && (
          <RecommendationPanel
            recommendations={recommendations}
            source={recSource}
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
