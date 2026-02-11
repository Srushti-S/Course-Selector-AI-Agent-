import React, { useState } from 'react';
import './CoursePlanner.css';

const CoursePlanner = ({ coursePlan, setCoursePlan, studentProfile }) => {
  const [semesters, setSemesters] = useState([
    { id: 1, name: 'Fall 2024', courses: [] },
    { id: 2, name: 'Spring 2025', courses: [] },
    { id: 3, name: 'Fall 2025', courses: [] },
    { id: 4, name: 'Spring 2026', courses: [] }
  ]);

  const [draggedCourse, setDraggedCourse] = useState(null);
  const [showAddCourseModal, setShowAddCourseModal] = useState(false);
  const [selectedSemester, setSelectedSemester] = useState(null);
  const [newCourseData, setNewCourseData] = useState({
    courseCode: '',
    courseName: '',
    credits: 3
  });

  const handleDragStart = (course, sourceSemesterId) => {
    setDraggedCourse({ course, sourceSemesterId });
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (targetSemesterId) => {
    if (!draggedCourse) return;

    const updatedSemesters = semesters.map(semester => {
      if (semester.id === draggedCourse.sourceSemesterId) {
        return {
          ...semester,
          courses: semester.courses.filter(c => c.id !== draggedCourse.course.id)
        };
      }
      if (semester.id === targetSemesterId) {
        return {
          ...semester,
          courses: [...semester.courses, draggedCourse.course]
        };
      }
      return semester;
    });

    setSemesters(updatedSemesters);
    setDraggedCourse(null);
  };

  const addSemester = () => {
    const newSemester = {
      id: semesters.length + 1,
      name: `Semester ${semesters.length + 1}`,
      courses: []
    };
    setSemesters([...semesters, newSemester]);
  };

  const removeSemester = (semesterId) => {
    if (semesters.length > 1) {
      setSemesters(semesters.filter(s => s.id !== semesterId));
    }
  };

  const openAddCourseModal = (semesterId) => {
    setSelectedSemester(semesterId);
    setShowAddCourseModal(true);
  };

  const handleAddCourse = () => {
    if (newCourseData.courseCode && newCourseData.courseName) {
      const course = {
        id: Date.now(),
        ...newCourseData
      };

      const updatedSemesters = semesters.map(semester => {
        if (semester.id === selectedSemester) {
          return {
            ...semester,
            courses: [...semester.courses, course]
          };
        }
        return semester;
      });

      setSemesters(updatedSemesters);
      setShowAddCourseModal(false);
      setNewCourseData({ courseCode: '', courseName: '', credits: 3 });
    }
  };

  const removeCourse = (semesterId, courseId) => {
    const updatedSemesters = semesters.map(semester => {
      if (semester.id === semesterId) {
        return {
          ...semester,
          courses: semester.courses.filter(c => c.id !== courseId)
        };
      }
      return semester;
    });
    setSemesters(updatedSemesters);
  };

  const calculateSemesterCredits = (courses) => {
    return courses.reduce((total, course) => total + (course.credits || 0), 0);
  };

  const getTotalCredits = () => {
    return semesters.reduce((total, semester) => 
      total + calculateSemesterCredits(semester.courses), 0
    );
  };

  return (
    <div className="course-planner">
      <div className="planner-header">
        <h2>Course Planner</h2>
        <div className="planner-stats">
          <div className="stat-card">
            <span className="stat-label">Total Semesters</span>
            <span className="stat-value">{semesters.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Credits</span>
            <span className="stat-value">{getTotalCredits()}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Avg Credits/Semester</span>
            <span className="stat-value">
              {semesters.length > 0 ? Math.round(getTotalCredits() / semesters.length) : 0}
            </span>
          </div>
        </div>
      </div>

      <div className="semesters-grid">
        {semesters.map(semester => {
          const semesterCredits = calculateSemesterCredits(semester.courses);
          const isOverloaded = semesterCredits > (studentProfile.creditHoursPerSemester || 15);
          const isUnderloaded = semesterCredits < 12 && semester.courses.length > 0;

          return (
            <div
              key={semester.id}
              className={`semester-card ${isOverloaded ? 'overloaded' : ''} ${isUnderloaded ? 'underloaded' : ''}`}
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(semester.id)}
            >
              <div className="semester-header">
                <h3>{semester.name}</h3>
                <div className="semester-actions">
                  <button
                    className="btn-icon"
                    onClick={() => openAddCourseModal(semester.id)}
                    title="Add course"
                  >
                    +
                  </button>
                  {semesters.length > 1 && (
                    <button
                      className="btn-icon btn-danger"
                      onClick={() => removeSemester(semester.id)}
                      title="Remove semester"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>

              <div className="semester-credits">
                <span>{semesterCredits} credits</span>
                {isOverloaded && <span className="warning">⚠️ Overloaded</span>}
                {isUnderloaded && <span className="warning">⚠️ Below minimum</span>}
              </div>

              <div className="courses-list">
                {semester.courses.length === 0 ? (
                  <div className="empty-semester">
                    <p>Drop courses here or click + to add</p>
                  </div>
                ) : (
                  semester.courses.map(course => (
                    <div
                      key={course.id}
                      className="course-card"
                      draggable
                      onDragStart={() => handleDragStart(course, semester.id)}
                    >
                      <div className="course-info">
                        <strong>{course.courseCode}</strong>
                        <p>{course.courseName}</p>
                      </div>
                      <div className="course-meta">
                        <span className="credits-badge">{course.credits} cr</span>
                        <button
                          className="btn-remove"
                          onClick={() => removeCourse(semester.id, course.id)}
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}

        <div className="add-semester-card" onClick={addSemester}>
          <div className="add-semester-content">
            <span className="add-icon">+</span>
            <p>Add Semester</p>
          </div>
        </div>
      </div>

      {showAddCourseModal && (
        <div className="modal-overlay" onClick={() => setShowAddCourseModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add Course</h3>
            <div className="form-group">
              <label>Course Code</label>
              <input
                type="text"
                value={newCourseData.courseCode}
                onChange={(e) => setNewCourseData({ ...newCourseData, courseCode: e.target.value })}
                placeholder="e.g., CS101"
              />
            </div>
            <div className="form-group">
              <label>Course Name</label>
              <input
                type="text"
                value={newCourseData.courseName}
                onChange={(e) => setNewCourseData({ ...newCourseData, courseName: e.target.value })}
                placeholder="e.g., Introduction to Computer Science"
              />
            </div>
            <div className="form-group">
              <label>Credits</label>
              <input
                type="number"
                min="1"
                max="6"
                value={newCourseData.credits}
                onChange={(e) => setNewCourseData({ ...newCourseData, credits: parseInt(e.target.value) })}
              />
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowAddCourseModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleAddCourse}>
                Add Course
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoursePlanner;