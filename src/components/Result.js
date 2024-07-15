// src/components/Result.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import '../App.css';

const Result = () => {
  const location = useLocation();
  const { state } = location;
  const { data } = state || {};

  console.log("Result page data:", data);

  if (!data) {
    return <p>No data available.</p>;
  }

  return (
    <div className="result-page">
      <h2>Analysis Result</h2>
      <section>
        <h3>Original Document</h3>
        <iframe src={`data:application/pdf;base64,${data.originalDocument}`} />
      </section>
      <section>
        <h3>Highlighted Document</h3>
        <iframe src={`data:application/pdf;base64,${data.highlightedDocument}`} />
      </section>
      <section>
        <h3>Detected Entities</h3>
        <ul>
          {data.entities.map((entity, index) => (
            <li key={index}>{entity.name}: {entity.score}</li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default Result;
