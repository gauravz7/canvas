import React from 'react';
import { Upload, Trash2, Globe, Link as LinkIcon } from 'lucide-react';

const MediaInput = ({ label, file, setFile, uri, setUri, inputRef, type = 'image', maxFiles = 1, files, setFiles }) => {
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      if (maxFiles > 1) {
        setFiles(Array.from(e.target.files));
      } else {
        setFile(e.target.files[0]);
      }
    }
  };

  const handleClear = () => {
    if (maxFiles > 1) {
      setFiles([]);
    } else {
      setFile(null);
    }
    if (setUri) setUri('');
    if (inputRef.current) inputRef.current.value = '';
  };

  const hasContent = (maxFiles > 1 ? (files && files.length > 0) : file) || uri;

  return (
    <div className="config-group" style={{ marginBottom: '1.5rem' }}>
      <label className="label">{label}</label>
      <div className="media-input-container">
        <div
          className={`upload-box ${hasContent ? 'has-content' : ''}`}
          onClick={() => inputRef.current?.click()}
          style={{ borderColor: hasContent ? 'var(--input-focus-ring-color)' : '' }}
        >
          <input
            type="file"
            ref={inputRef}
            onChange={handleFileChange}
            accept={type === 'video' ? "video/mp4,video/quicktime,video/webm" : "image/*"}
            multiple={maxFiles > 1}
            style={{ display: 'none' }}
          />

          {!hasContent ? (
            <div className="upload-placeholder">
              <Upload size={20} className="icon" />
              <span>Click to Upload {maxFiles > 1 ? 'Images' : (type === 'video' ? 'Video' : 'Image')}</span>
            </div>
          ) : (
            <div className="file-info">
              {maxFiles > 1 ? (
                <span>{files.length} file(s) selected</span>
              ) : (
                <>
                  {file ? (
                    <span>{file.name}</span>
                  ) : (
                    <span className="uri-text">
                      <Globe size={14} style={{ display: 'inline', marginRight: 4 }} />
                      {uri.split('/').pop() || 'GCS URI'}
                    </span>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {setUri && (
          <div className="uri-input-group">
            <LinkIcon size={16} className="uri-icon" />
            <input
              type="text"
              placeholder="gs://bucket/path/to/file"
              value={uri}
              onChange={(e) => setUri(e.target.value)}
              className="input-field uri-input"
            />
          </div>
        )}

        {hasContent && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            className="clear-button"
            title="Clear"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </div>
  );
};

export default MediaInput;
