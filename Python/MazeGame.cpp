#include <iostream>
#include <conio.h>
#include <vector>
#include <stack>
#include <cstdlib>
#include <ctime>

#define WIDTH 30
#define HEIGHT 30

using namespace std;

enum Key {
    ESC = 27,
    UP = 72,
    DOWN = 80,
    LEFT = 75,
    RIGHT = 77
};

// Структура для зберігання координат
struct Cell {
    int x, y;
};

void printMaze(char maze[HEIGHT][WIDTH], int cursorX, int cursorY) {
    system("cls");
    for (int i = 0; i < HEIGHT; i++) {
        for (int j = 0; j < WIDTH; j++) {
            if (i == cursorY && j == cursorX) {
                cout << "[*]";
            }
            else {
                cout << " " << maze[i][j] << " ";
            }
        }
        cout << endl;
    }
}

// Перевірка, чи можна пройти в клітинку (мешканці на парних індексах – стіни)
bool isValid(int x, int y) {
    return (x > 0 && x < WIDTH - 1 && y > 0 && y < HEIGHT - 1);
}

// Отримати сусідів для алгоритму-бектрекінгу
vector<Cell> getNeighbors(const Cell& c, char maze[HEIGHT][WIDTH]) {
    vector<Cell> neighbors;
    // Зсуви у чотирьох напрямках через два кроки
    int dx[4] = { 0, 0, 2, -2 };
    int dy[4] = { 2, -2, 0, 0 };

    for (int i = 0; i < 4; i++) {
        int nx = c.x + dx[i];
        int ny = c.y + dy[i];
        if (isValid(nx, ny) && maze[ny][nx] == '#') {
            neighbors.push_back({nx, ny});
        }
    }
    return neighbors;
}

// Функція для вибіркового видалення перегородки між двома клітинками
void removeWall(const Cell& a, const Cell& b, char maze[HEIGHT][WIDTH]) {
    int wallX = (a.x + b.x) / 2;
    int wallY = (a.y + b.y) / 2;
    maze[wallY][wallX] = ' ';
}

// Генерація лабіринту методом рекурсивного бектрекінгу (ітеровано зі стеком)
void generateMaze(char maze[HEIGHT][WIDTH]) {
    // Спочатку заповнюємо весь масив стінами
    for (int i = 0; i < HEIGHT; i++) {
        for (int j = 0; j < WIDTH; j++) {
            maze[i][j] = '#';
        }
    }

    srand(time(NULL));
    stack<Cell> st;
    Cell start = {1, 1};
    maze[start.y][start.x] = ' ';
    st.push(start);

    while (!st.empty()) {
        Cell current = st.top();
        vector<Cell> neighbors = getNeighbors(current, maze);

        if (!neighbors.empty()) {
            // Обираємо випадкового сусіда
            Cell next = neighbors[rand() % neighbors.size()];
            // Видаляємо стінку між поточним і сусіднім
            removeWall(current, next, maze);
            // Позначаємо нову клітинку як кімнату
            maze[next.y][next.x] = ' ';
            // Переходимо далі
            st.push(next);
        }
        else {
            // Немає доступних сусідів – повертаємось
            st.pop();
        }
    }

    // Встановлюємо точки входу та виходу
    maze[1][1] = 'S';                                   // Старт
    maze[HEIGHT - 2][WIDTH - 2] = 'E';                   // Кінець
}

int main() {
    char maze[HEIGHT][WIDTH];
    generateMaze(maze);

    int cursorX = 1, cursorY = 1;  // Початкова позиція на 'S'
    char key;

    while (true) {
        printMaze(maze, cursorX, cursorY);
        key = _getch();

        if (key == ESC) break;

        switch (key) {
        case UP:
            if (cursorY > 0 && maze[cursorY - 1][cursorX] != '#') cursorY--;
            break;
        case DOWN:
            if (cursorY < HEIGHT - 1 && maze[cursorY + 1][cursorX] != '#') cursorY++;
            break;
        case LEFT:
            if (cursorX > 0 && maze[cursorY][cursorX - 1] != '#') cursorX--;
            break;
        case RIGHT:
            if (cursorX < WIDTH - 1 && maze[cursorY][cursorX + 1] != '#') cursorX++;
            break;
        }

        if (maze[cursorY][cursorX] == 'E') {
            printMaze(maze, cursorX, cursorY);
            cout << "You reached the end!" << endl;
            break;
        }
    }

    return 0;
}
