import Dashboard from "@/components/Dashboard";
import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    // The protected route will handle redirection, but we can be explicit.
    navigate("/");
  };

  if (!user) {
    // This should theoretically not be reached due to ProtectedRoute,
    // but it's good practice for robustness.
    return null; 
  }

  return <Dashboard user={user} onLogout={handleLogout} />;
};

export default DashboardPage;