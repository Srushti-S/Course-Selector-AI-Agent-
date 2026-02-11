import React, { useState } from 'react';
import './PrerequisiteVisualization.css';

const PrerequisiteVisualization = ({ completedCourses }) => {
  const [selectedCourse, setSelectedCourse] = useState(null);

  // Sample course data with prerequisites
  const coursesData = [
    {
      code: 'CS101',
      name: 'Intro to CS',
      level: 1,
      prerequisites: [],
      status: completedCourses.includes('CS101') ? 'completed' : 'available'
    },
    {
      code: 'CS102',
      name: 'Data Structures',
      level: 2,
      prerequisites: ['CS101'],
      status: completedCourses.includes('CS102') ? 'completed' : 
              completedCourses.includes('CS101') ? 'available' : 'locked'
    },
    {
      code: 'CS201',
      name: 'Algorithms',
      level: 3,
      prerequisites: ['CS102'],
      status: completedCourses.includes('CS201') ? 'completed' : 
              completedCourses.includes('CS102') ? 'available' : 'locked'
    },
    {
      code: 'CS301',
      name: 'Advanced Algorithms',
      level: 4,
      prerequisites: ['CS201'],
      status: completedCourses.includes('CS301') ? 'completed' : 
              completedCourses.includes('CS201') ? 'available' : 'locked'
    },
    {
      code: 'MATH201',
      name: 'Calculus I',
      level: 1,
      prerequisites: [],
      status: completedCourses.includes('MATH201') ? 'completed' : 'available'
    },
    {
      code: 'MATH202',
      name: 'Calculus II',
      level: 2,
      prerequisites: ['MATH201'],
      status: completedCourses.includes('MATH202') ? 'completed' : 
              completedCourses.includes('MATH201') ? 'available' : 'locked'
    },
    {
      code: 'CS250',
      name: 'Discrete Math',
      level: 2,
      prerequisites: ['MATH201'],
      status: completedCourses.includes('CS250') ? 'completed' : 
              completedCourses.includes('MATH201') ? 'available' : 'locked'
    },
    {
      code: 'CS350',
      name: 'Machine Learning',
      level: 4,
      prerequisites: ['CS201', 'CS250', 'MATH202'],
      status: completedCourses.includes('CS350') ? 'completed' : 
              (completedCourses.includes('CS201') && 
               completedCourses.includes('CS250') && 
               completedCourses.includes('MATH202')) ? 'available' : 'locked'
    }
  ];

  const levels = [
    { level: 1, label: 'Foundation' },
    { level: 2, label: 'Intermediate' },
    { level: 3, label: 'Advanced' },
    { level: 4, label: 'Specialization' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'available':
        return '#3b82f6';
      case 'locked':
        return '#9ca3af';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'available':
        return '→';
      case 'locked':
        return '🔒';
      default:
        return '';
    }
  };

  return (
    <div className="prerequisite-visualization">
      <div className="viz-header">
        <h2>Course Prerequisites Map</h2>
        <p className="subtitle">Visualize your academic progression path</p>
      </div>

      <div className="legend">
        <div className="legend-item">
          <span className="legend-color completed"></span>
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-color available"></span>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <span className="legend-color locked"></span>
          <span>Locked</span>
        </div>
      </div>

      <div className="course-map">
        {levels.map(levelInfo => (
          <div key={levelInfo.level} className="course-level">
            <div className="level-label">
              <h3>{levelInfo.label}</h3>
              <span className="level-number">Level {levelInfo.level}</span>
            </div>
            <div className="courses-row">
              {coursesData
                .filter(course => course.level === levelInfo.level)
                .map(course => (
                  <div
                    key={course.code}
                    className={`course-node ${course.status} ${selectedCourse === course.code ? 'selected' : ''}`}
                    style={{ borderColor: getStatusColor(course.status) }}
                    onClick={() => setSelectedCourse(course.code)}
                  >
                    <div className="course-icon">
                      {getStatusIcon(course.status)}
                    </div>
                    <div className="course-code">{course.code}</div>
                    <div className="course-name">{course.name}</div>
                    {course.prerequisites.length > 0 && (
                      <div className="prerequisites-count">
                        {course.prerequisites.length} prereq{course.prerequisites.length > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {selectedCourse && (
        <div className="course-details-panel">
          {(() => {
            const course = coursesData.find(c => c.code === selectedCourse);
            return (
              <>
                <div className="panel-header">
                  <h3>{course.code}: {course.name}</h3>
                  <button onClick={() => setSelectedCourse(null)}>×</button>
                </div>
                <div className="panel-content">
                  <div className="detail-section">
                    <h4>Status</h4>
                    <p className={`status-text ${course.status}`}>
                      {course.status.charAt(0).toUpperCase() + course.status.slice(1)}
                    </p>
                  </div>
                  <div className="detail-section">
                    <h4>Prerequisites</h4>
                    {course.prerequisites.length === 0 ? (
                      <p>No prerequisites required</p>
                    ) : (
                      <ul>
                        {course.prerequisites.map(prereq => {
                          const prereqStatus = completedCourses.includes(prereq) ? 'completed' : 'not-completed';
                          return (
                            <li key={prereq} className={prereqStatus}>
                              {prereq} {prereqStatus === 'completed' ? '✓' : '✗'}
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                  <div className="detail-section">
                    <h4>Unlocks</h4>
                    {(() => {
                      const unlocks = coursesData.filter(c => 
                        c.prerequisites.includes(course.code)
                      );
                      return unlocks.length === 0 ? (
                        <p>No courses unlocked</p>
                      ) : (
                        <ul>
                          {unlocks.map(unlock => (
                            <li key={unlock.code}>{unlock.code}: {unlock.name}</li>
                          ))}
                        </ul>
                      );
                    })()}
                  </div>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default PrerequisiteVisualization;