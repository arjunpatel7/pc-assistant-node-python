'use client'

import { useState, useEffect } from 'react';

interface File {
  id: string;
  name: string;
  size: number;
  created_at: string;
}
interface Reference {
  name: string;
  url: string;
}

interface AssistantFilesProps {
  referencedFiles: Reference[];
}

export default function AssistantFiles({ referencedFiles }: AssistantFilesProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isOpen, setIsOpen] = useState(true);
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

  const isReferenced = (file: File) => {
    return referencedFiles.some(ref => ref.name === file.name);
  };

  return (
    <div className="w-full mt-4 bg-white shadow-md rounded-lg overflow-hidden">
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
                <div
                  key={file.id}
                  className="w-full sm:w-1/2 md:w-1/3 px-2 mb-4 relative"
                >
                  <div className={`bg-gray-100 p-4 rounded-lg ${isReferenced(file) ? 'border border-blue-500' : ''}`}>
                    <h3 className="font-semibold truncate">{file.name}</h3>
                    <p className="text-sm text-gray-600">Size: {formatFileSize(file.size)}</p>
                    <p className="text-sm text-gray-600">
                      Created: {new Date(file.created_at).toLocaleDateString()}
                    </p>
                    {isReferenced(file) && (
                      <span className="absolute bottom-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">Referenced</span>
                    )}
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