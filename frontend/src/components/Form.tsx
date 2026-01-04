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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!destBranch) return;
    const title = prTitle || `${sourceBranch} -> ${destBranch}`;
    onSubmit({ sourceBranch, destBranch, prTitle: title, prBody });
  };

  return (
    <form onSubmit={handleSubmit} className="pr-form">
      <h2>Configure Pull Request</h2>
      <label>
        Source Branch:
        <input
          type="text"
          value={sourceBranch}
          onChange={(e) => setSourceBranch(e.target.value)}
        />
      </label>
      <label>
        Destination Branch:
        <input
          type="text"
          value={destBranch}
          onChange={(e) => setDestBranch(e.target.value)}
          required
        />
      </label>
      <label>
        PR Title:
        <input
          type="text"
          value={prTitle}
          onChange={(e) => setPrTitle(e.target.value)}
          placeholder={`${sourceBranch} -> ${destBranch}`}
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
      <button type="submit" disabled={selectedRepos.length === 0}>
        Create PRs for {selectedRepos.length} repos
      </button>
    </form>
  );
};

export default Form;