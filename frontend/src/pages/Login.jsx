import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/client";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(form.email, form.password);
      navigate("/upload");
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid email or password");
    }
  };

  return (
    <div className="max-w-sm mx-auto px-6 pt-20">
      <h1 className="font-display text-3xl mb-8">Welcome back</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm">
          <span className="text-clinic-ink/70">Email</span>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="mt-1 w-full border border-clinic-line rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-clinic-sage"
          />
        </label>
        <label className="block text-sm">
          <span className="text-clinic-ink/70">Password</span>
          <input
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="mt-1 w-full border border-clinic-line rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-clinic-sage"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          className="w-full bg-clinic-sage text-white py-3 rounded-full hover:bg-clinic-sageDark transition"
        >
          Log in
        </button>
      </form>
      <p className="text-sm text-clinic-ink/60 mt-6">
        Need an account?{" "}
        <Link to="/signup" className="text-clinic-sageDark underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
