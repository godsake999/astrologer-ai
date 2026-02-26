'use client';

import { useState, useEffect } from 'react';
import styles from './page.module.css';
import ChartDisplay from '@/components/ChartDisplay';
import ReadingResult from '@/components/ReadingResult';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface SynthesisData {
  western: {
    sun: string; moon: string; mercury: string; venus: string;
    mars: string; jupiter: string; saturn: string;
    ascendant: string; dominant_aspects: string[];
  };
  vedic: {
    nakshatra: string; nakshatra_pada: number; nakshatra_lord: string;
    mahadasha: string; mahadasha_ends: string; next_dasha: string;
  };
  mahabote: {
    birth_day: string; birth_day_burmese: string;
    house_name: string; house_burmese: string; ruling_planet: string;
    be_year: number; nakshatra_burmese: string; grid_number: number; characteristics: string;
  };
}

interface ResultData {
  synthesis: SynthesisData;
  reading: string | null;
  error: string | null;
}

export default function Home() {
  const [formData, setFormData] = useState({ name: '', gender: 'Male', dob: '', time: '', city: '' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResultData | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [stars, setStars] = useState<{ left: string, top: string, delay: string }[]>([]);

  useEffect(() => {
    setStars(
      Array.from({ length: 20 }).map(() => ({
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        delay: `${Math.random() * 3}s`,
      }))
    );
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setApiError(null);
    setResult(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/synthesis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `Error ${response.status}`);
      }

      const data: ResultData = await response.json();
      setResult(data);
    } catch (err: any) {
      setApiError(err.message || 'Failed to connect to the server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Hero Header */}
      <header className={`${styles.header} animate-fade-in`}>
        <div className={styles.starfield} aria-hidden="true">
          {stars.map((star, i) => (
            <span key={i} className={styles.star} style={{
              left: star.left,
              top: star.top,
              animationDelay: star.delay,
            }} />
          ))}
        </div>
        <h1 className={styles.title}>AstroLogic AI</h1>
        <p className={`${styles.subtitle} burmese`}>
          Western • Vedic • မဟာဘုတ် (Mahabote)
        </p>
        <p className={styles.subtitleEn}>
          High-precision astrology powered by astronomical calculation & AI wisdom.
        </p>
      </header>

      <main className={styles.mainGrid}>
        {/* Input Form */}
        <aside className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <form className={styles.formCard} onSubmit={handleSubmit}>
            <h2 className={styles.formTitle}>✦ ဗေဒင် တွက်ချက်ရန် ✦</h2>

            <div className={styles.inputGroup}>
              <label htmlFor="name" className={styles.label}>Your Name</label>
              <input type="text" id="name" className={styles.input} placeholder="e.g. Ko Jimmy"
                value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="gender" className={styles.label}>Gender</label>
              <select id="gender" className={styles.input} value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}>
                <option value="Male">Male (ကျား)</option>
                <option value="Female">Female (မ)</option>
              </select>
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="dob" className={`${styles.label} burmese`}>မွေးသက္ကရာဇ် (Date of Birth)</label>
              <input type="date" id="dob" className={styles.input} value={formData.dob}
                onChange={(e) => setFormData({ ...formData, dob: e.target.value })} required />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="time" className={`${styles.label} burmese`}>မွေးဖွားချိန် (Exact Time)</label>
              <input type="time" id="time" className={styles.input} value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })} required />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="city" className={`${styles.label} burmese`}>မွေးဖွားရာမြို့ (City of Birth)</label>
              <input type="text" id="city" className={styles.input} placeholder="e.g. Yangon, Myanmar"
                value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} required />
            </div>

            <button type="submit" id="synthesize-btn" className={styles.submitBtn} disabled={loading}>
              <span className="burmese">
                {loading ? '⟳ တွက်ချက်နေသည်...' : '⟡ ဗေဒင် ဟောကြည့်ရန်'}
              </span>
            </button>

            {apiError && (
              <div className={styles.errorBox}>
                <strong>Error:</strong> {apiError}
              </div>
            )}
          </form>
        </aside>

        {/* Results */}
        <section className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <p className="burmese">ဗေဒင် တွက်ချက်နေသည်...</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Calculating planetary positions & generating your reading...
              </p>
            </div>
          )}

          {!loading && !result && (
            <div className={styles.placeholder}>
              <div className={styles.placeholderIcon}>🌌</div>
              <h3 className="burmese">သင်၏ ဘ၀ မောင်းနှင်ကြောင်းများကို ရှာဖွေပါ</h3>
              <p>Enter your birth details on the left to reveal your cosmic blueprint.</p>
              <div className={styles.featureList}>
                <div>☉ Western Natal Chart</div>
                <div>🕉 Vedic Nakshatra & Dasha</div>
                <div className="burmese">✦ မဟာဘုတ် Grid</div>
                <div className="burmese">🔮 AI ဟောစာတမ်း (Burmese)</div>
              </div>
            </div>
          )}

          {!loading && result && (
            <div className={styles.resultsArea}>
              <ChartDisplay
                western={result.synthesis.western}
                vedic={result.synthesis.vedic}
                mahabote={result.synthesis.mahabote}
              />
              {result.reading && (
                <div style={{ marginTop: '1.5rem' }}>
                  <ReadingResult reading={result.reading} />
                </div>
              )}
              {!result.reading && (
                <div className={styles.noReadingNote}>
                  <p>Note: Set <code>OPENROUTER_API_KEY</code> in <code>backend/.env</code> to enable the AI reading. (If in a restricted region, a VPN may be required).</p>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      <footer className={styles.footer}>
        <p>
          <span className="burmese">AstroLogic AI</span> — Western + Vedic + Burmese Mahabote synthesis.
          Astronomical data is mathematically calculated; for guidance only.
        </p>
      </footer>
    </div>
  );
}
