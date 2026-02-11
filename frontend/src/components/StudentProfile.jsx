import React, { useState } from 'react';
import './StudentProfile.css';

const StudentProfile = ({ profile, setProfile, onGetRecommendations }) => {
  const [newCourse, setNewCourse] = useState('');
  const [newInterest, setNewInterest] = useState('');

  const majors = [
    'Computer Science',
    'Data Science',
    'Software Engineering',
    'Information Systems',
    'Cybersecurity',
    'Artificial Intelligence'
  ];

  const years = ['Freshman', 'Sophomore', 'Junior', 'Senior'];

  const handleAddCourse = () => {
    if (newCourse.trim()) {
      setProfile({
        ...profile,
        completedCourses: [...profile.completedCourses, newCourse.trim()]
      });
      setNewCourse('');
    }
  };

  const handleRemoveCourse = (index) => {
    setProfile({
      ...profile,
      completedCourses: profile.completedCourses.filter((_, i) => i !== index)
    });
  };

  const handleAddInterest = () => {
    if (newInterest.trim()) {
      setProfile({
        ...profile,
        interests: [...profile.interests, newInterest.trim()]
      });
      setNewInterest('');
    }
  };

  const handleRemoveInterest = (index) => {
    setProfile({
      ...profile,
      interests: profile.interests.filter((_, i) => i !== index)
    });
  };

  const isProfileComplete = profile.name && profile.major && profile.careerGoals;

  return (
    <div className="student-profile">
      <h2>Student Profile</h2>
      <p className="subtitle">Tell us about yourself to get personalized course recommendations</p>

      <div className="profile-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Major</label>
              <select
                value={profile.major}
                onChange={(e) => setProfile({ ...profile, major: e.target.value })}
              >
                <option value="">Select your major</option>
                {majors.map(major => (
                  <option key={major} value={major}>{major}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Academic Year</label>
              <select
                value={profile.year}
                onChange={(e) => setProfile({ ...profile, year: e.target.value })}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Preferred Credit Hours per Semester</label>
            <input
              type="number"
              min="12"
              max="18"
              value={profile.creditHoursPerSemester}
              onChange={(e) => setProfile({ ...profile, creditHoursPerSemester: parseInt(e.target.value) })}
            />
            <small>Typically 12-18 credit hours</small>
          </div>
        </div>

        <div className="form-section">
          <h3>Completed Courses</h3>
          <div className="input-with-button">
            <input
              type="text"
              value={newCourse}
              onChange={(e) => setNewCourse(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCourse()}
              placeholder="e.g., CS101, MATH201"
            />
            <button onClick={handleAddCourse} className="btn-add">Add</button>
          </div>
          
          <div className="tags-container">
            {profile.completedCourses.length === 0 ? (
              <p className="empty-state">No courses added yet</p>
            ) : (
              profile.completedCourses.map((course, index) => (
                <span key={index} className="tag">
                  {course}
                  <button onClick={() => handleRemoveCourse(index)}>×</button>
                </span>
              ))
            )}
          </div>
        </div>

        <div className="form-section">
          <h3>Interests & Specializations</h3>
          <div className="input-with-button">
            <input
              type="text"
              value={newInterest}
              onChange={(e) => setNewInterest(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddInterest()}
              placeholder="e.g., Machine Learning, Web Development"
            />
            <button onClick={handleAddInterest} className="btn-add">Add</button>
          </div>
          
          <div className="tags-container">
            {profile.interests.length === 0 ? (
              <p className="empty-state">No interests added yet</p>
            ) : (
              profile.interests.map((interest, index) => (
                <span key={index} className="tag interest-tag">
                  {interest}
                  <button onClick={() => handleRemoveInterest(index)}>×</button>
                </span>
              ))
            )}
          </div>
        </div>

        <div className="form-section">
          <h3>Career Goals</h3>
          <div className="form-group">
            <textarea
              value={profile.careerGoals}
              onChange={(e) => setProfile({ ...profile, careerGoals: e.target.value })}
              placeholder="Describe your career aspirations and what you'd like to achieve..."
              rows="4"
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn-primary"
            onClick={onGetRecommendations}
            disabled={!isProfileComplete}
          >
            🤖 Get AI Recommendations
          </button>
          {!isProfileComplete && (
            <p className="validation-message">Please complete all required fields</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentProfile;