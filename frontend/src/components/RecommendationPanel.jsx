import React, { useState } from 'react';
import './RecommendationPanel.css';

const RecommendationPanel = ({ recommendations, onAddToPlan }) => {
  const [expandedCard, setExpandedCard] = useState(null);

  const priorityColors = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981'
  };

  const priorityLabels = {
    high: '🔴 High Priority',
    medium: '🟡 Medium Priority',
    low: '🟢 Low Priority'
  };

  const toggleCard = (id) => {
    setExpandedCard(expandedCard === id ? null : id);
  };

  if (recommendations.length === 0) {
    return (
      <div className="recommendation-panel">
        <div className="empty-recommendations">
          <div className="empty-icon">🤖</div>
          <h3>No Recommendations Yet</h3>
          <p>Complete your student profile to get personalized course recommendations from our AI agent.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendation-panel">
      <div className="panel-header">
        <h2>AI-Powered Course Recommendations</h2>
        <p className="subtitle">Based on your profile, interests, and career goals</p>
      </div>

      <div className="recommendations-grid">
        {recommendations.map(rec => (
          <div
            key={rec.id}
            className={`recommendation-card ${expandedCard === rec.id ? 'expanded' : ''}`}
          >
            <div className="card-header">
              <div className="course-title">
                <h3>{rec.courseCode}</h3>
                <p>{rec.courseName}</p>
              </div>
              <div
                className="priority-badge"
                style={{ backgroundColor: priorityColors[rec.priority] }}
              >
                {priorityLabels[rec.priority]}
              </div>
            </div>

            <div className="card-body">
              <div className="course-details">
                <div className="detail-item">
                  <span className="label">Credits:</span>
                  <span className="value">{rec.credits}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Recommended Semester:</span>
                  <span className="value">{rec.semester}</span>
                </div>
              </div>

              <div className="ai-reasoning">
                <h4>🤖 AI Reasoning</h4>
                <p>{rec.reason}</p>
              </div>

              {expandedCard === rec.id && (
                <div className="expanded-content">
                  <div className="prerequisites">
                    <h4>Prerequisites</h4>
                    <p>{rec.prerequisites || 'None'}</p>
                  </div>
                  <div className="learning-outcomes">
                    <h4>What You'll Learn</h4>
                    <ul>
                      <li>Core concepts and fundamentals</li>
                      <li>Practical applications and projects</li>
                      <li>Industry-relevant skills</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            <div className="card-actions">
              <button
                className="btn-secondary"
                onClick={() => toggleCard(rec.id)}
              >
                {expandedCard === rec.id ? 'Show Less' : 'Show More'}
              </button>
              <button
                className="btn-primary"
                onClick={() => onAddToPlan(rec)}
              >
                ➕ Add to Plan
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="recommendation-footer">
        <div className="info-box">
          <h4>💡 Pro Tips</h4>
          <ul>
            <li>High priority courses are essential for your degree progression</li>
            <li>Consider workload balance when selecting courses</li>
            <li>Check prerequisites before adding courses to your plan</li>
            <li>Consult with your academic advisor for final approval</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RecommendationPanel;