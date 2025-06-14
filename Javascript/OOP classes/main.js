class Circle {
    constructor(radius) {
        this._radius = radius;
    }

    get radius() {
        return this._radius;
    }

    set radius(value) {
        this._radius = value;
    }

    get diameter() {
        return this._radius * 2;
    }

    getArea() {
        return Math.PI * this._radius * this._radius;
    }

    getCircumference() {
        return 2 * Math.PI * this._radius;
    }
}

const c = new Circle(10);
console.log('Radius:', c.radius);
console.log('Diameter:', c.diameter);
console.log('Area:', c.getArea());
console.log('Circumference:', c.getCircumference());
c.radius = 5;
console.log('New radius:', c.radius);

class HtmlElement {
    constructor(tagName, isSelfClosing = false, text = '') {
        this.tagName = tagName;
        this.isSelfClosing = isSelfClosing;
        this.text = text;
        this.attributes = [];
        this.styles = [];
        this.children = [];
    }

    setAttribute(name, value) {
        const idx = this.attributes.findIndex(attr => attr.name === name);
        if (idx >= 0) this.attributes[idx].value = value;
        else this.attributes.push({ name, value });
    }

    setStyle(property, value) {
        const idx = this.styles.findIndex(style => style.property === property);
        if (idx >= 0) this.styles[idx].value = value;
        else this.styles.push({ property, value });
    }

    appendChild(element) {
        this.children.push(element);
    }

    prependChild(element) {
        this.children.unshift(element);
    }

    getHtml() {
        let attrStr = this.attributes.map(a => ` ${a.name}="${a.value}"`).join('');
        let styleStr = this.styles.length
            ? ` style="${this.styles.map(s => `${s.property}: ${s.value};`).join(' ')}"`
            : '';
        if (this.isSelfClosing) {
            return `<${this.tagName}${attrStr}${styleStr} />`;
        }
        let childrenHtml = this.children.map(child => child.getHtml()).join('');
        return `<${this.tagName}${attrStr}${styleStr}>${this.text}${childrenHtml}</${this.tagName}>`;
    }
}

class CssClass {
    constructor(className) {
        this.className = className;
        this.styles = [];
    }

    setStyle(property, value) {
        const idx = this.styles.findIndex(s => s.property === property);
        if (idx >= 0) this.styles[idx].value = value;
        else this.styles.push({ property, value });
    }

    removeStyle(property) {
        this.styles = this.styles.filter(s => s.property !== property);
    }

    getCss() {
        if (!this.styles.length) return '';
        const stylesStr = this.styles.map(s => `${s.property}: ${s.value};`).join(' ');
        return `.${this.className} { ${stylesStr} }`;
    }
}

class HtmlBlock {
    constructor() {
        this.cssClasses = [];
        this.rootElement = null;
    }

    addCssClass(cssClass) {
        this.cssClasses.push(cssClass);
    }

    setRootElement(element) {
        this.rootElement = element;
    }

    getCode() {
        const styles = this.cssClasses.map(c => c.getCss()).join('\n');
        const styleTag = styles ? `<style>\n${styles}\n</style>\n` : '';
        return styleTag + (this.rootElement ? this.rootElement.getHtml() : '');
    }
}

const wrapClass = new CssClass('wrap');
wrapClass.setStyle('display', 'flex');
wrapClass.setStyle('gap', '20px');

const blockClass = new CssClass('block');
blockClass.setStyle('width', '300px');
blockClass.setStyle('margin', '10px');
blockClass.setStyle('border', '1px solid #ccc');
blockClass.setStyle('padding', '10px');
blockClass.setStyle('box-sizing', 'border-box');

const imgClass = new CssClass('img');
imgClass.setStyle('width', '100%');

const textClass = new CssClass('text');
textClass.setStyle('text-align', 'justify');

const wrapper2 = new HtmlElement('div');
wrapper2.setAttribute('id', 'wrapper');
wrapper2.setAttribute('class', 'wrap');

for (let i = 0; i < 2; i++) {
    const block = new HtmlElement('div');
    block.setAttribute('class', 'block');

    const h3 = new HtmlElement('h3', false, 'What is Lorem Ipsum?');
    const img = new HtmlElement('img', true);
    img.setAttribute('class', 'img');
    img.setAttribute('src', 'lipsum.jpg');
    img.setAttribute('alt', 'Lorem Ipsum');

    const p = new HtmlElement('p');
    p.setAttribute('class', 'text');
    p.text = `"Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. "`;

    const a = new HtmlElement('a', false, 'More...');
    a.setAttribute('href', 'https://www.lipsum.com/');
    a.setAttribute('target', '_blank');
    p.appendChild(a);

    block.appendChild(h3);
    block.appendChild(img);
    block.appendChild(p);

    wrapper2.appendChild(block);
}

const htmlBlock = new HtmlBlock();
htmlBlock.addCssClass(wrapClass);
htmlBlock.addCssClass(blockClass);
htmlBlock.addCssClass(imgClass);
htmlBlock.addCssClass(textClass);
htmlBlock.setRootElement(wrapper2);

document.write(htmlBlock.getCode());
