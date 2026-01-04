import React from 'react';

const Login: React.FC = () => {
  const handleLogin = () => {
    window.location.href = '/api/auth/github/login/';
  };

  return (
    <div className="login">
      <h2>Login with GitHub</h2>
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default Login;