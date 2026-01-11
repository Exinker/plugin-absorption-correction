# ABSORPTIONS-CORRECTION

**ABSORPTIONS-CORRECTION** - плагин для ПО [Атом](https://www.vmk.ru/product/programmnoe_obespechenie/atom.html) для линеаризации аналитического сигнала в спектрах абсорбции.


## Author Information:
Павел Ващенко (vaschenko@vmk.ru)
[ВМК-Оптоэлектроника](https://www.vmk.ru/), г. Новосибирск 2025 г.

## Installation

### Установка Git
Для работы требуется установить Git. *Последнюю версию можно скачать [здесь](https://git-scm.com/downloads/win).*

### Установка Python
Для работы требуется установить Python версии 3.12. *Последнюю версию можно скачать [здесь](https://www.python.org/downloads/).*
Установка зависимостей выполняется с использованием пакетного менеджера `uv`, который можно установить командой: `pip install uv`;

### Установка виртуального окружения
Зависимости, необходимые для работы приложения, необходимо установить в виртуальное окружение `.venv`. Для этого в командной строке необходимо:
1. Зайти в папку с плагинами: `cd ATOM_PATH\Plugins\python`;
2. Клонировать проект с удаленного репозитория: `git clone https://github.com/Exinker/plugin-absorption-correction.git`;
3. Зайти в папку с плагином для расчета формы контура пика: `cd plugin-absorption-correction`;
4. Создать виртуальное окружение и установить необходимые зависимости: `uv sync --no-dev`;

## Usage

### ENV
Преременные окружения плагина:
- `LOGGING_LEVEL: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' = 'INFO'` - уровень логгирования;
