import { useState } from 'react';
import './App.css';

const API_BASE =
  import.meta.env.VITE_API_BASE || 'https://<render-backend-url>';

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
        throw new Error(`API error ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError('Не удалось загрузить данные, попробуй ещё раз.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Твой день в истории</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Дата рождения:
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </label>

        <label>
          Город:
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Kyiv"
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Загружаю...' : 'Показать магию'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {data && (
        <div className="cards">
          <section className="card">
            <h2>Погода в этот день</h2>
            {data.weather ? (
              <>
                <p>
                  Максимум: {data.weather.t_max} °C, минимум:{' '}
                  {data.weather.t_min} °C
                </p>
                <p>{data.weather.anomaly_comment}</p>
              </>
            ) : (
              <p>Пока нет данных.</p>
            )}
          </section>

          <section className="card">
            <h2>Небо</h2>
            {data.astro ? (
              <>
                <p>Фаза Луны: {data.astro.moon_phase}</p>
                {data.astro.events && data.astro.events.length > 0 && (
                  <ul>
                    {data.astro.events.map((ev, idx) => (
                      <li key={idx}>{ev}</li>
                    ))}
                  </ul>
                )}
              </>
            ) : (
              <p>Пока нет данных.</p>
            )}
          </section>

          <section className="card">
            <h2>События в мире</h2>
            {data.world_events && data.world_events.length > 0 ? (
              <ul>
                {data.world_events.map((ev, idx) => (
                  <li key={idx}>{ev}</li>
                ))}
              </ul>
            ) : (
              <p>Пока пусто, но мы это заполним.</p>
            )}
          </section>

          <section className="card">
            <h2>Индекс необычности</h2>
            <p>{data.fun_score ?? 'скоро появится'}</p>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
