import { useState, useEffect } from 'react'
import './App.css'

const artists = [
  {
    name: 'Вінсент Ван Гог',
    birthdate: '30 березня 1853',
    biography: 'Вінсент Віллем ван Гог — нідерландський художник‑постімпресіоніст, одна з найвідоміших і найвпливовіших постатей в історії західного мистецтва.',
    history: 'За трохи більше як десятиліття створив близько 2 100 художніх робіт, у тому числі приблизно 860 олійних картин, більшість із яких належать до останніх двох років його життя. Роботи відзначаються сміливим кольором і драматичною виразністю мазків.',
    artworks: [
      {
        id: 1,
        title: 'Зоряна ніч',
        year: 1889,
        description: '«Зоряна ніч» була написана під час перебування ван Гога в лікарні для душевнохворих у Сен-Ремі-де-Прованс. Картина зображує вигаданий нічний пейзаж з вихровим небом і селом.'
      },
      {
        id: 2,
        title: 'Соняшники',
        year: 1888,
        description: 'Серія з кількох натюрмортів, на яких зображено соняшники у вазах. Символізують вдячність та дружбу.'
      },
      {
        id: 3,
        title: 'Спальня в Арлі',
        year: 1888,
        description: 'Картина зображає інтер’єр кімнати ван Гога в Арлі. Особливу увагу привертають яскраві кольори й спрощена перспектива.'
      }
    ]
  },
  {
    name: 'Клод Моне',
    birthdate: '14 листопада 1840',
    biography: 'Оскар-Клод Моне — французький живописець, один із засновників імпресіонізму, ключовий представник модернізму завдяки бажанню зобразити природу такою, якою він її бачив.',
    history: 'Протягом тривалої кар’єри був послідовним прихильником філософії імпресіонізму, особливо у пленерному живописі. Назва напряму походить від його картини «Враження. Сонце, що сходить».',
    artworks: [
      {
        id: 1,
        title: 'Враження. Сонце, що сходить',
        year: 1872,
        description: 'Картина, що дала назву імпресіонізму. Зображує порт Гавра вранці при туманному освітленні.'
      },
      {
        id: 2,
        title: 'Водяні лілії',
        year: 1916,
        description: 'Серія з приблизно 250 полотен, на яких зображені лілії з саду художника в Живерні. Одні з найвідоміших творів Моне.'
      },
      {
        id: 3,
        title: 'Жінка з парасолькою',
        year: 1875,
        description: 'Портрет дружини Моне Камілли і їхнього сина, написаний на пленері. Картина передає легкість руху й вітер.'
      }
    ]
  }
]

function App() {
  const [currentArtist, setCurrentArtist] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentArtist(prev => (prev + 1) % artists.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className='App'>
      <ArtistCard artist={artists[currentArtist]} />
    </div>
  )
}

function ArtistCard({ artist }) {
  return (
    <div className='artist-card'>
      <h1>{artist.name}</h1>
      <p><b>Дата народження:</b> {artist.birthdate}</p>
      <p><b>Біографія:</b> {artist.biography}</p>
      <p><b>Історія:</b> {artist.history}</p>
      <h2>Твори мистецтва:</h2>
      <div className='artworks'>
        {artist.artworks.map(artwork => (
          <Artwork key={artwork.id} artwork={artwork} />
        ))}
      </div>
    </div>
  )
}

function Artwork({ artwork }) {
  return (
    <div className='artwork'>
      <h3>{artwork.title} ({artwork.year})</h3>
      <p>{artwork.description}</p>
    </div>
  )
}

export default App