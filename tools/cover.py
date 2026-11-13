# Обложки для материалов редакции VAYN SIY (1200x630, для ленты и превью в Telegram/WhatsApp).
# Запуск из корня репозитория:  python3 tools/cover.py
# Делает covers/<slug>.jpg для всех материалов без своей фотографии и прописывает поле "cover".
# Уже существующие обложки не трогает (пересоздать одну: python3 tools/cover.py --force <slug>).
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
W, HH = 1200, 630
BONE, GOLD, GOLD2, DIM = (237, 231, 218), (201, 162, 39), (232, 199, 90), (160, 152, 136)
RUB = {'ichkeriya': ('ИЧКЕРИЯ И ПОЛИТИКА', '#C9A227'), 'diaspora-pravo': ('ДИАСПОРА И ПРАВО', '#5b84a8'), 'pamyat': ('VAYNA DAGAẊ DU', '#8a9a4a'),
       'imperskiy-test': ('ИМПЕРСКИЙ ТЕСТ', '#b8243a'), 'novosti': ('НОВОСТИ И АКЦИИ', '#d0502f'), 'mott': ('NOXÇIYŊ MOTT', '#3d9a5c'),
       'geopolitika': ('ГЕОПОЛИТИКА', '#7a5cc4'), 'video': ('ВИДЕО', '#e53935')}
REG = {'ukraina': 'УКРАИНА', 'kavkaz': 'КАВКАЗ', 'evropa': 'ЕВРОПА', 'gaza': 'ГАЗА'}
F = lambda n, s: ImageFont.truetype(f'{H}/fonts/{n}.ttf', s)
hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def wrap(d, text, font, width):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def make(a, out):
    im = Image.new('RGB', (W, HH))
    # фон: тёмно-зелёный -> бордовый, как у общей обложки сайта
    g = Image.linear_gradient('L').rotate(90).resize((W, HH))
    im = Image.composite(Image.new('RGB', (W, HH), (58, 18, 24)), Image.new('RGB', (W, HH), (10, 18, 14)), g)
    orn = Image.open(f'{H}/ornament.webp').convert('RGBA')
    orn = orn.resize((int(orn.width * HH / orn.height), HH))
    alpha = orn.split()[3].point(lambda v: int(v * .16))
    for x in range(W - orn.width * 2, W, orn.width): im.paste(orn, (x, 0), alpha)
    # затемнение под текстом
    sh = Image.new('L', (W, HH), 0); ImageDraw.Draw(sh).rectangle([0, 0, 900, HH], fill=150)
    im = Image.composite(Image.new('RGB', (W, HH), (8, 12, 10)), im, sh.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(im)
    rt, rc = RUB.get(a.get('rubric'), ('VAYN SIY', '#C9A227'))
    col = hexrgb(rc)
    # эмблема слева
    em = Image.open(f'{H}/emblem.png').convert('RGBA'); em.thumbnail((150, 260))
    im.paste(em, (64, (HH - em.height) // 2 - 10), em)
    X, TW = 270, W - 270 - 70
    # строка раздела
    label = rt + (f'  ·  {REG[a["region"]]}' if a.get('region') in REG else '')
    d.rectangle([X, 92, X + 46, 96], fill=col)
    d.text((X + 62, 80), label, font=F('plex-mono-500', 24), fill=GOLD2)
    # заголовок: подбираем размер, чтобы влез в 4 строки
    title = a.get('title', '').strip()
    for size in (74, 68, 62, 56, 50, 46):
        ft = F('cormorant-700', size); lines = wrap(d, title, ft, TW)
        if len(lines) <= 4: break
    lines = lines[:4]
    lh = int(size * 1.08); y = 140
    for ln in lines: d.text((X, y), ln, font=ft, fill=BONE); y += lh
    # чеченская строка
    sub = (a.get('sub') or '').strip()
    if sub:
        fs = F('cormorant-600i', 36); sl = wrap(d, sub, fs, TW)[:1]
        d.text((X, y + 18), sl[0], font=fs, fill=GOLD)
    # низ: знак и адрес
    wm = Image.open(f'{H}/wordmark.png').convert('RGBA'); wm.thumbnail((230, 40))
    im.paste(wm, (X, HH - 70 - wm.height // 2), wm)
    d.text((W - 70, HH - 70), 'vaynsiy.com', font=F('plex-mono-500', 22), fill=DIM, anchor='rm')
    d.rectangle([0, HH - 8, W, HH], fill=col)
    im.save(out, 'JPEG', quality=84, optimize=True, progressive=True)


def main():
    force = sys.argv[2:] if len(sys.argv) > 2 and sys.argv[1] == '--force' else []
    p = f'{ROOT}/articles.json'; data = json.load(open(p, encoding='utf-8'))
    os.makedirs(f'{ROOT}/covers', exist_ok=True)
    n = 0
    for a in data['articles']:
        if a.get('image'): continue
        slug = a['slug']; out = f'{ROOT}/covers/{slug}.jpg'
        if not os.path.exists(out) or slug in force: make(a, out); n += 1
        a['cover'] = f'/covers/{slug}.jpg'
    with open(p, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=1)
    print('обложек сделано:', n)


if __name__ == '__main__':
    main()
