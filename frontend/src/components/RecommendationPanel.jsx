import React, { useState } from 'react';
import './RecommendationPanel.css';

const RecommendationPanel = ({ recommendations, onAddToPlan }) => {
  const [expandedCard, setExpandedCard] = useState(null);

  if (recommendations.length === 0) {
    return (
      <div className="recommendation-panel">
        <div className="empty-recommendations">
          <div className="empty-icon">◈</div>
          <h3>No Recommendations Yet</h3>
          <p>Complete your student profile and click "Get AI Recommendations" to see personalized course suggestions.</p>
        </div>
      </div>
    );
  }

  const highCount = recommendations.filter((r) => r.priority === 'high').length;
  const totalCredits = recommendations.reduce((s, r) => s + r.credits, 0);

  return (
    <div className="recommendation-panel">
      <div className="panel-header">
        <h2>Recommended Courses</h2>
        <p className="subtitle">
          {recommendations.length} courses · {totalCredits} credits · {highCount} high priority
        </p>
        <div className="ai-badge">◈ AI-Generated</div>
      </div>

      <div className="recommendations-grid">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className={`recommendation-card ${expandedCard === rec.id ? 'expanded' : ''}`}
          >
            <div className="card-header">
              <div className="course-title">
                <h3>{rec.courseCode}</h3>
                <p>{rec.courseName}</p>
              </div>
              <span className={`priority-badge priority-${rec.priority}`}>
                {rec.priority}
              </span>
            </div>

            <div className="course-meta-row">
              <div className="meta-item">
                Credits: <span className="value">{rec.credits}</span>
              </div>
              <div className="meta-item">
                Semester: <span className="value">{rec.semester}</span>
              </div>
              {rec.prerequisites && rec.prerequisites !== 'None' && (
                <div className="meta-item">
                  Prereqs: <span className="value">{rec.prerequisites}</span>
                </div>
              )}
            </div>

            <div className="ai-reasoning">
              <h4>Why this course</h4>
              <p>{rec.reason}</p>
            </div>

            {expandedCard === rec.id && (
              <div className="expanded-content">
                <div className="detail-row">
                  <div>
                    <h4>Description</h4>
                    <p>{rec.description || 'No description available.'}</p>
                  </div>
                  <div>
                    <h4>Level</h4>
                    <p>
                      {rec.level === 1 && 'Foundation'}
                      {rec.level === 2 && 'Intermediate'}
                      {rec.level === 3 && 'Advanced'}
                      {rec.level === 4 && 'Specialization'}
                      {!rec.level && 'N/A'}
                      {rec.major && ` · ${rec.major}`}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="card-actions">
              <button className="btn-ghost" onClick={() => setExpandedCard(expandedCard === rec.id ? null : rec.id)}>
                {expandedCard === rec.id ? 'Less' : 'More'}
              </button>
              <button className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }} onClick={() => onAddToPlan(rec)}>
                + Add to Plan
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationPanel;
