import React, { useState, useRef, useEffect } from 'react';
import './StudentProfile.css';
import Icon from './Icon';

const DEFAULT_MAJORS = [
  'Computer Science', 'Data Science', 'Software Engineering',
  'Information Systems', 'Cybersecurity', 'Artificial Intelligence',
];

const StudentProfile = ({ profile, setProfile, onGetRecommendations, courseCatalog, majors: majorsProp, error }) => {
  const [courseQuery, setCourseQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [newInterest, setNewInterest] = useState('');
  const dropdownRef = useRef(null);

  const majors = majorsProp && majorsProp.length > 0 ? majorsProp : DEFAULT_MAJORS;
  const years = ['Freshman', 'Sophomore', 'Junior', 'Senior'];

  const interestSuggestions = [
    'Machine Learning', 'Web Development', 'Cybersecurity', 'Data Science',
    'Mobile Development', 'Cloud Computing', 'AI/NLP', 'DevOps',
  ];

  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowDropdown(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filteredCourses = courseCatalog.filter(
    (c) =>
      !profile.completedCourses.includes(c.code) &&
      (c.code.toLowerCase().includes(courseQuery.toLowerCase()) ||
        c.name.toLowerCase().includes(courseQuery.toLowerCase()))
  );

  const addCourse = (code) => {
    if (!profile.completedCourses.includes(code)) {
      setProfile({ ...profile, completedCourses: [...profile.completedCourses, code] });
    }
    setCourseQuery('');
    setShowDropdown(false);
  };

  const removeCourse = (index) => {
    setProfile({
      ...profile,
      completedCourses: profile.completedCourses.filter((_, i) => i !== index),
    });
  };

  const addInterest = (interest) => {
    const val = interest || newInterest.trim();
    if (val && !profile.interests.includes(val)) {
      setProfile({ ...profile, interests: [...profile.interests, val] });
    }
    setNewInterest('');
  };

  const removeInterest = (index) => {
    setProfile({ ...profile, interests: profile.interests.filter((_, i) => i !== index) });
  };

  const isComplete = profile.name && profile.major && profile.careerGoals;

  return (
    <div className="student-profile">
      <h2>Student Profile</h2>
      <p className="subtitle">Fill out your info to get personalized course recommendations</p>

      {error && (
        <div className="error-message" role="alert">
          <Icon name="alert" />
          <span>{error}. Could not reach the backend. Check that it is running.</span>
        </div>
      )}

      <div className="profile-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-group">
            <label htmlFor="profile-name">Full Name</label>
            <input
              id="profile-name"
              type="text"
              autoComplete="name"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              placeholder="Your full name"
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="profile-major">Major</label>
              <select
                id="profile-major"
                value={profile.major}
                onChange={(e) => setProfile({ ...profile, major: e.target.value })}
              >
                <option value="">Select major</option>
                {majors.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="profile-year">Year</label>
              <select
                id="profile-year"
                value={profile.year}
                onChange={(e) => setProfile({ ...profile, year: e.target.value })}
              >
                {years.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="profile-credits">Credits per Semester</label>
            <input
              id="profile-credits"
              type="number"
              min="12"
              max="21"
              aria-describedby="profile-credits-help"
              value={profile.creditHoursPerSemester}
              onChange={(e) =>
                setProfile({ ...profile, creditHoursPerSemester: parseInt(e.target.value) || 15 })
              }
            />
            <small id="profile-credits-help">Typically 12 to 18 credit hours</small>
          </div>
        </div>

        <div className="form-section">
          <h3 id="completed-heading">Completed Courses</h3>
          <div
            className="course-select-wrapper"
            ref={dropdownRef}
            onKeyDown={(e) => e.key === 'Escape' && setShowDropdown(false)}
          >
            <input
              className="course-search-input"
              type="text"
              aria-labelledby="completed-heading"
              value={courseQuery}
              onChange={(e) => {
                setCourseQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              placeholder="Search courses, e.g. CS101 or Data Structures"
            />
            {showDropdown && courseQuery && filteredCourses.length > 0 && (
              <ul className="course-dropdown">
                {filteredCourses.slice(0, 8).map((c) => (
                  <li key={c.code}>
                    <button
                      type="button"
                      className="course-dropdown-item"
                      onClick={() => addCourse(c.code)}
                    >
                      <span className="code">{c.code}</span>
                      <span>{c.name}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="tags-container">
            {profile.completedCourses.length === 0 ? (
              <p className="empty-state">No courses added yet</p>
            ) : (
              profile.completedCourses.map((course, i) => (
                <span key={i} className="tag">
                  {course}
                  <button type="button" aria-label={`Remove ${course}`} onClick={() => removeCourse(i)}>
                    <Icon name="close" size={12} />
                  </button>
                </span>
              ))
            )}
          </div>
        </div>

        <div className="form-section">
          <h3>Interests & Specializations</h3>
          <div className="tags-container" style={{ marginBottom: 12 }}>
            {interestSuggestions
              .filter((s) => !profile.interests.includes(s))
              .map((s) => (
                <button
                  key={s}
                  type="button"
                  className="tag interest-tag suggestion-tag"
                  onClick={() => addInterest(s)}
                >
                  <Icon name="plus" size={12} />
                  {s}
                </button>
              ))}
          </div>
          <div className="input-with-button">
            <input
              type="text"
              aria-label="Custom interest"
              value={newInterest}
              onChange={(e) => setNewInterest(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addInterest()}
              placeholder="Or type a custom interest"
            />
            <button type="button" className="btn-add" onClick={() => addInterest()}>
              Add
            </button>
          </div>
          <div className="tags-container">
            {profile.interests.map((interest, i) => (
              <span key={i} className="tag interest-tag">
                {interest}
                <button type="button" aria-label={`Remove ${interest}`} onClick={() => removeInterest(i)}>
                  <Icon name="close" size={12} />
                </button>
              </span>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h3 id="career-heading">Career Goals</h3>
          <div className="form-group">
            <textarea
              aria-labelledby="career-heading"
              value={profile.careerGoals}
              onChange={(e) => setProfile({ ...profile, careerGoals: e.target.value })}
              placeholder="Describe your career aspirations, e.g. become a machine learning engineer at a top tech company"
              rows="4"
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-primary"
            onClick={onGetRecommendations}
            disabled={!isComplete}
            aria-describedby={!isComplete ? 'profile-incomplete' : undefined}
          >
            Get AI Recommendations
          </button>
          {!isComplete && (
            <p className="validation-message" id="profile-incomplete">
              Complete name, major, and career goals to continue
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentProfile;
