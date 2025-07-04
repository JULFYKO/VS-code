import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import "./App.css";

function Biography() {
  return (
    <div>
      <h2>Vincent van Gogh - Biography</h2>
      <p>
        Vincent van Gogh was a Dutch post-impressionist painter who is among the
        most famous and influential figures in the history of Western art. He
        created about 2,100 artworks, including around 860 oil paintings, most of
        them in the last two years of his life.
      </p>
    </div>
  );
}

function FamousPainting() {
  return (
    <div>
      <h2>Starry Night</h2>
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/500px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"
        alt="Starry Night"
        className="painting-img"
      />
      <p>
        "The Starry Night" is one of van Gogh's most famous paintings, painted
        in June 1889.
      </p>
    </div>
  );
}

function Collection() {
  const paintings = [
    {
      title: "Sunflowers",
      img: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Vincent_Willem_van_Gogh_127.jpg/250px-Vincent_Willem_van_Gogh_127.jpg",
    },
    {
      title: "Café Terrace at Night",
      img: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Vincent_van_Gogh_%281853-1890%29_Caf%C3%A9terras_bij_nacht_%28place_du_Forum%29_Kr%C3%B6ller-M%C3%BCller_Museum_Otterlo_23-8-2016_13-35-40.JPG/330px-Vincent_van_Gogh_%281853-1890%29_Caf%C3%A9terras_bij_nacht_%28place_du_Forum%29_Kr%C3%B6ller-M%C3%BCller_Museum_Otterlo_23-8-2016_13-35-40.JPG",
    },
    {
      title: "Irises",
      img: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Irises-Vincent_van_Gogh.jpg/330px-Irises-Vincent_van_Gogh.jpg",
    },
  ];
  return (
    <div>
      <h2>Collection of Paintings</h2>
      <div className="collection-list">
        {paintings.map((p) => (
          <div key={p.title} className="collection-item">
            <img src={p.img} alt={p.title} className="painting-img" />
            <p>{p.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function NotFound() {
  return (
    <div className="not-found">
      <h2>Сторінку не знайдено</h2>
      <p>404 – Такої сторінки не існує.</p>
    </div>
  );
}

function App() {
  return (
    <>
      <nav className="main-nav">
        <Link to="/" className="nav-link">
          Biography
        </Link>
        <Link to="/famous" className="nav-link">
          Famous Painting
        </Link>
        <Link to="/collection" className="nav-link">
          Collection
        </Link>
      </nav>
      <Routes>
        <Route path="/" element={<Biography />} />
        <Route path="/famous" element={<FamousPainting />} />
        <Route path="/collection" element={<Collection />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}

export default App;
