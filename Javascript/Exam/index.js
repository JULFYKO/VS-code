const apiKey = '77e3476d0462c40b742a1071bd746de1';
let currentCity = 'Київ';
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');
const tabs = document.querySelectorAll('.tab-btn');
const contents = document.querySelectorAll('.tab-content');
const errorPage = document.getElementById('error-page');


tabs.forEach(btn=>{
  btn.addEventListener('click', ()=>{
    tabs.forEach(b=>b.classList.remove('active'));
    contents.forEach(c=>c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab==='forecast') fetchForecast();
    else fetchToday();
  });
});

searchBtn.addEventListener('click', ()=> {
  currentCity = cityInput.value.trim() || currentCity;
  fetchAll();
});

window.addEventListener('load', () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos=>{
      const {latitude, longitude} = pos.coords;
      fetchCityByCoords(latitude, longitude)
        .then(city=>{ currentCity=city; cityInput.value=city; fetchAll(); })
        .catch(()=> { cityInput.value=currentCity; fetchAll(); });
    }, ()=>{ cityInput.value=currentCity; fetchAll(); });
  } else {
    cityInput.value=currentCity;
    fetchAll();
  }
});

function fetchAll() {
  errorPage.classList.add('hidden');
  if (document.querySelector('.tab-btn.active').dataset.tab==='forecast') fetchForecast();
  else fetchToday();
}

async function fetchCityByCoords(lat, lon) {
  const res = await fetch(`https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=${apiKey}`);
  const data = await res.json();
  if (!data[0]) throw new Error();
  return data[0].name;
}

async function fetchToday() {
  try {
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${currentCity}&units=metric&lang=uk&appid=${apiKey}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error();
    const today = await res.json();
    renderTodaySummary(today);
    renderTodayHourly(today.coord.lat, today.coord.lon);
    renderNearby(today.coord.lat, today.coord.lon);
  } catch {
    showError();
  }
}

async function renderTodaySummary(d) {
  const sunrise = new Date(d.sys.sunrise*1000);
  const sunset = new Date(d.sys.sunset*1000);
  const dayLengthMs = d.sys.sunset*1000 - d.sys.sunrise*1000;
  document.getElementById('today-summary').innerHTML = `
    <h2>${d.name}, ${new Date().toLocaleDateString()}</h2>
    <img src="https://openweathermap.org/img/wn/${d.weather[0].icon}@2x.png"/>
    <p>${d.weather[0].description}</p>
    <p>Темп: ${d.main.temp.toFixed(1)}°C (відчувається як ${d.main.feels_like.toFixed(1)}°C)</p>
    <p>Схід: ${sunrise.toLocaleTimeString()}</p>
    <p>Захід: ${sunset.toLocaleTimeString()}</p>
    <p>Тривалість дня: ${Math.floor(dayLengthMs/3600000)} год ${Math.floor((dayLengthMs%3600000)/60000)} хв</p>
  `;
}

async function renderTodayHourly(lat, lon) {
  const res = await fetch(`https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&lang=uk&appid=${apiKey}`);
  const data = await res.json();

  const todayDate = new Date().getDate();
  const hours = data.list.filter(item => new Date(item.dt * 1000).getDate() === todayDate);

  const html = hours.map(h => `
    <div class="hour">
      <span>${new Date(h.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
      <img src="https://openweathermap.org/img/wn/${h.weather[0].icon}.png"/>
      <span>${h.weather[0].description}</span>
      <span>${h.main.temp.toFixed(1)}°C (feels ${h.main.feels_like.toFixed(1)}°C)</span>
      <span>Вітер: ${h.wind.speed} м/с ${getWindDir(h.wind.deg)}</span>
    </div>
  `).join('');
  
  document.getElementById('today-hourly').innerHTML = html;
}

async function renderNearby(lat, lon) {
  const res = await fetch(`https://api.openweathermap.org/data/2.5/find?lat=${lat}&lon=${lon}&cnt=5&units=metric&appid=${apiKey}`);
  const data = await res.json();
  const html = data.list.map(c=>`
    <div class="nearby-city">
      <strong>${c.name}</strong>
      <img src="https://openweathermap.org/img/wn/${c.weather[0].icon}.png"/>
      <span>${c.main.temp.toFixed(1)}°C</span>
    </div>
  `).join('');
  document.getElementById('nearby').innerHTML = html;
}

let selectedDayIndex = null;
async function fetchForecast() {
  try {
    const res = await fetch(`https://api.openweathermap.org/data/2.5/forecast?q=${currentCity}&units=metric&lang=uk&appid=${apiKey}`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    renderForecastSummary(data.list);
    const todayIdx = 0;
    selectForecastDay(todayIdx);
  } catch {
    showError();
  }
}

function renderForecastSummary(list) {
  const days = {};
  list.forEach(item=>{
    const day = new Date(item.dt*1000).toLocaleDateString('uk-UA',{weekday:'long', day:'numeric'});
    if (!days[day]) days[day] = [];
    days[day].push(item);
  });
  const html = Object.entries(days).slice(0,5).map(([day, items], idx)=> {
    const mid = items[Math.floor(items.length/2)];
    return `<div class="day-summary" data-idx="${idx}">${day}
      <img src="https://openweathermap.org/img/wn/${mid.weather[0].icon}.png"/>
      <span>${mid.main.temp.toFixed(1)}°C</span>
      <p>${mid.weather[0].description}</p>
    </div>`;
  }).join('');
  const container = document.getElementById('forecast-summary');
  container.innerHTML = html;
  container.querySelectorAll('.day-summary').forEach(el=>{
    el.addEventListener('click', ()=> selectForecastDay(+el.dataset.idx));
  });
}

function selectForecastDay(idx) {
  const summaries = [...document.querySelectorAll('.day-summary')];
  summaries.forEach(el=>el.classList.toggle('active', +el.dataset.idx===idx));
  selectedDayIndex = idx;
  renderForecastHourly(idx);
}

function renderForecastHourly(dayIdx) {
  fetch(`https://api.openweathermap.org/data/2.5/forecast?q=${currentCity}&units=metric&lang=uk&appid=${apiKey}`)
    .then(r=>r.json())
    .then(data=>{
      const days = {};
      data.list.forEach(item=>{
        const key = new Date(item.dt*1000).toLocaleDateString('uk-UA',{weekday:'long', day:'numeric'});
        if (!days[key]) days[key]=[];
        days[key].push(item);
      });
      const dayKey = Object.keys(days)[dayIdx];
      const html = days[dayKey].map(h=>`
        <div class="hour">
          <span>${new Date(h.dt*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
          <img src="https://openweathermap.org/img/wn/${h.weather[0].icon}.png"/>
          <span>${h.weather[0].description}</span>
          <span>${h.main.temp.toFixed(1)}°C (feels ${h.main.feels_like.toFixed(1)}°C)</span>
          <span>Вітер: ${h.wind.speed} м/с ${getWindDir(h.wind.deg)}</span>
        </div>
      `).join('');
      document.getElementById('forecast-hourly').innerHTML = html;
    });
}

function getWindDir(deg) {
  const dirs = ['Пн','ПнСх','Сх','ПдСх','Пд','ПдЗх','Зх','ПнЗх'];
  return dirs[Math.round(deg/45)%8];
}

function showError() {
  errorPage.classList.remove('hidden');
  contents.forEach(c=>c.classList.remove('active'));
}