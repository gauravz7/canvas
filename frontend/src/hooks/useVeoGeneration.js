import { useState } from 'react';

export const useVeoGeneration = (userId, config) => {
  const [activeMode, setActiveMode] = useState('standard'); // standard, extension, subject
  const [modelId, setModelId] = useState(config?.DEFAULT_VEO_MODEL || 'veo-3.1-generate-preview');
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');

  // Params
  const [duration, setDuration] = useState(8);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [resolution, setResolution] = useState('720p');
  const [generateAudio, setGenerateAudio] = useState(false);

  // Status
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const generateVideo = async (mediaState) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('model_id', modelId);
    formData.append('duration_seconds', duration);
    formData.append('aspect_ratio', aspectRatio);
    formData.append('resolution', resolution);
    formData.append('generate_audio', generateAudio);
    if (negativePrompt) formData.append('negative_prompt', negativePrompt);
    formData.append('user_id', userId);

    const {
      firstFrameFile, firstFrameUri,
      lastFrameFile, lastFrameUri,
      videoFile, videoUri,
      referenceFiles, referenceUris
    } = mediaState;

    if (activeMode === 'standard') {
      if (firstFrameFile) formData.append('first_frame_file', firstFrameFile);
      if (firstFrameUri) formData.append('first_frame_uri', firstFrameUri);
      if (lastFrameFile) formData.append('last_frame_file', lastFrameFile);
      if (lastFrameUri) formData.append('last_frame_uri', lastFrameUri);
    } else if (activeMode === 'extension') {
      if (videoFile) formData.append('video_file', videoFile);
      if (videoUri) formData.append('video_uri', videoUri);
    } else if (activeMode === 'subject') {
      referenceFiles.forEach(file => formData.append('reference_files', file));
      if (referenceUris) formData.append('reference_uris', referenceUris);
    }

    try {
      const response = await fetch('/api/generate/video', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    state: {
      activeMode, setActiveMode,
      modelId, setModelId,
      prompt, setPrompt,
      negativePrompt, setNegativePrompt,
      duration, setDuration,
      aspectRatio, setAspectRatio,
      resolution, setResolution,
      generateAudio, setGenerateAudio,
      isLoading,
      result,
      error
    },
    generateVideo
  };
};
