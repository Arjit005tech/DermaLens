import { Link } from "react-router-dom";
import { isAuthenticated } from "../api/client";

export default function Home() {
  const authed = isAuthenticated();

  return (
    <div className="max-w-3xl mx-auto px-6 pt-24 pb-16 text-center">
      <p className="uppercase tracking-[0.2em] text-xs text-clinic-sageDark mb-4">
        Personal AI Skin Expert
      </p>
      <h1 className="font-display text-5xl leading-tight mb-6">
        A closer look at your skin,
        <br />
        in under three seconds.
      </h1>
      <p className="text-clinic-ink/70 max-w-xl mx-auto mb-10">
        Upload a photo and get an AI-assisted read on common skin
        conditions, with a visual heatmap showing exactly what the model
        noticed — plus guidance on what to do next.
      </p>
      <Link
        to={authed ? "/upload" : "/signup"}
        className="inline-block bg-clinic-sage text-white px-8 py-3 rounded-full hover:bg-clinic-sageDark transition"
      >
        {authed ? "Start a new scan" : "Create a free account"}
      </Link>

      <div className="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-8 text-left">
        <Feature
          n="01"
          title="Upload"
          desc="A clear photo of the affected area is all it takes."
        />
        <Feature
          n="02"
          title="Analyze"
          desc="A CNN trained on dermatology image data classifies the condition."
        />
        <Feature
          n="03"
          title="Understand"
          desc="A heatmap shows what the model focused on — no black box."
        />
      </div>

      <p className="text-xs text-clinic-ink/40 mt-16 max-w-md mx-auto">
        DermaLens is a preliminary screening tool, not a medical diagnosis.
        Always consult a licensed dermatologist for confirmation and
        treatment.
      </p>
    </div>
  );
}

function Feature({ n, title, desc }) {
  return (
    <div className="border-t border-clinic-line pt-4">
      <span className="text-xs text-clinic-clay font-medium">{n}</span>
      <h3 className="font-display text-lg mt-1 mb-1">{title}</h3>
      <p className="text-sm text-clinic-ink/60">{desc}</p>
    </div>
  );
}
