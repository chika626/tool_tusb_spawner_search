import anvil
import math
from tqdm import tqdm
import yaml
import os


def sel_mca(chx, chy):
    if chx < 0 and chy < 0:
        return "r.-1.-1.mca"
    elif chx < 0 and chy >= 0:
        return "r.-1.0.mca"
    elif chx >= 0 and chy < 0:
        return "r.0.-1.mca"
    else:
        return "r.0.0.mca"


def chunk_chander(chx, chy):
    if chx < 0 and chy < 0:
        return (32 + chx, 32 + chy)
    elif chx < 0 and chy >= 0:
        return (32 + chx, chy)
    elif chx >= 0 and chy < 0:
        return (chx, 32 + chy)
    else:
        return (chx, chy)


def conf_Minecartsp(data):
    # あくまでチャンク毎渡されているから 座標を全部返さないといけない
    res = []
    if not ("Entities" in list(i for i in data)):
        return res
    entities = data["Entities"]
    if len(entities) == 0:
        return res
    for entry in entities:
        if not ("Passengers" in list(i for i in entry)):
            continue
        passengers = entry["Passengers"]
        if len(passengers) == 0:
            continue
        for pent in passengers:
            if not ("id" in list(i for i in pent)):
                continue
            id = str(pent["id"])
            if id == "MinecartSpawner":
                # 座標を確認する必要がある
                res.append([math.floor(float(str(pos))) for pos in list(pent["Pos"])])
    return res


def conf_Mobsp(data):
    res = []
    if not ("TileEntities" in list(i for i in data)):
        return res
    entities = data["TileEntities"]
    if len(entities) == 0:
        return res
    for entry in entities:
        if not ("id" in list(i for i in entry)):
            continue
        id = str(entry["id"])
        if id == "MobSpawner":
            res.append(
                [int(str(entry["x"])), int(str(entry["y"])), int(str(entry["z"]))]
            )
    return res


def main(source, spawners_txt):
    assert os.path.exists(
        spawners_txt
    ), f"{spawners_txt}が存在しません run.pyを実行して生成するか、config.ymlを確認してください"
    # 確認用の座標を全列挙
    def_sp = []
    with open(spawners_txt) as f:
        l = f.readlines()
        for pos in l:
            x, y, z = pos.split(" ")
            def_sp.append([int(x), int(y), int(z)])

    range_chunk = [[-12, -12], [18, 14]]
    posses = []
    for chx in tqdm(list(range(range_chunk[0][0], range_chunk[1][0]))):
        for chy in list(range(range_chunk[0][1], range_chunk[1][1])):
            region = anvil.Region.from_file(source + sel_mca(chx, chy))
            ccx, ccy = chunk_chander(chx, chy)
            chunk = anvil.Chunk.from_region(region, ccx, ccy)
            # print(sel_mca(chx,chy) , '  : ',ccx,' ',ccy)
            data = chunk.data
            mcartsp = conf_Minecartsp(data)
            mcdefsp = conf_Mobsp(data)
            for val in mcartsp:
                posses.append(val)
            for val in mcdefsp:
                posses.append(val)

    # 重複削除
    n = len(posses)
    ans = []
    for i in range(n - 1):
        iok = True
        for j in range((i + 1), n):
            x1, y1, z1 = posses[i]
            x2, y2, z2 = posses[j]
            if x1 == x2 and y1 == y2 and z1 == z2:
                iok = False
        if iok:
            ans.append(posses[i])
    ans.append(posses[n - 1])

    # spawners_txtを見て、ansに存在しないなら壊せている証
    n = len(def_sp)
    # 岩盤座標を無視するためlocalで作っておく
    bbpos = [
        [-95, 174, -151],
        [-10, 134, -60],
        [-6, 134, -64],
        [-2, 134, -60],
        [-6, 134, -56],
        [191, 141, 171],
    ]
    nokori = []
    for x1, y1, z1 in def_sp:
        nai = True
        for x2, y2, z2 in ans:
            if x1 == x2 and y1 == y2 and z1 == z2:
                # 完全一致の場合、どこかに残りがあるということ
                nai = False
                for bx, by, bz in bbpos:  # 岩盤座標ならスルーする
                    if x1 == bx and y1 == by and z1 == bz:
                        # スルーしていい
                        nai = True
        if not nai:
            nokori.append([x1, y1, z1])  # お残りを保持
    if len(nokori) == 0:
        print("完走！！")
    else:
        for x1, y1, z1 in nokori:
            print(x1, " ", y1, " ", z1)
        print("お残り : ", len(nokori))


if __name__ == "__main__":
    with open("config.yml", "r", encoding="utf-8_sig") as yml:
        config = yaml.safe_load(yml)
    source = config["fin"]["source"]
    spawners_txt = config["fin"]["spawners_txt"]
    main(source, spawners_txt)
