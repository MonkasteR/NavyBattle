import random


class Game:
    def __init__(self, size=9):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.user = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = layout
        field = Field(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(random.randint(0, self.size), random.randint(0, self.size)), l, random.randint(0, 1))
                try:
                    field.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        field.begin()
        return field

    def greeting(self):
        print('┌──────────────────────────────┐')
        print('│       Игра морской бой       │')
        print('├──────────────────────────────┤')
        print('│ Введите координаты хода, два │')
        print(f'│ числа от 1 до {self.size} через пробел │')
        print('│ номер строки и номер столбца │')
        print('└──────────────────────────────┘')

    def loop(self):
        num = 0

        def print_fields():
            print("────" + "─" * 9 * g.size)

            # Получаем строки с досками игрока и компьютера
            user_board_str = str(self.user.field).split("\n")
            ai_board_str = str(self.ai.field).split("\n")

            # Объединяем строки игровых досок построчно с помощью zip()
            # и выводим горизонтально
            for row_user, row_ai in zip(user_board_str, ai_board_str):
                print(f"{' ' * 2}{row_user}{' ' * 5}{row_ai}")

        while True:
            print_fields()
            if num % 2 == 0:
                print("────" + "─" * 9 * g.size)  # Пытаемся подстроиться под размер доски
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("────" + "─" * 9 * g.size)  # Пытаемся подстроиться под размер доски
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.field.count == len(layout):  # счетчик потопленных кораблей
                print_fields()
                print("────" + "─" * 9 * g.size)  # Пытаемся подстроиться под размер доски
                print("Игрок победил!")
                print(f'Вы потопили все {len(layout)} кораблей противника')
                break

            if self.user.field.count == len(layout):  # счетчик потопленных кораблей
                print_fields()
                print("────" + "─" * 9 * g.size)
                print("Компьютер выиграл!")
                print(f'Компьютер потопил все {len(layout)} ваших кораблей')
                break
            num += 1

    def start(self):
        self.greeting()
        self.loop()


class Player:
    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите координаты хода ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, g.size - 1), random.randint(0, g.size - 1))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class Field:
    def __init__(self, hid=False, size=9):
        self.size = (size if size <= 9 else 9)
        self.hid = hid
        self.count = 0
        self.busy = []
        self.ships = []
        self.fld = [[" "] * self.size for _ in range(self.size)]

    def __str__(self):
        res = '  │'
        for i in range(self.size):
            res += f' {i + 1} │'
        for i, row in enumerate(self.fld):
            res += f'\n{i + 1} │ ' + ' │ '.join(row) + ' │'
        if self.hid:
            res = res.replace("█", " ")
        return res

    def output(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):

        for d in ship.dots:
            if self.output(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.fld[d.x][d.y] = "█"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.output(cur)) and cur not in self.busy:
                    if verb:
                        self.fld[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def shot(self, d):
        if self.output(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.fld[d.x][d.y] = "╳"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.fld[d.x][d.y] = "•"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []
    # def add_ship(self, ship):


class Ship:
    def __init__(self, rotation, lenght, o):
        self.rotation = rotation
        self.lenght = lenght
        self.o = o
        self.lives = lenght

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.lenght):
            cur_x = self.rotation.x
            cur_y = self.rotation.y
            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы игрового поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Сюда уже стреляли"


class BoardWrongShipException(BoardException):
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    layout = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # раскладка кораблей
    g = Game(size=9)  # Инициализируем игру с указанным резмером поля
    g.start()
