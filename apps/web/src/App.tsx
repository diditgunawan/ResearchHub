import { useState, useEffect } from 'react';
import { api, User, Project } from './api/client';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { SearchPage } from './pages/SearchPage';
import { LibraryPage } from './pages/LibraryPage';
import { ScreeningPage } from './pages/ScreeningPage';
import { SynthesisPage } from './pages/SynthesisPage';
import { LineagePage } from './pages/LineagePage';
import { JournalsPage } from './pages/JournalsPage';

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  const loadUserData = async () => {
    try {
      const me = await api.getMe();
      setUser(me);
      const projList = await api.getProjects();
      setProjects(projList);
      if (projList.length > 0) {
        setActiveProject(projList[0]);
      }
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserData();
  }, []);

  const handleLoginSuccess = async (loggedInUser: User) => {
    setUser(loggedInUser);
    const projList = await api.getProjects();
    setProjects(projList);
    if (projList.length > 0) {
      setActiveProject(projList[0]);
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setProjects([]);
    setActiveProject(null);
  };

  const handleProjectCreated = (newProj: Project) => {
    setProjects([newProj, ...projects]);
    setActiveProject(newProj);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F6F8F9] text-[#4A5B68] text-sm">
        Initializing ResearchForge Workspace...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F8F9]">
      <Navbar
        user={user}
        projects={projects}
        activeProject={activeProject}
        onSelectProject={setActiveProject}
        onLogout={handleLogout}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
      />

      <main className="flex-1">
        {!user ? (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        ) : activeTab === 'search' ? (
          <SearchPage activeProject={activeProject} />
        ) : activeTab === 'library' ? (
          <LibraryPage activeProject={activeProject} />
        ) : activeTab === 'screening' ? (
          <ScreeningPage activeProject={activeProject} />
        ) : activeTab === 'synthesis' ? (
          <SynthesisPage activeProject={activeProject} />
        ) : activeTab === 'lineage' ? (
          <LineagePage activeProject={activeProject} />
        ) : activeTab === 'journals' ? (
          <JournalsPage />
        ) : (
          <DashboardPage
            user={user}
            projects={projects}
            activeProject={activeProject}
            onProjectCreated={handleProjectCreated}
            onNavigateTab={setActiveTab}
          />
        )}
      </main>

      <footer className="bg-white border-t border-[#D7DEE3] py-4 text-center text-xs text-[#4A5B68]">
        ResearchForge v0.1 · Grounded Evidence Synthesis · PRISMA 2020 Flow · Zero Hallucination Policy
      </footer>
    </div>
  );
}

export default App;
