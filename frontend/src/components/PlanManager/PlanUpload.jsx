import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText } from 'lucide-react';

export function PlanUpload({ onUpload }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  return (
    <div className="plan-upload-section">
      <h3>Upload Your Own Plan</h3>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="dropzone-icon" />
        {isDragActive ? (
          <p className="dropzone-text">Drop your file here...</p>
        ) : (
          <>
            <p className="dropzone-text">
              Drag & drop your workout plan here
            </p>
            <p className="dropzone-subtext">or</p>
            <button type="button" className="browse-button">
              Browse Files
            </button>
          </>
        )}
      </div>
      <div className="upload-note">
        <FileText className="w-4 h-4" />
        <p>
          <strong>Supported formats:</strong> Excel (.xlsx, .xls), CSV (.csv)
          <br />
          <em>Note: File parsing coming soon - UI only for now</em>
        </p>
      </div>
    </div>
  );
}
