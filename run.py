import anvil
import math
from tqdm import tqdm
import yaml


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


# blockのIDを返す なんとなく集計用
def bit_blocks(data, pos):
    bit = ""
    blocks = data["Sections"]
    if len(blocks) == 0:
        return bit
    # print(pos)
    y_pos = math.floor(pos[1] / 16)
    y_block = blocks[y_pos]
    possition = ((pos[1] % 16) * 256) + ((pos[2] % 16) * 16) + ((pos[0] % 16))
    block = y_block["Blocks"][possition]
    return block


def conf_Minecartsp(data):
    # あくまでチャンク毎渡されているから 座標を全部返さないといけない
    res = []
    res2 = []
    if not ("Entities" in list(i for i in data)):
        return res, res2
    entities = data["Entities"]
    if len(entities) == 0:
        return res, res2
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
                res2.append(
                    bit_blocks(
                        data, [math.floor(float(str(pos))) for pos in list(pent["Pos"])]
                    )
                )
    return res, res2


def conf_Mobsp(data):
    res = []
    res2 = []
    if not ("TileEntities" in list(i for i in data)):
        return res, res2
    entities = data["TileEntities"]
    if len(entities) == 0:
        return res, res2
    for entry in entities:
        if not ("id" in list(i for i in entry)):
            continue
        id = str(entry["id"])
        if id == "MobSpawner":
            res.append(
                [int(str(entry["x"])), int(str(entry["y"])), int(str(entry["z"]))]
            )
            res2.append(
                bit_blocks(
                    data,
                    [int(str(entry["x"])), int(str(entry["y"])), int(str(entry["z"]))],
                )
            )
    return res, res2


def main(source_path, output_path):
    range_chunk = [[-12, -12], [18, 14]]  # 通常世界のチャンクをforで全部見る
    posses = []
    posses_mob = []
    posses_car = []
    for chx in tqdm(list(range(range_chunk[0][0], range_chunk[1][0]))):
        for chy in list(range(range_chunk[0][1], range_chunk[1][1])):
            region = anvil.Region.from_file(source_path + sel_mca(chx, chy))
            ccx, ccy = chunk_chander(chx, chy)
            chunk = anvil.Chunk.from_region(region, ccx, ccy)
            # print(sel_mca(chx,chy) , '  : ',ccx,' ',ccy)
            data = chunk.data
            # マインカートスポナーを保持
            mcartsp, tmp1 = conf_Minecartsp(data)
            for val in mcartsp:
                posses.append(val)
            for val in tmp1:
                posses_car.append(val)
            # MOBスポナーを保持
            mcdefsp, tmp2 = conf_Mobsp(data)
            for val in mcdefsp:
                posses.append(val)
            for val in tmp2:
                posses_mob.append(val)

    n = len(posses)

    # # {ID: num}でスポナー種別を表print
    # dic = dict()
    # for bit in posses_car:
    #     if not bit in dic:
    #         dic[bit] = 0
    #     dic[bit] += 1
    # for bit in posses_mob:
    #     if not bit in dic:
    #         dic[bit] = 0
    #     dic[bit] += 1
    # for key in dic:
    #     print("{", key, ": ", dic[key], "}")

    # MOBスポナーとマインカートスポナーの重複削除
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

    with open(output_path, mode="w") as f:
        for d in ans:
            f.write(str(d[0]))
            f.write(" ")
            f.write(str(d[1]))
            f.write(" ")
            f.write(str(d[2]))
            f.write("\n")
    print("spawner:", len(ans))


if __name__ == "__main__":
    with open("config.yml", "r", encoding="utf-8_sig") as yml:
        config = yaml.safe_load(yml)
    source_path = config["run"]["source"]
    output_path = config["run"]["output_txt"]
    main(source_path, output_path)
