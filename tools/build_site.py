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
# Превью ссылки в мессенджерах и соцсетях (Open Graph) и описание для поисковиков — только для сайта
SITE = 'https://tvoymuzmanager.ru/'
OG_DESC = 'Личный менеджер для артиста: план релиза, контент-план и задачи на каждый день. Помогает выпускать музыку регулярно и расти.'
OG = (
    '<meta name="robots" content="noindex, nofollow">\n'  # закрыто от поиска до запуска; к запуску убрать эту строку
    '<meta name="description" content="%s">\n'
    '<link rel="canonical" href="%s">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:site_name" content="ТММ — Твой Музыкальный Менеджер">\n'
    '<meta property="og:title" content="Твой Музыкальный Менеджер">\n'
    '<meta property="og:description" content="%s">\n'
    '<meta property="og:url" content="%s">\n'
    '<meta property="og:image" content="%sog.jpg?v=2">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta property="og:image:alt" content="ТММ — маскот в наушниках и название приложения">\n'
    '<meta property="og:locale" content="ru_RU">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="twitter:title" content="Твой Музыкальный Менеджер">\n'
    '<meta name="twitter:description" content="%s">\n'
    '<meta name="twitter:image" content="%sog.jpg?v=2">\n'
) % (OG_DESC, SITE, OG_DESC, SITE, SITE, OG_DESC, SITE)
if 'og:title' not in s and '</title>' in s:
    s = s.replace('</title>', '</title>\n' + OG.rstrip('\n'), 1)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(s)
sw = os.path.join(root, 'sw.js')
w = open(sw, encoding='utf-8').read()
w = re.sub(r"const CACHE = 'tmm-[^']*';", "const CACHE = 'tmm-%s';" % re.sub(r'[^A-Za-z0-9.-]', '', ver), w)
open(sw, 'w', encoding='utf-8').write(w)
open(os.path.join(root, 'version.txt'), 'w').write(ver + '\n')
print('Собрано: версия', ver, ',', len(s), 'символов')
