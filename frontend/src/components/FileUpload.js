// src/components/FileUpload.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import '../App.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    console.log("Form submitted with file:", file);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData);
      console.log("File uploaded successfully:", response.data);
      navigate('/result', { state: { data: response.data } });
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="file-upload">
      <h2>Business Contract Validation</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,.txt" />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default FileUpload;
