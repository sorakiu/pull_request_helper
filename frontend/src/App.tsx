import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import axios from 'axios'
import Login from './components/Login'
import RepoList from './components/RepoList'
import Form from './components/Form'
import './App.css'

function App() {
  const [selectedRepos, setSelectedRepos] = useState<number[]>([]);
  const [jobId, setJobId] = useState<number | null>(null);

  const handleFormSubmit = async (data: {
    sourceBranch: string;
    destBranch: string;
    prTitle: string;
    prBody: string;
  }) => {
    try {
      const response = await axios.post('/api/jobs/', {
        repos: selectedRepos,
        ...data,
      });
      setJobId(response.data.job_id);
    } catch (error) {
      console.error('Failed to create job', error);
    }
  };

  return (
    <Router>
      <div className="app">
        <h1>Pull Request Helper</h1>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/repos" element={
            <div>
              <RepoList selectedRepos={selectedRepos} setSelectedRepos={setSelectedRepos} />
              <Form selectedRepos={selectedRepos} onSubmit={handleFormSubmit} />
              {jobId && <p>Job submitted: {jobId}</p>}
            </div>
          } />
        </Routes>
      </div>
    </Router>
  )
}

export default App
