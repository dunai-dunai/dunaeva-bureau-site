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
   "group": "Фон",
   "name": "Фон — молочная штукатурка",
   "file": "00-background.png",
   "x": 0,
   "y": 0,
   "blend": "normal",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "01 Лепнина",
   "name": "Тень",
   "file": "01-Лепнина-тень.png",
   "x": 173,
   "y": 379,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "01 Лепнина",
   "name": "Образец — Лепнина",
   "file": "01-Лепнина-образец.png",
   "x": 232,
   "y": 431,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "02 Паркет",
   "name": "Тень",
   "file": "02-Паркет-тень.png",
   "x": 1099,
   "y": 195,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "02 Паркет",
   "name": "Образец — Паркет",
   "file": "02-Паркет-образец.png",
   "x": 1150,
   "y": 230,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "03 Цементная плитка",
   "name": "Тень",
   "file": "03-Цементная плитка-тень.png",
   "x": 1990,
   "y": 212,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "03 Цементная плитка",
   "name": "Образец — Цементная плитка",
   "file": "03-Цементная плитка-образец.png",
   "x": 2052,
   "y": 262,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "04 Бархат",
   "name": "Тень",
   "file": "04-Бархат-тень.png",
   "x": 230,
   "y": 959,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "04 Бархат",
   "name": "Образец — Бархат",
   "file": "04-Бархат-образец.png",
   "x": 280,
   "y": 1001,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "05 Золотая смальта",
   "name": "Тень",
   "file": "05-Золотая смальта-тень.png",
   "x": 1152,
   "y": 1094,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "05 Золотая смальта",
   "name": "Образец — Золотая смальта",
   "file": "05-Золотая смальта-образец.png",
   "x": 1208,
   "y": 1143,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "06 Лиловое стекло",
   "name": "Тень",
   "file": "06-Лиловое стекло-тень.png",
   "x": 2368,
   "y": 522,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "06 Лиловое стекло",
   "name": "Образец — Лиловое стекло",
   "file": "06-Лиловое стекло-образец.png",
   "x": 2422,
   "y": 562,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "07 Бархат в полоску",
   "name": "Тень",
   "file": "07-Бархат в полоску-тень.png",
   "x": 2648,
   "y": 1518,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "07 Бархат в полоску",
   "name": "Образец — Бархат в полоску",
   "file": "07-Бархат в полоску-образец.png",
   "x": 2703,
   "y": 1563,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "08 Ковёр",
   "name": "Тень",
   "file": "08-Ковёр-тень.png",
   "x": 269,
   "y": 1672,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "08 Ковёр",
   "name": "Образец — Ковёр",
   "file": "08-Ковёр-образец.png",
   "x": 332,
   "y": 1721,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "09 Латунь",
   "name": "Тень",
   "file": "09-Латунь-тень.png",
   "x": 1056,
   "y": 1949,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "09 Латунь",
   "name": "Образец — Латунь",
   "file": "09-Латунь-образец.png",
   "x": 1122,
   "y": 2002,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  },
  {
   "group": "10 Зеркальная сталь",
   "name": "Тень",
   "file": "10-Зеркальная сталь-тень.png",
   "x": 1850,
   "y": 1197,
   "blend": "multiply",
   "opacity": 100,
   "smart": false
  },
  {
   "group": "10 Зеркальная сталь",
   "name": "Образец — Зеркальная сталь",
   "file": "10-Зеркальная сталь-образец.png",
   "x": 1900,
   "y": 1240,
   "blend": "normal",
   "opacity": 100,
   "smart": true
  }
 ],
 "texts": [
  {
   "group": "Подписи",
   "name": "лепнина · гипс",
   "lines": [
    "лепнина · гипс"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 252,
   "y": 902,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "паркет · дуб, ёлочка",
   "lines": [
    "паркет · дуб, ёлочка"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 1170,
   "y": 1006,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "плитка · цемент",
   "lines": [
    "плитка · цемент"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 2072,
   "y": 919,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "бархат · мохер, горчичный",
   "lines": [
    "бархат · мохер, горчичный"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 300,
   "y": 1636,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "смальта · золото",
   "lines": [
    "смальта · золото"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 1228,
   "y": 1742,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "стекло · лиловое, рифлёное",
   "lines": [
    "стекло · лиловое, рифлёное"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 2502,
   "y": 1553,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "бархат · чёрный и молочный",
   "lines": [
    "бархат · чёрный и молочный"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 2723,
   "y": 2037,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "ковёр · горчичный ворс",
   "lines": [
    "ковёр · горчичный ворс"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 352,
   "y": 2277,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "латунь",
   "lines": [
    "латунь"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 1142,
   "y": 2293,
   "leading": 56,
   "tracking": 0
  },
  {
   "group": "Подписи",
   "name": "сталь · зеркальная, выбивка",
   "lines": [
    "сталь · зеркальная, выбивка"
   ],
   "font": [
    "CormorantGaramond-Italic",
    "CormorantGaramond-Italic.ttf",
    400
   ],
   "size": 44,
   "color": "#2A2826",
   "x": 1920,
   "y": 1946,
   "leading": 56,
   "tracking": 0
  },
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
   "size": 26,
   "color": "#8A837B",
   "x": 236,
   "y": 200,
   "leading": 32,
   "tracking": 180
  },
  {
   "group": "Заголовок",
   "name": "Заголовок",
   "lines": [
    "Текстурная доска"
   ],
   "font": [
    "CormorantGaramond-Light",
    "CormorantGaramond.ttf",
    300
   ],
   "size": 96,
   "color": "#2A2826",
   "x": 230,
   "y": 320,
   "leading": 100,
   "tracking": 0
  }
 ],
 "circles": [],
 "title": "Текстурная доска v2"
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
