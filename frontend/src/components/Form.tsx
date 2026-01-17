import React, { useState } from 'react';

interface FormProps {
  selectedRepos: number[];
  onSubmit: (data: {
    sourceBranch: string;
    destBranch: string;
    prTitle: string;
    prBody: string;
  }) => void;
}

const Form: React.FC<FormProps> = ({ selectedRepos, onSubmit }) => {
  const [sourceBranch, setSourceBranch] = useState('main');
  const [destBranch, setDestBranch] = useState('');
  const [prTitle, setPrTitle] = useState('');
  const [prBody, setPrBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  // Validate form fields
  const validateForm = (): boolean => {
    const newErrors: {[key: string]: string} = {};

    if (!sourceBranch.trim()) {
      newErrors.sourceBranch = 'Source branch is required';
    } else if (!/^[a-zA-Z0-9._/-]+$/.test(sourceBranch.trim())) {
      newErrors.sourceBranch = 'Branch name contains invalid characters';
    }

    if (!destBranch.trim()) {
      newErrors.destBranch = 'Destination branch is required';
    } else if (!/^[a-zA-Z0-9._/-]+$/.test(destBranch.trim())) {
      newErrors.destBranch = 'Branch name contains invalid characters';
    }

    if (sourceBranch.trim() === destBranch.trim()) {
      newErrors.destBranch = 'Source and destination branches must be different';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      // Use custom title if provided, otherwise generate one
      const title = prTitle.trim() || `${sourceBranch.trim()} -> ${destBranch.trim()}`;
      await onSubmit({ sourceBranch: sourceBranch.trim(), destBranch: destBranch.trim(), prTitle: title, prBody: prBody.trim() });
    } finally {
      setSubmitting(false);
    }
  };

  // Clear specific field error when user starts typing
  const clearFieldError = (field: string) => {
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="pr-form">
      <h2>Configure Pull Request</h2>
       <label>
         Source Branch:
         <input
           type="text"
           value={sourceBranch}
           onChange={(e) => {
             setSourceBranch(e.target.value);
             clearFieldError('sourceBranch');
           }}
           className={errors.sourceBranch ? 'error' : ''}
         />
         {errors.sourceBranch && <span className="error-message">{errors.sourceBranch}</span>}
       </label>
       <label>
         Destination Branch:
         <input
           type="text"
           value={destBranch}
           onChange={(e) => {
             setDestBranch(e.target.value);
             clearFieldError('destBranch');
           }}
           className={errors.destBranch ? 'error' : ''}
           required
         />
         {errors.destBranch && <span className="error-message">{errors.destBranch}</span>}
       </label>
       <label>
         PR Title:
         <input
           type="text"
           value={prTitle}
           onChange={(e) => setPrTitle(e.target.value)}
           placeholder={sourceBranch && destBranch ? `${sourceBranch} -> ${destBranch}` : 'Enter PR title'}
         />
       </label>
      <label>
        PR Body:
        <textarea
          value={prBody}
          onChange={(e) => setPrBody(e.target.value)}
          placeholder="Optional description"
        />
      </label>
      <button type="submit" disabled={selectedRepos.length === 0 || submitting}>
        {submitting ? 'Creating...' : `Create PRs for ${selectedRepos.length} repos`}
      </button>
    </form>
  );
};

export default Form;