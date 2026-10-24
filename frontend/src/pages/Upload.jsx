import { useState } from "react";
import { analyzeImage } from "../api/client";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [answers, setAnswers] = useState({
    sensation: "",
    moist_area: "",
    duration: "",
    pattern: "",
  });

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError("");
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const res = await analyzeImage(file, answers);
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Analysis failed. Is the backend running and the model trained?"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 pt-16 pb-20">
      <h1 className="font-display text-3xl mb-2">New scan</h1>
      <p className="text-clinic-ink/60 mb-8">
        Upload a clear, well-lit photo of the affected skin area.
      </p>

      <label className="block border-2 border-dashed border-clinic-line rounded-2xl p-10 text-center cursor-pointer hover:border-clinic-sage transition bg-white">
        <input
          type="file"
          accept="image/png, image/jpeg"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <img
            src={preview}
            alt="preview"
            className="max-h-64 mx-auto rounded-lg"
          />
        ) : (
          <p className="text-clinic-ink/50">
            Click to choose an image, or drag one here
          </p>
        )}
      </label>

      {file && !result && (
        <div className="mt-6 bg-white border border-clinic-line rounded-2xl p-5">
          <button
            type="button"
            onClick={() => setShowQuestionnaire(!showQuestionnaire)}
            className="text-sm text-clinic-sageDark underline"
          >
            {showQuestionnaire ? "Hide" : "Add"} a few quick details
            (optional, improves accuracy)
          </button>

          {showQuestionnaire && (
            <div className="mt-4 space-y-4">
              <QuestionGroup
                label="How does the area feel?"
                name="sensation"
                value={answers.sensation}
                onChange={(v) => setAnswers({ ...answers, sensation: v })}
                options={[
                  ["itchy", "Itchy"],
                  ["painful", "Painful / tender"],
                  ["burning", "Burning / stinging"],
                  ["none", "No particular sensation"],
                ]}
              />
              <QuestionGroup
                label="Is the area moist, sweaty, or in a skin fold (feet, groin, underarms)?"
                name="moist_area"
                value={answers.moist_area}
                onChange={(v) => setAnswers({ ...answers, moist_area: v })}
                options={[
                  ["yes", "Yes"],
                  ["no", "No"],
                ]}
              />
              <QuestionGroup
                label="How long has this been present?"
                name="duration"
                value={answers.duration}
                onChange={(v) => setAnswers({ ...answers, duration: v })}
                options={[
                  ["days", "A few days"],
                  ["weeks", "A few weeks"],
                  ["months", "Months or longer"],
                ]}
              />
              <QuestionGroup
                label="Does it come and go, or stay constant?"
                name="pattern"
                value={answers.pattern}
                onChange={(v) => setAnswers({ ...answers, pattern: v })}
                options={[
                  ["comes_and_goes", "Comes and goes"],
                  ["constant", "Fairly constant"],
                ]}
              />
            </div>
          )}
        </div>
      )}

      {file && !result && (
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-4 w-full bg-clinic-sage text-white py-3 rounded-full hover:bg-clinic-sageDark transition disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze image"}
        </button>
      )}

      {error && <p className="text-sm text-red-600 mt-4">{error}</p>}

      {result && (
        <div className="mt-10 bg-white border border-clinic-line rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-clinic-ink/50">
                Predicted condition
              </p>
              <p className="font-display text-2xl capitalize">
                {result.predicted_class.replace("_", " ")}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-wide text-clinic-ink/50">
                Confidence
              </p>
              <p className="font-display text-2xl">
                {(result.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs text-clinic-ink/50 mb-1">Original</p>
              <img
                src={`${API_BASE_URL}${result.original_image_url}`}
                className="rounded-lg w-full"
              />
            </div>
            <div>
              <p className="text-xs text-clinic-ink/50 mb-1">
                Grad-CAM heatmap
              </p>
              <img
                src={`${API_BASE_URL}${result.heatmap_image_url}`}
                className="rounded-lg w-full"
              />
            </div>
          </div>

          <div className="bg-clinic-bg rounded-lg p-4 mb-3">
            <p className="text-sm">{result.recommendation}</p>
          </div>
          {result.questionnaire_used && (
            <p className="text-xs text-clinic-sageDark mb-2">
              This result includes your answers to the quick questions,
              alongside the image analysis.
            </p>
          )}
          <p className="text-xs text-clinic-ink/40">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}

function QuestionGroup({ label, name, value, onChange, options }) {
  return (
    <div>
      <p className="text-sm text-clinic-ink/80 mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map(([val, text]) => (
          <button
            key={val}
            type="button"
            onClick={() => onChange(val)}
            className={`text-sm px-3 py-1.5 rounded-full border transition ${
              value === val
                ? "bg-clinic-sage text-white border-clinic-sage"
                : "border-clinic-line text-clinic-ink/70 hover:border-clinic-sage"
            }`}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}
