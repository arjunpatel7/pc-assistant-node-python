'use client'

import { useState, useEffect } from 'react';

interface File {
  id: string;
  name: string;
  size: number;
  created_at: string;
}

export default function AssistantFiles() {
  const [files, setFiles] = useState<File[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await fetch('/api/list_assistant_files');
      const data = await response.json();
      if (data.status === 'success') {
        setFiles(data.files);
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('Error fetching assistant files');
    }
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Byte';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)).toString());
    return Math.round(bytes / Math.pow(1024, i)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-2xl mt-4 bg-white shadow-md rounded-lg overflow-hidden">
      <button
        className="w-full flex justify-between items-center p-4 bg-gray-100 hover:bg-gray-200 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-semibold">Assistant Files</span>
        <span className="text-xl">{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && (
        <div className="p-4">
          {error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <div className="flex flex-wrap -mx-2">
              {files.map((file) => (
                <div key={file.id} className="w-full sm:w-1/2 md:w-1/3 px-2 mb-4">
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <h3 className="font-semibold truncate">{file.name}</h3>
                    <p className="text-sm text-gray-600">Size: {formatFileSize(file.size)}</p>
                    <p className="text-sm text-gray-600">
                      Created: {new Date(file.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}