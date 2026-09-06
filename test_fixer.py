import os, tempfile
from PIL import Image
import fixer

def test_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        src, ref, dst = (os.path.join(d, n) for n in ('out', 'ref', 'site'))
        os.makedirs(src); os.makedirs(ref)
        Image.new('RGBA', (1500, 1700)).save(f'{src}/＃球体化 コアフォルダ単体_7(ナナ)-1.png')
        Image.new('RGBA', (1000, 1000)).save(f'{src}/＃球体化 コアフォルダ単体_ゼフィア-1.png')  # 圧縮版なし → 中央値倍率
        Image.new('P', (400, 453)).save(f'{ref}/emstk_corefolder7-1.png')
        fixer.run(src, ref, dst)
        a = Image.open(f'{dst}/＃球体化 コアフォルダ単体_7(ナナ)-1.png')
        b = Image.open(f'{dst}/＃球体化 コアフォルダ単体_ゼフィア-1.png')
        assert a.size == (1300, 1473) and a.mode == 'P', a.size      # 400*3.25 = 1300
        assert b.size == (867, 867), b.size                           # 1000 * (1300/1500)

if __name__ == '__main__':
    test_roundtrip(); print('ok')
