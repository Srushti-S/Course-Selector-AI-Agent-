import React, { useState, useMemo } from 'react';
import './PrerequisiteVisualization.css';
import Icon from './Icon';

const PrerequisiteVisualization = ({ completedCourses, courseCatalog }) => {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [majorFilter, setMajorFilter] = useState('All');

  const majors = useMemo(() => {
    const set = new Set(courseCatalog.map((c) => c.major));
    return ['All', ...Array.from(set).sort()];
  }, [courseCatalog]);

  const coursesData = useMemo(() => {
    return courseCatalog.map((c) => {
      const prereqStr = c.prerequisites || 'None';
      const prereqCodes =
        prereqStr === 'None' ? [] : prereqStr.match(/[A-Z]{2,4}\d{3}/g) || [];

      let status = 'locked';
      if (completedCourses.includes(c.code)) {
        status = 'completed';
      } else if (
        prereqCodes.length === 0 ||
        prereqCodes.every((p) => completedCourses.includes(p))
      ) {
        status = 'available';
      }

      return {
        code: c.code,
        name: c.name,
        level: c.level,
        major: c.major,
        prerequisites: prereqCodes,
        status,
        description: c.description,
        credits: c.credits,
      };
    });
  }, [courseCatalog, completedCourses]);

  const filteredCourses = useMemo(() => {
    if (majorFilter === 'All') return coursesData;
    return coursesData.filter((c) => c.major === majorFilter);
  }, [coursesData, majorFilter]);

  const levels = [
    { level: 1, label: 'Foundation' },
    { level: 2, label: 'Intermediate' },
    { level: 3, label: 'Advanced' },
    { level: 4, label: 'Specialization' },
  ];

  const statusIcon = { completed: 'check', available: 'arrow', locked: 'lock' };

  const stats = useMemo(() => ({
    completed: coursesData.filter((c) => c.status === 'completed').length,
    available: coursesData.filter((c) => c.status === 'available').length,
    total: coursesData.length,
  }), [coursesData]);

  return (
    <div className="prerequisite-visualization">
      <div className="viz-header">
        <h2>Prerequisites Map</h2>
        <p className="subtitle">
          {stats.total === 0
            ? 'Courses appear here once the catalog loads.'
            : `${stats.completed} completed, ${stats.available} available, ${stats.total} total courses`}
        </p>
      </div>

      <div className="viz-controls">
        {majors.map((m) => (
          <button
            key={m}
            type="button"
            className={`filter-btn ${majorFilter === m ? 'active' : ''}`}
            aria-pressed={majorFilter === m}
            onClick={() => setMajorFilter(m)}
          >
            {m}
          </button>
        ))}
      </div>

      <div className="legend">
        <div className="legend-item">
          <span className="legend-dot completed" />
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot available" />
          <span>Available</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot locked" />
          <span>Locked</span>
        </div>
      </div>

      <div className="course-map">
        {levels.map((lv) => {
          const lvCourses = filteredCourses.filter((c) => c.level === lv.level);
          if (lvCourses.length === 0) return null;
          return (
            <div key={lv.level} className="course-level">
              <div className="level-label">
                <h3>{lv.label}</h3>
                <span className="level-number">Level {lv.level}</span>
              </div>
              <div className="courses-row">
                {lvCourses.map((course) => (
                  <button
                    key={course.code}
                    type="button"
                    className={`course-node ${course.status} ${selectedCourse === course.code ? 'selected' : ''}`}
                    aria-pressed={selectedCourse === course.code}
                    aria-label={`${course.code}, ${course.name}, ${course.status}`}
                    onClick={() => setSelectedCourse(selectedCourse === course.code ? null : course.code)}
                  >
                    <span className="course-icon"><Icon name={statusIcon[course.status]} /></span>
                    <span className="course-code">{course.code}</span>
                    <span className="course-name">{course.name}</span>
                    {course.prerequisites.length > 0 && (
                      <span className="prerequisites-count">
                        {course.prerequisites.length} prereq{course.prerequisites.length > 1 ? 's' : ''}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {selectedCourse && (() => {
        const course = coursesData.find((c) => c.code === selectedCourse);
        if (!course) return null;
        const unlocks = coursesData.filter((c) => c.prerequisites.includes(course.code));
        return (
          <div className="course-details-panel">
            <div className="panel-header">
              <h3>{course.code}: {course.name}</h3>
              <button type="button" aria-label="Close course details" onClick={() => setSelectedCourse(null)}>
                <Icon name="close" />
              </button>
            </div>
            <div className="panel-content">
              <div className="detail-section">
                <h4>Status</h4>
                <span className={`status-text ${course.status}`}>
                  {course.status.charAt(0).toUpperCase() + course.status.slice(1)}
                </span>
              </div>
              <div className="detail-section">
                <h4>Description</h4>
                <p className="detail-text">{course.description || 'No description'}</p>
                <p className="detail-text detail-meta">{course.credits} credits, {course.major}</p>
              </div>
              <div className="detail-section">
                <h4>Prerequisites</h4>
                {course.prerequisites.length === 0 ? (
                  <p className="detail-text detail-meta">None required</p>
                ) : (
                  <ul>
                    {course.prerequisites.map((p) => (
                      <li key={p} className={completedCourses.includes(p) ? 'completed' : 'not-completed'}>
                        {p}, {completedCourses.includes(p) ? 'completed' : 'not completed'}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="detail-section">
                <h4>Unlocks ({unlocks.length})</h4>
                {unlocks.length === 0 ? (
                  <p className="detail-text detail-meta">No courses unlocked</p>
                ) : (
                  <ul>
                    {unlocks.map((u) => (
                      <li key={u.code} className="unlock-item">
                        <button type="button" onClick={() => setSelectedCourse(u.code)}>
                          {u.code}: {u.name}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};

export default PrerequisiteVisualization;
