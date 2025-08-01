import React from 'react';

const ScoreTag = ({ score }) => {
  if (score === null || score === undefined) {
    return (
      <span className="badge badge-primary">
        Pending
      </span>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'badge-success';
    if (score >= 60) return 'badge-warning';
    return 'badge-danger';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    return 'Poor Match';
  };

  return (
    <div className="flex items-center space-x-2">
      <span className={`badge ${getScoreColor(score)}`}>
        {score}% Match
      </span>
      <span className="text-xs text-gray-500">
        {getScoreLabel(score)}
      </span>
    </div>
  );
};

export default ScoreTag;
