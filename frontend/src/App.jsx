import { useState } from 'react';
import './App.css';

const API_BASE =
  import.meta.env.VITE_API_BASE || 'https://birthday-day-info.onrender.com';

const cities = ['Kyiv', 'Lviv', 'Kharkiv', 'Odesa', 'Dnipro'];

function App() {
  const [date, setDate] = useState('');
  const [city, setCity] = useState('Kyiv');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!date) return;
    setLoading(true);
    setError('');
    setData(null);

    try {
      const params = new URLSearchParams({ date, city });
      const res = await fetch(`${API_BASE}/day-info?${params.toString()}`);
      if (!res.ok) {
        if (res.status === 400) {
          throw new Error('Невірний формат дати.');
        }
        throw new Error(`API error ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error(err);
      setError('Не вдалося завантажити дані, спробуй ще раз трохи пізніше.');
    } finally {
      setLoading(false);
    }
  };

  const renderWeather = () => {
    if (!data?.weather) return <p>Поки що немає даних.</p>;
    const { t_min, t_max, precipitation, anomaly_comment } = data.weather;
    if (t_min == null && t_max == null) {
      return <p>{anomaly_comment}</p>;
    }
    return (
      <>
        <p>
          Максимум: {t_max != null ? `${t_max} °C` : '—'}, мінімум:{' '}
          {t_min != null ? `${t_min} °C` : '—'}
        </p>
        <p>
          Опади:{' '}
          {precipitation != null ? `${precipitation} мм за добу` : 'дані відсутні'}
        </p>
        <p>{anomaly_comment}</p>
      </>
    );
  };

  const renderAstro = () => {
    if (!data?.astro) return <p>Поки що немає даних.</p>;
    const { sunrise, sunset, day_length } = data.astro;
    if (!sunrise && !sunset && !day_length) {
      return <p>Дані про Сонце поки що недоступні.</p>;
    }
    return (
      <>
        <p>Схід сонця: {sunrise || '—'}</p>
        <p>Захід сонця: {sunset || '—'}</p>
        <p>Тривалість дня: {day_length || '—'}</p>
      </>
    );
  };

  return (
    <div className="app">
      <h1>Твій день в історії</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Дата народження:
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </label>

        <label>
          Місто:
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
          >
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Завантажую…' : 'Показати магію'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {data && (
        <div className="cards">
          <section className="card">
            <h2>Погода в цей день</h2>
            {renderWeather()}
          </section>

          <section className="card">
            <h2>Небо</h2>
            {renderAstro()}
          </section>

          <section className="card">
            <h2>Події у світі</h2>
            {data.world_events && data.world_events.length > 0 ? (
              <ul>
                {data.world_events.map((ev, idx) => (
                  <li key={idx}>{ev}</li>
                ))}
              </ul>
            ) : (
              <p>Поки порожньо, але ми це заповнимо.</p>
            )}
          </section>

          <section className="card">
            <h2>Індекс незвичності</h2>
            <p>{data.fun_score ?? 'скоро зʼявиться'}</p>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
