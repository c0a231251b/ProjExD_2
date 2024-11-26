import os
import math
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA={
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,+5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(+5,0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct:pg.Rect) -> tuple[bool,bool]:

    """
    引数で与えられたRectが画面の中か外か判定する
    引数:こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（縦、横）/画面内:True、画面外Flase

    """
    yoko,tate=True,True
    if rct.left < 0 or WIDTH < rct.right:
        yoko =False 
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate=False
    return yoko,tate


#演習課題1
def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に，半透明の黒い画面上に「Game Over」と表示し，
    両側に泣いているこうかとん画像を貼り付ける関数
    """
    # 半透明の黒い画面を描画
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)  # 半透明
    screen.blit(overlay, (0, 0))

    # 泣いているこうかとん画像
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    crying_kk_left_rct = crying_kk_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))
    crying_kk_right_rct = crying_kk_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))
    screen.blit(crying_kk_img, crying_kk_left_rct)
    screen.blit(crying_kk_img, crying_kk_right_rct)

    # "Game Over" テキスト
    fonto = pg.font.Font(None, 80)  # フォント設定
    txt = fonto.render("Game Over", True, (255, 255, 255))  # 白色で描画
    screen.blit(txt, [WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2])  # 中央揃え

    pg.display.update()  # 描画内容を更新
    time.sleep(5)  # 5秒間表示


#演習課題2
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    """
    bb_imgs = []  # 爆弾の画像リスト
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)  # サイズ変更
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)  # 爆弾描画
        bb_imgs.append(bb_img)
    accs = [a for a in range(1, 11)]  # 加速度リスト
    return bb_imgs, accs


#演習課題3
def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:        
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す。
    """
    kk_base_img = pg.image.load("fig/3.png")
    kk_images = {
        #こうかとん変更
        (-5, 0): pg.transform.rotozoom(kk_base_img, 0, 0.9),
        (-5, 5): pg.transform.rotozoom(kk_base_img, 45, 0.9),
        (0, 5): pg.transform.rotozoom(kk_base_img, 90, 0.9),
        (5, 5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), -45, 0.9),
        (5, 0): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), 0, 0.9),
        (5, -5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), 45, 0.9),
        (0, -5): pg.transform.rotozoom(kk_base_img, -90, 0.9),
        (-5, -5): pg.transform.rotozoom(kk_base_img, -45, 0.9),
        (0, 0): pg.transform.rotozoom(kk_base_img, 0, 0.9),  
    }
    return kk_images.get(sum_mv, kk_images[(0, 0)])


#演習課題4
import math

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    orgから見てdstがどの方向にあるかを計算し、移動方向ベクトルを返す。
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery
    distance = math.sqrt(dx**2 + dy**2)

    if distance < 300:  # 近づきすぎたら慣性を維持
        return current_xy

    # 正規化してノルムを√50にする
    norm = math.sqrt(50) / distance
    return dx * norm, dy * norm


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg") 
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface(((20,20))) #爆弾用のsurface
    pg.draw.circle(bb_img,(255,0,0),(10,10),10) #爆弾円を描く
    bb_img.set_colorkey((0,0,0)) #四隅の黒を透過させる
    bb_rct = bb_img.get_rect() #爆弾円rectの抽出
    bb_rct.center=random.randint(0,WIDTH),random.randint(0,HEIGHT)
    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾画像と加速度リストを取得
    bb_img = bb_imgs[0]  # 初期爆弾画像
    vx,vy=+2,+2 #爆弾速度ベクトル 確認の際に臨機に変更
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return #ゲームオーバー
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key,tpl in DELTA.items():
            if key_lst[key]==True:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        
        kk_img=get_kk_img(tuple(sum_mv))

        
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct)!=(True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾のサイズと加速の更新
        idx = min(tmr // 500, 9)  # 時間に応じて段階を選択（最大9）
        avx = vx * bb_accs[idx]  # 加速度適用
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]  # サイズ更新

        # 爆弾の追従計算
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        bb_rct.move_ip(vx, vy)




        bb_rct.move_ip(vx,vy) #爆弾動く
        bb_rct.move_ip(avx,avy)#爆弾動く
        yoko,tate=check_bound(bb_rct)
        if not yoko:
            vx*=-1
        if not tate:
            vy*=-1
        
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
