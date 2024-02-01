## summary
tusb v12.0.9のスポナー座標列挙および同座標の破壊確認を一括で行うスクリプト  
RTA用  
座標列挙までするので他に何か機能を付け加えていじってもらっていいです  

## how to run
環境はlinuxでもanacondaでも  
anaconda python3.8で動作確認済み  

anacondaの場合 https://qiita.com/ozaki_physics/items/985188feb92570e5b82d を参考に仮想環境をpython=3.8で作って`pip install -r requirements.txt`をする  
```
(base)$ conda create -n tool_tusb_spawner_search python=3.8
(tool_tusb_spawner_search)$ pip install -r requirements.txt
```

### 座標列挙
`config.yml`にダウンロードした直後の`TUSBフォルダ/region/`を指定 絶対パスのがいいかも  
`python run.py`で`config.yml`に書いた`output_txt`名の座標列挙txtが出力されるはず  
`v12.0.9`の全座標は`spawners_pos.txt`に生成済みです(岩盤6個、バグで消える2個を含めた830座標)

## 完走判定
`config.yml`に完走したりなんかしたフォルダのパスを`region/`まで含めて書いて  
`python fin.py`で実行  
完走してればログにそうでるし、残ってたら座標と残り数が出る  

