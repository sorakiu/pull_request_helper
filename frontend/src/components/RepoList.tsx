import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Repo {
  id: number;
  name: string;
  owner: string;
}

interface RepoListProps {
  selectedRepos: number[];
  setSelectedRepos: React.Dispatch<React.SetStateAction<number[]>>;
}

const RepoList: React.FC<RepoListProps> = ({ selectedRepos, setSelectedRepos }) => {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const response = await axios.get('/api/repos/');
        setRepos(response.data);
      } catch (error) {
        setError('Failed to load repositories. Please check your login.');
        console.error('Failed to fetch repos', error);
      } finally {
        setLoading(false);
      }
    };
    fetchRepos();
  }, []);

  const handleCheckboxChange = (repoId: number) => {
    setSelectedRepos(prev =>
      prev.includes(repoId) ? prev.filter(id => id !== repoId) : [...prev, repoId]
    );
  };

  if (loading) return <p>Loading repositories...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div className="repo-list">
      <h2>Select Repositories</h2>
      {repos.map(repo => (
        <div key={repo.id}>
          <label>
            <input
              type="checkbox"
              checked={selectedRepos.includes(repo.id)}
              onChange={() => handleCheckboxChange(repo.id)}
            />
            {repo.owner}/{repo.name}
          </label>
        </div>
      ))}
      <p>Selected: {selectedRepos.length} repositories</p>
    </div>
  );
};

export default RepoList;