import React, { useState, useMemo, useRef, useEffect } from 'react';
import './CoursePlanner.css';
import Icon from './Icon';

const prereqCodes = (course) => {
  const str = course.prerequisites;
  if (!str || str === 'None') return [];
  return str.match(/[A-Z]{2,4}\d{3}/g) || [];
};

const CoursePlanner = ({
  semesters,
  setSemesters,
  studentProfile,
  onGeneratePlan,
  onSavePlan,
  savedPlanId,
  planLoading,
  planError,
  planSource,
  profileComplete,
}) => {
  const [draggedCourse, setDraggedCourse] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedSemester, setSelectedSemester] = useState(null);
  const [newCourse, setNewCourse] = useState({ courseCode: '', courseName: '', credits: 3 });
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (showModal && !dialog.open) dialog.showModal();
    if (!showModal && dialog.open) dialog.close();
  }, [showModal]);

  const handleDragStart = (e, course, semId) => {
    e.dataTransfer.setData('text/plain', String(course.id));
    e.dataTransfer.effectAllowed = 'move';
    setDraggedCourse({ course, semId });
  };
  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (targetId) => {
    if (!draggedCourse) return;
    if (draggedCourse.semId === targetId) {
      setDraggedCourse(null);
      return;
    }
    setSemesters((prev) => {
      const source = prev.find((s) => s.id === draggedCourse.semId);
      const course = source && source.courses.find((c) => c.id === draggedCourse.course.id);
      if (!course || !prev.some((s) => s.id === targetId)) return prev;
      return prev.map((s) => {
        if (s.id === draggedCourse.semId)
          return { ...s, courses: s.courses.filter((c) => c.id !== course.id) };
        if (s.id === targetId)
          return { ...s, courses: [...s.courses, course] };
        return s;
      });
    });
    setDraggedCourse(null);
  };

  const addSemester = () => {
    const id = Math.max(0, ...semesters.map((s) => s.id)) + 1;
    setSemesters([...semesters, { id, name: `Semester ${id}`, courses: [] }]);
  };

  const removeSemester = (id) => {
    if (semesters.length > 1) setSemesters(semesters.filter((s) => s.id !== id));
  };

  const openModal = (id) => { setSelectedSemester(id); setShowModal(true); };

  const handleAddCourse = () => {
    if (!newCourse.courseCode || !newCourse.courseName) return;
    setSemesters((prev) =>
      prev.map((s) =>
        s.id === selectedSemester
          ? { ...s, courses: [...s.courses, { id: Date.now(), ...newCourse }] }
          : s
      )
    );
    setShowModal(false);
    setNewCourse({ courseCode: '', courseName: '', credits: 3 });
  };

  const removeCourse = (semId, courseId) => {
    setSemesters((prev) =>
      prev.map((s) =>
        s.id === semId ? { ...s, courses: s.courses.filter((c) => c.id !== courseId) } : s
      )
    );
  };

  const semCredits = (courses) => courses.reduce((t, c) => t + (c.credits || 0), 0);
  const totalCredits = semesters.reduce((t, s) => t + semCredits(s.courses), 0);
  const totalCourses = semesters.reduce((t, s) => t + s.courses.length, 0);
  const max = studentProfile.creditHoursPerSemester || 15;

  const missingPrereqs = useMemo(() => {
    const satisfied = new Set(studentProfile.completedCourses || []);
    const map = {};
    semesters.forEach((sem) => {
      sem.courses.forEach((c) => {
        const missing = prereqCodes(c).filter((p) => !satisfied.has(p));
        if (missing.length > 0) map[c.id] = missing;
      });
      sem.courses.forEach((c) => {
        if (c.courseCode) satisfied.add(c.courseCode);
      });
    });
    return map;
  }, [semesters, studentProfile.completedCourses]);
  const conflictCount = Object.keys(missingPrereqs).length;

  return (
    <div className="course-planner">
      <div className="planner-header">
        <h2>Semester Planner</h2>
        <div className="planner-generate">
          <button
            type="button"
            className="btn-primary"
            onClick={onGeneratePlan}
            disabled={planLoading || !profileComplete}
          >
            {planLoading ? 'Generating…' : 'Generate Plan'}
          </button>
          <button type="button" className="btn-secondary" onClick={onSavePlan} disabled={totalCourses === 0}>
            Save Plan
          </button>
          {!profileComplete && (
            <span className="plan-hint">Complete your profile to generate a plan</span>
          )}
          {savedPlanId && (
            <span className="plan-hint">
              Saved. Share it with <a href={`?plan=${savedPlanId}`}>this link</a>
            </span>
          )}
          {planSource && (
            <span className="plan-source-badge">
              {planSource === 'ai' ? 'AI-generated plan' : 'Rule-based plan'}
            </span>
          )}
          {conflictCount > 0 && (
            <span className="warning">
              <Icon name="alert" size={14} />
              {conflictCount} prerequisite conflict{conflictCount > 1 ? 's' : ''}
            </span>
          )}
          {planError && (
            <span className="warning" role="alert">
              <Icon name="alert" size={14} />
              {planError}
            </span>
          )}
        </div>
        <div className="planner-stats">
          <div className="stat-card">
            <span className="stat-label">Semesters</span>
            <span className="stat-value">{semesters.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Credits</span>
            <span className="stat-value">{totalCredits}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Courses</span>
            <span className="stat-value">{totalCourses}</span>
          </div>
        </div>
      </div>

      <div className="semesters-grid">
        {semesters.map((sem) => {
          const credits = semCredits(sem.courses);
          const over = credits > max;
          const under = credits > 0 && credits < 12;
          return (
            <div
              key={sem.id}
              className={`semester-column ${over ? 'overloaded' : ''} ${under ? 'underloaded' : ''}`}
              onDragOver={handleDragOver}
              onDrop={(e) => {
                e.preventDefault();
                handleDrop(sem.id);
              }}
            >
              <div className="semester-header">
                <h3>{sem.name}</h3>
                <div className="semester-actions">
                  <button
                    type="button"
                    onClick={() => openModal(sem.id)}
                    title="Add course"
                    aria-label={`Add a course to ${sem.name}`}
                  >
                    <Icon name="plus" />
                  </button>
                  {semesters.length > 1 && (
                    <button
                      type="button"
                      className="btn-danger"
                      onClick={() => removeSemester(sem.id)}
                      title="Remove"
                      aria-label={`Remove ${sem.name}`}
                    >
                      <Icon name="close" />
                    </button>
                  )}
                </div>
              </div>
              <div className="semester-credits">
                {credits} / {max} credits
                {over && (
                  <span className="warning">
                    <Icon name="alert" size={14} />
                    Over limit
                  </span>
                )}
                {under && (
                  <span className="warning">
                    <Icon name="alert" size={14} />
                    Below 12
                  </span>
                )}
              </div>
              <div className="courses-list">
                {sem.courses.length === 0 ? (
                  <div className="empty-semester">Drop courses here or click +</div>
                ) : (
                  sem.courses.map((c) => (
                    <div
                      key={c.id}
                      className={`course-card ${missingPrereqs[c.id] ? 'prereq-conflict' : ''}`}
                      draggable
                      onDragStart={(e) => handleDragStart(e, c, sem.id)}
                    >
                      <div className="course-info">
                        <strong>{c.courseCode}</strong>
                        <p>{c.courseName}</p>
                        {missingPrereqs[c.id] && (
                          <span className="prereq-warning">
                            <Icon name="alert" size={12} />
                            needs {missingPrereqs[c.id].join(', ')}
                          </span>
                        )}
                      </div>
                      <div className="course-meta">
                        <span className="credits-badge">{c.credits} cr</span>
                        <button
                          type="button"
                          className="btn-remove"
                          aria-label={`Remove ${c.courseCode} from ${sem.name}`}
                          onClick={() => removeCourse(sem.id, c.id)}
                        >
                          <Icon name="close" size={14} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
        <button type="button" className="add-semester-card" onClick={addSemester}>
          <span className="add-semester-content">
            <span className="add-icon"><Icon name="plus" size={24} /></span>
            <span>Add Semester</span>
          </span>
        </button>
      </div>

      <dialog
        ref={dialogRef}
        className="modal"
        aria-labelledby="add-course-title"
        onClose={() => setShowModal(false)}
        onClick={(e) => {
          if (e.target === dialogRef.current) setShowModal(false);
        }}
      >
        <div className="modal-content">
          <h3 id="add-course-title">Add Course</h3>
          <div className="form-group">
            <label htmlFor="new-course-code">Course Code</label>
            <input
              id="new-course-code"
              value={newCourse.courseCode}
              onChange={(e) => setNewCourse({ ...newCourse, courseCode: e.target.value })}
              placeholder="e.g. CS101"
            />
          </div>
          <div className="form-group">
            <label htmlFor="new-course-name">Course Name</label>
            <input
              id="new-course-name"
              value={newCourse.courseName}
              onChange={(e) => setNewCourse({ ...newCourse, courseName: e.target.value })}
              placeholder="e.g. Intro to CS"
            />
          </div>
          <div className="form-group">
            <label htmlFor="new-course-credits">Credits</label>
            <input
              id="new-course-credits"
              type="number" min="1" max="6"
              value={newCourse.credits}
              onChange={(e) => setNewCourse({ ...newCourse, credits: parseInt(e.target.value) || 3 })}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
            <button type="button" className="btn-primary" onClick={handleAddCourse}>Add</button>
          </div>
        </div>
      </dialog>
    </div>
  );
};

export default CoursePlanner;
