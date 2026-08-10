import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Feed } from './pages/Feed';
import { Profile } from './pages/Profile';
import { PostDetail } from './pages/PostDetail';
import { EditProfile } from './pages/EditProfile';
import { Network } from './pages/Network';
import { Jobs } from './pages/Jobs';
import { Messages } from './pages/Messages';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<ProtectedRoute><Layout><Feed /></Layout></ProtectedRoute>} />
          <Route path="/videos" element={<ProtectedRoute><Layout><Feed filter="videos" /></Layout></ProtectedRoute>} />
          <Route path="/network" element={<ProtectedRoute><Layout><Network /></Layout></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><Layout><Jobs /></Layout></ProtectedRoute>} />
          <Route path="/messages" element={<ProtectedRoute><Layout><Messages /></Layout></ProtectedRoute>} />
          <Route path="/profile/:id" element={<ProtectedRoute><Layout><Profile /></Layout></ProtectedRoute>} />
          <Route path="/post/:id" element={<Layout><PostDetail /></Layout>} />
          <Route path="/edit-profile" element={<ProtectedRoute><Layout><EditProfile /></Layout></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
