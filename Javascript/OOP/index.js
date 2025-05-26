class PrintMachine {
  constructor(fontSize, color, fontFamily) {
    this.fontSize = fontSize;
    this.color = color;
    this.fontFamily = fontFamily;
  }
  print(text) {
    document.write(`<p style="font-size:${this.fontSize};color:${this.color};font-family:${this.fontFamily}">${text}</p>`);
  }
}

class NewsItem {
  constructor(title, text, tags, date) {
    this.title = title;
    this.text = text;
    this.tags = tags;
    this.date = new Date(date);
  }
  print() {
    const now = Date.now();
    const diffMs = now - this.date.getTime();
    const diffDays = Math.floor(diffMs / 86400000);
    let dateLabel = '';
    if (diffMs < 86400000) dateLabel = 'today';
    else if (diffDays < 7) dateLabel = `${diffDays} days ago`;
    else {
      const d = String(this.date.getDate()).padStart(2,'0');
      const m = String(this.date.getMonth()+1).padStart(2,'0');
      const y = this.date.getFullYear();
      dateLabel = `${d}.${m}.${y}`;
    }
    document.write(`
      <div style="border:1px solid #ccc;padding:10px;margin:10px 0">
        <h3>${this.title}</h3>
        <small>${dateLabel}</small>
        <p>${this.text}</p>
        <p>Tags: ${this.tags.map(t=>`#${t}`).join(' ')}</p>
      </div>
    `);
  }
}

class NewsFeed {
  constructor() {
    this.news = [];
  }
  get count() {
    return this.news.length;
  }
  add(item) {
    this.news.push(item);
  }
  remove(item) {
    this.news = this.news.filter(n=>n !== item);
  }
  printAll() {
    this.news.forEach(n=>n.print());
  }
  sortByDate() {
    this.news.sort((a,b)=>b.date - a.date);
  }
  searchByTag(tag) {
    return this.news.filter(n=>n.tags.includes(tag));
  }
}

const printer = new PrintMachine('48px','green','Arial');
printer.print('Hello, world!');

const n1 = new NewsItem('Lorem','Lorem ipsum dolor sit amet consectetur adipisicing elit. Reprehenderit a ipsam necessitatibus nemo deserunt quidem dolore fugiat? Omnis doloribus facilis neque placeat corporis dolorum aliquam adipisci, assumenda in, aspernatur illum.',['tag1','jtag2'],'2025-05-24');
const n2 = new NewsItem('lorem','Lorem ipsum dolor sit amet consectetur adipisicing elit. Eos nam a ea assumenda excepturi illo nisi cumque, provident in! Nobis vero assumenda ex, nostrum laboriosam laborum? Maxime beatae vero perspiciatis.',['lorem'],'2025-05-20');
const feed = new NewsFeed();
feed.add(n1);
feed.add(n2);
feed.sortByDate();
feed.printAll();
console.log(feed.count);
const found = feed.searchByTag('js');
found.forEach(n=>n.print());
