#!/usr/bin/env python3
"""Сборка сайта ТММ из сохранённой версии артефакта.
Запуск: python3 tools/build_site.py <файл артефакта .html> <номер версии>
Пишет index.html в корень репозитория, обновляет версию кэша в sw.js и version.txt.
Иконки, manifest.webmanifest и sw.js уже лежат в корне репозитория (плоско, без папки icons/).
"""
import os, re, sys

src, ver = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(src, encoding='utf-8').read()
# артефакт хранится в служебной оболочке: берём внутренний документ
i = s.find('<!doctype html>', 10)
if s.lower().startswith('<!doctype html>') and i > 0:
    s = s[i:]
    e = s.rfind('</body></html>')
    s = s[:e].rstrip()
if 'function mkTasks' not in s or len(s) < 100000:
    sys.exit('Это не похоже на приложение ТММ — сборка остановлена')
if '/*TMM-MOBILE v2*/' not in s:
    sys.exit('В версии нет мобильного патча (маркер /*TMM-MOBILE v2*/) — сначала накатить claude/web/patch_mobile.py')
s = s.replace('href="icons/', 'href="')
# Правки для сайта, которые ещё не попали в артефакт (старый текст → новый).
# Если старого текста нет — правка уже в артефакте или код поменялся, сборку это не останавливает.
FIXES = [
    # Яндекс Браузер на iPhone: реальный путь проверен на телефоне владельца 14.10.2026
    ("iya:['iPhone · Яндекс Браузер',['Нажми кнопку меню внизу экрана (☰ или ⋯).','Выбери «Поделиться», затем «На экран „Домой“».','Нажми «Добавить».','Нет такого пункта — открой эту страницу в Safari и добавь оттуда.']],",
     "iya:['iPhone · Яндекс Браузер',['Нажми ⋮ (три точки) справа внизу, в адресной строке.','Выбери «Добавить ярлык на телефон».','Нажми «Добавить на экран „Домой“».','Проверь, что включено «Открыть как веб-приложение», и нажми «Добавить».']],"),
]
for a, b in FIXES:
    if a in s:
        s = s.replace(a, b)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(s)
sw = os.path.join(root, 'sw.js')
w = open(sw, encoding='utf-8').read()
w = re.sub(r"const CACHE = 'tmm-[^']*';", "const CACHE = 'tmm-%s';" % re.sub(r'[^A-Za-z0-9.-]', '', ver), w)
open(sw, 'w', encoding='utf-8').write(w)
open(os.path.join(root, 'version.txt'), 'w').write(ver + '\n')
print('Собрано: версия', ver, ',', len(s), 'символов')
