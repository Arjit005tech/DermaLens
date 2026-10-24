import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signup, login } from "../api/client";

export default function Signup() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await signup(form.name, form.email, form.password);
      await login(form.email, form.password);
      navigate("/upload");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <div className="max-w-sm mx-auto px-6 pt-20">
      <h1 className="font-display text-3xl mb-8">Create your account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field
          label="Name"
          value={form.name}
          onChange={(v) => setForm({ ...form, name: v })}
        />
        <Field
          label="Email"
          type="email"
          value={form.email}
          onChange={(v) => setForm({ ...form, email: v })}
        />
        <Field
          label="Password"
          type="password"
          value={form.password}
          onChange={(v) => setForm({ ...form, password: v })}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          className="w-full bg-clinic-sage text-white py-3 rounded-full hover:bg-clinic-sageDark transition"
        >
          Sign up
        </button>
      </form>
      <p className="text-sm text-clinic-ink/60 mt-6">
        Already have an account?{" "}
        <Link to="/login" className="text-clinic-sageDark underline">
          Log in
        </Link>
      </p>
    </div>
  );
}

function Field({ label, value, onChange, type = "text" }) {
  return (
    <label className="block text-sm">
      <span className="text-clinic-ink/70">{label}</span>
      <input
        type={type}
        required
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full border border-clinic-line rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-clinic-sage"
      />
    </label>
  );
}
