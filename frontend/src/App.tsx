import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'
import { ToastContainer, toast } from 'react-toastify'
import Login from './components/Login'
import RepoList from './components/RepoList'
import Form from './components/Form'
import './App.css'
import './components.css'
import 'react-toastify/dist/ReactToastify.css'

function App() {
  const [selectedRepos, setSelectedRepos] = useState<number[]>([]);
  const [jobId, setJobId] = useState<number | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await axios.get('/api/csrf/');
      } catch (error) {
        console.error('Failed to fetch CSRF token', error);
      }

      try {
        await axios.get('/api/repos/');
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
        toast.error('Please log in with GitHub before continuing.');
      }
    };

    bootstrap();
  }, []);

  const handleFormSubmit = async (data: {
    sourceBranch: string;
    destBranch: string;
    prTitle: string;
    prBody: string;
  }) => {
    try {
      const response = await axios.post('/api/jobs/', {
        repos: selectedRepos,
        source_branch: data.sourceBranch,
        dest_branch: data.destBranch,
        pr_title: data.prTitle,
        pr_body: data.prBody,
      });
      setJobId(response.data.job_id);
      toast.success('Job submitted successfully.');
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? error.response?.data?.error || error.message
        : 'Failed to create job';
      toast.error(message);
      console.error('Failed to create job', error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout/');
      setIsAuthenticated(false);
      toast.success('Logged out successfully.');
    } catch (error) {
      // Even if logout fails server-side, force client-side logout for security
      setIsAuthenticated(false);
      const message = axios.isAxiosError(error)
        ? error.response?.data?.error || error.message
        : 'Logout completed (with server error)';
      toast.error(message);
      console.error('Failed to logout server-side', error);
    }
  };

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div className="app">
        <h1>Pull Request Helper</h1>
        <Routes>
          <Route path="/" element={
            isAuthenticated ? (
              <Navigate to="/repos" replace />
            ) : (
              <Login />
            )
          } />
           <Route path="/repos" element={
             isAuthenticated ? (
               <div>
                 <div className="logout-container">
                   <button onClick={handleLogout} className="logout-button">
                     Logout
                   </button>
                 </div>
                 <RepoList selectedRepos={selectedRepos} setSelectedRepos={setSelectedRepos} />
                 <Form selectedRepos={selectedRepos} onSubmit={handleFormSubmit} />
                 {jobId && <p>Job submitted: {jobId}</p>}
               </div>
             ) : <Navigate to="/" replace />
           } />
        </Routes>
        <ToastContainer position="bottom-right" newestOnTop closeOnClick pauseOnFocusLoss={false} />
      </div>
    </Router>
  )
}

export default App
