import { Link, useNavigate } from "react-router-dom";
import { isAuthenticated, logout } from "../api/client";

export default function Navbar() {
  const navigate = useNavigate();
  const authed = isAuthenticated();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="border-b border-clinic-line bg-clinic-bg/90 backdrop-blur sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="font-display text-xl tracking-tight">
          Derma<span className="text-clinic-clay">Lens</span>
        </Link>
        <div className="flex items-center gap-6 text-sm">
          {authed ? (
            <>
              <Link to="/upload" className="hover:text-clinic-sageDark">
                New Scan
              </Link>
              <Link to="/dashboard" className="hover:text-clinic-sageDark">
                History
              </Link>
              <button
                onClick={handleLogout}
                className="text-clinic-clay hover:text-clinic-sageDark"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-clinic-sageDark">
                Log in
              </Link>
              <Link
                to="/signup"
                className="bg-clinic-sage text-white px-4 py-2 rounded-full hover:bg-clinic-sageDark transition"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
