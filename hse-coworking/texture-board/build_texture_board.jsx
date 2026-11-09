// Текстурная доска — сборка в Photoshop.
// Файл → Сценарии → Обзор… → выбрать этот файл. Папка layers/ должна лежать рядом.
#target photoshop
app.bringToFront();
(function () {
var SPEC = {
 "width": 3508,
 "height": 2480,
 "resolution": 300,
 "background": "#FFFFFF",
 "images": [
  {
   "group": "01 Лепнина",
   "name": "Тень",
   "file": "swatch-01-shadow.png",
   "x": 1126,
   "y": 396,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "01 Лепнина",
   "name": "Образец — Лепнина",
   "file": "swatch-01.png",
   "x": 1216,
   "y": 470,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Тень",
   "file": "swatch-02-shadow.png",
   "x": 1670,
   "y": 396,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Образец — Лиловое стекло",
   "file": "swatch-02.png",
   "x": 1760,
   "y": 470,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Тень",
   "file": "swatch-03-shadow.png",
   "x": 2214,
   "y": 396,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Образец — Паркет «ёлочка»",
   "file": "swatch-03.png",
   "x": 2304,
   "y": 470,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "04 Бархат",
   "name": "Тень",
   "file": "swatch-04-shadow.png",
   "x": 2758,
   "y": 396,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "04 Бархат",
   "name": "Образец — Бархат",
   "file": "swatch-04.png",
   "x": 2848,
   "y": 470,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "05 Цементная плитка",
   "name": "Тень",
   "file": "swatch-05-shadow.png",
   "x": 1126,
   "y": 1176,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "05 Цементная плитка",
   "name": "Образец — Цементная плитка",
   "file": "swatch-05.png",
   "x": 1216,
   "y": 1250,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "06 Латунь",
   "name": "Тень",
   "file": "swatch-06-shadow.png",
   "x": 1670,
   "y": 1176,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "06 Латунь",
   "name": "Образец — Латунь",
   "file": "swatch-06.png",
   "x": 1760,
   "y": 1250,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "07 Золотая смальта",
   "name": "Тень",
   "file": "swatch-07-shadow.png",
   "x": 2214,
   "y": 1176,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "07 Золотая смальта",
   "name": "Образец — Золотая смальта",
   "file": "swatch-07.png",
   "x": 2304,
   "y": 1250,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "08 Хром",
   "name": "Тень",
   "file": "swatch-08-shadow.png",
   "x": 2758,
   "y": 1176,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "08 Хром",
   "name": "Образец — Хром",
   "file": "swatch-08.png",
   "x": 2848,
   "y": 1250,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  }
 ],
 "texts": [
  {
   "group": "Заголовок",
   "name": "Надзаголовок",
   "lines": [
    "КОВОРКИНГ · ЦЕНТР МОСКВЫ"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 30,
   "color": "#8C8680",
   "x": 200,
   "y": 520,
   "leading": 37,
   "tracking": 180
  },
  {
   "group": "Заголовок",
   "name": "Заголовок",
   "lines": [
    "Текстурная",
    "доска"
   ],
   "font": [
    "CormorantGaramond-Light",
    "CormorantGaramond.ttf",
    300
   ],
   "size": 210,
   "color": "#26252B",
   "x": 200,
   "y": 740,
   "leading": 190,
   "tracking": 0
  },
  {
   "group": "Заголовок",
   "name": "Подводка",
   "lines": [
    "Историческая оболочка — лепнина",
    "и паркет — встречается с цветным",
    "стеклом, бархатом и золотом",
    "советской мозаики."
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 38,
   "color": "#26252B",
   "x": 200,
   "y": 1110,
   "leading": 60,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Палитра — подпись",
   "lines": [
    "ПАЛИТРА"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 28,
   "color": "#8C8680",
   "x": 200,
   "y": 1520,
   "leading": 35,
   "tracking": 180
  },
  {
   "group": "Палитра",
   "name": "Цвет — Тёплый белый",
   "lines": [
    "Тёплый белый"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 200,
   "y": 1761,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Тёплый белый",
   "lines": [
    "#EFE6DC"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 200,
   "y": 1797,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Лиловое стекло",
   "lines": [
    "Лиловое стекло"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 422,
   "y": 1761,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Лиловое стекло",
   "lines": [
    "#B79AC8"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 422,
   "y": 1797,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Медовый дуб",
   "lines": [
    "Медовый дуб"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 644,
   "y": 1761,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Медовый дуб",
   "lines": [
    "#C8976A"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 644,
   "y": 1797,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Горчичный",
   "lines": [
    "Горчичный"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 866,
   "y": 1761,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Горчичный",
   "lines": [
    "#B57E1F"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 866,
   "y": 1797,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Латунь",
   "lines": [
    "Латунь"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 200,
   "y": 2091,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Латунь",
   "lines": [
    "#B08D57"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 200,
   "y": 2127,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Бирюза",
   "lines": [
    "Бирюза"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 422,
   "y": 2091,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Бирюза",
   "lines": [
    "#1F8A93"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 422,
   "y": 2127,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Графит",
   "lines": [
    "Графит"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 644,
   "y": 2091,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Графит",
   "lines": [
    "#3B4046"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 644,
   "y": 2127,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "Цвет — Хром",
   "lines": [
    "Хром"
   ],
   "font": [
    "Inter-Regular",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    null
   ],
   "size": 24,
   "color": "#26252B",
   "x": 866,
   "y": 2091,
   "leading": 30,
   "tracking": 0
  },
  {
   "group": "Палитра",
   "name": "HEX — Хром",
   "lines": [
    "#C4C8CE"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 22,
   "color": "#8C8680",
   "x": 866,
   "y": 2127,
   "leading": 27,
   "tracking": 0
  },
  {
   "group": "01 Лепнина",
   "name": "Номер",
   "lines": [
    "01"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 1216,
   "y": 1034,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "01 Лепнина",
   "name": "Название",
   "lines": [
    "Лепнина"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 1294,
   "y": 1028,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "01 Лепнина",
   "name": "Описание",
   "lines": [
    "гипс, тёплая белая",
    "матовая краска"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 1294,
   "y": 1078,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "01 Лепнина",
   "name": "Зона",
   "lines": [
    "ПОТОЛКИ · КАРНИЗЫ"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 1294,
   "y": 1168,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Номер",
   "lines": [
    "02"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 1760,
   "y": 1034,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Название",
   "lines": [
    "Лиловое стекло"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 1838,
   "y": 1028,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Описание",
   "lines": [
    "рифлёное и гладкое,",
    "тонированное"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 1838,
   "y": 1078,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "02 Лиловое стекло",
   "name": "Зона",
   "lines": [
    "РЕСЕПШЕН · КАБИНЫ"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 1838,
   "y": 1168,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Номер",
   "lines": [
    "03"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 2304,
   "y": 1034,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Название",
   "lines": [
    "Паркет «ёлочка»"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 2382,
   "y": 1028,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Описание",
   "lines": [
    "дуб, медовый тон,",
    "масло"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 2382,
   "y": 1078,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "03 Паркет «ёлочка»",
   "name": "Зона",
   "lines": [
    "РАБОЧАЯ ЗОНА"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 2382,
   "y": 1168,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "04 Бархат",
   "name": "Номер",
   "lines": [
    "04"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 2848,
   "y": 1034,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "04 Бархат",
   "name": "Название",
   "lines": [
    "Бархат"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 2926,
   "y": 1028,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "04 Бархат",
   "name": "Описание",
   "lines": [
    "мохер, горчичный"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 2926,
   "y": 1078,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "04 Бархат",
   "name": "Зона",
   "lines": [
    "КРЕСЛО С ОТТОМАНКОЙ"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 2926,
   "y": 1130,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "05 Цементная плитка",
   "name": "Номер",
   "lines": [
    "05"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 1216,
   "y": 1814,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "05 Цементная плитка",
   "name": "Название",
   "lines": [
    "Цементная плитка"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 1294,
   "y": 1808,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "05 Цементная плитка",
   "name": "Описание",
   "lines": [
    "графит и беж,",
    "диагональ"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 1294,
   "y": 1858,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "05 Цементная плитка",
   "name": "Зона",
   "lines": [
    "МИНИ-КУХНЯ"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 1294,
   "y": 1948,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "06 Латунь",
   "name": "Номер",
   "lines": [
    "06"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 1760,
   "y": 1814,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "06 Латунь",
   "name": "Название",
   "lines": [
    "Латунь"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 1838,
   "y": 1808,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "06 Латунь",
   "name": "Описание",
   "lines": [
    "шлифованная,",
    "тёплый тон"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 1838,
   "y": 1858,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "06 Латунь",
   "name": "Зона",
   "lines": [
    "ДЕТАЛИ · СВЕТ · ПАННО"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 1838,
   "y": 1948,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "07 Золотая смальта",
   "name": "Номер",
   "lines": [
    "07"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 2304,
   "y": 1814,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "07 Золотая смальта",
   "name": "Название",
   "lines": [
    "Золотая смальта"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 2382,
   "y": 1808,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "07 Золотая смальта",
   "name": "Описание",
   "lines": [
    "мозаика в духе",
    "«Новослободской»"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 2382,
   "y": 1858,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "07 Золотая смальта",
   "name": "Зона",
   "lines": [
    "ПАННО"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 2382,
   "y": 1948,
   "leading": 23,
   "tracking": 140
  },
  {
   "group": "08 Хром",
   "name": "Номер",
   "lines": [
    "08"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 64,
   "color": "#7B5A93",
   "x": 2848,
   "y": 1814,
   "leading": 80,
   "tracking": 0
  },
  {
   "group": "08 Хром",
   "name": "Название",
   "lines": [
    "Хром"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 32,
   "color": "#26252B",
   "x": 2926,
   "y": 1808,
   "leading": 40,
   "tracking": 0
  },
  {
   "group": "08 Хром",
   "name": "Описание",
   "lines": [
    "полированная сталь,",
    "зеркальный блеск"
   ],
   "font": [
    "Inter-Light",
    "/usr/share/fonts/opentype/inter/Inter-Light.otf",
    null
   ],
   "size": 26,
   "color": "#26252B",
   "x": 2926,
   "y": 1858,
   "leading": 38,
   "tracking": 0
  },
  {
   "group": "08 Хром",
   "name": "Зона",
   "lines": [
    "РАБОЧИЕ КРЕСЛА"
   ],
   "font": [
    "Inter-Medium",
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    null
   ],
   "size": 19,
   "color": "#8C8680",
   "x": 2926,
   "y": 1948,
   "leading": 23,
   "tracking": 140
  }
 ],
 "circles": [
  {
   "name": "Тёплый белый",
   "hex": "#EFE6DC",
   "cx": 265,
   "cy": 1640,
   "d": 130
  },
  {
   "name": "Лиловое стекло",
   "hex": "#B79AC8",
   "cx": 487,
   "cy": 1640,
   "d": 130
  },
  {
   "name": "Медовый дуб",
   "hex": "#C8976A",
   "cx": 709,
   "cy": 1640,
   "d": 130
  },
  {
   "name": "Горчичный",
   "hex": "#B57E1F",
   "cx": 931,
   "cy": 1640,
   "d": 130
  },
  {
   "name": "Латунь",
   "hex": "#B08D57",
   "cx": 265,
   "cy": 1970,
   "d": 130
  },
  {
   "name": "Бирюза",
   "hex": "#1F8A93",
   "cx": 487,
   "cy": 1970,
   "d": 130
  },
  {
   "name": "Графит",
   "hex": "#3B4046",
   "cx": 709,
   "cy": 1970,
   "d": 130
  },
  {
   "name": "Хром",
   "hex": "#C4C8CE",
   "cx": 931,
   "cy": 1970,
   "d": 130
  }
 ],
 "title": "Текстурная доска"
};
var here = File($.fileName).parent;
var oldRuler = app.preferences.rulerUnits, oldType = app.preferences.typeUnits;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
app.displayDialogs = DialogModes.NO;

function rgb(hex) { var c = new SolidColor(); c.rgb.hexValue = hex.replace('#', ''); return c; }

var doc = app.documents.add(SPEC.width, SPEC.height, SPEC.resolution, SPEC.title,
                            NewDocumentMode.RGB, DocumentFill.WHITE);
doc.artLayers[0].name = 'Фон';

var groups = {};
function group(name) {
  if (!groups[name]) { groups[name] = doc.layerSets.add(); groups[name].name = name; }
  return groups[name];
}

function toSmart() {
  try { executeAction(stringIDToTypeID('newPlacedLayer'), undefined, DialogModes.NO); } catch (e) {}
}

// images
for (var i = 0; i < SPEC.images.length; i++) {
  var e = SPEC.images[i];
  var f = new File(here + '/layers/' + e.file);
  if (!f.exists) { alert('Нет файла: ' + f.fsName); continue; }
  var src = app.open(f);
  var lyr = src.activeLayer.duplicate(doc, ElementPlacement.PLACEATBEGINNING);
  src.close(SaveOptions.DONOTSAVECHANGES);
  app.activeDocument = doc;
  doc.activeLayer = lyr;
  var b = lyr.bounds;
  lyr.translate(e.x - b[0].as('px'), e.y - b[1].as('px'));
  if (e.smart) { toSmart(); lyr = doc.activeLayer; }
  lyr.name = e.name;
  if (e.blend == 'multiply') lyr.blendMode = BlendMode.MULTIPLY;
  lyr.opacity = e.opacity;
  lyr.move(group(e.group), ElementPlacement.PLACEATBEGINNING);
}

// palette circles
for (var i = 0; i < SPEC.circles.length; i++) {
  var c = SPEC.circles[i], r = c.d / 2, pts = [];
  for (var k = 0; k < 96; k++) {
    var a = k / 96 * Math.PI * 2;
    pts.push([c.cx + r * Math.cos(a), c.cy + r * Math.sin(a)]);
  }
  var lyr = doc.artLayers.add();
  lyr.name = 'Круг — ' + c.name;
  doc.selection.select(pts, SelectionType.REPLACE, 0, true);
  doc.selection.fill(rgb(c.hex));
  doc.selection.deselect();
  lyr.move(group('Палитра'), ElementPlacement.PLACEATBEGINNING);
}

// text layers (point text; lines split with \r)
var missingFonts = {};
for (var i = 0; i < SPEC.texts.length; i++) {
  var t = SPEC.texts[i];
  var lyr = doc.artLayers.add();
  lyr.kind = LayerKind.TEXT;
  lyr.name = t.name;
  var ti = lyr.textItem;
  ti.contents = t.lines.join('\r');
  try { ti.font = t.font[0]; } catch (err) { missingFonts[t.font[0]] = 1; }
  ti.size = t.size;
  ti.color = rgb(t.color);
  ti.useAutoLeading = false;
  ti.leading = t.leading;
  ti.tracking = t.tracking;
  ti.position = [t.x, t.y];
  lyr.move(group(t.group), ElementPlacement.PLACEATBEGINNING);
}

app.preferences.rulerUnits = oldRuler;
app.preferences.typeUnits = oldType;
var mf = []; for (var k in missingFonts) mf.push(k);
if (mf.length) alert('Не найдены шрифты: ' + mf.join(', ') + '\nУстановите Cormorant Garamond и Inter из папки fonts и запустите заново.');
})();
