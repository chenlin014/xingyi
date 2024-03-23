import sys, json, csv

def trans_chord_map(cm, km):
    new_cm = dict()
    for zg, ma in cm:
        lstroke = ''
        rstroke = ''

        for col, act in enumerate(ma):
            if act == '0':
                continue
            elif act == '1':
                lstroke += km[0][col]
                rstroke += km[0][7-col]
            elif act == '2':
                lstroke += km[1][col]
                rstroke += km[1][7-col]
            else:
                lstroke += km[0][col] + km[1][col]
                rstroke += km[0][7-col] + km[1][7-col]

        new_cm[zg] = (lstroke, rstroke)

    return new_cm

def main():
    if len(sys.argv) < 4:
        print(f'Usage: {sys.argv[0]} <字根并击表> <键盘布局> <拆字表>')
        quit()
    _, chord_map_path, keymap_path, mb_path = sys.argv

    with open(keymap_path) as f:
        km = json.loads(f.read())

    with open(chord_map_path) as f:
        reader = csv.reader(f, delimiter='\t')
        chord_map = [(zg, ma) for zg, ma in reader]
    chord_map = trans_chord_map(chord_map, km)

    with open(mb_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        mb = {zi:ma for zi, ma in reader}
    codes = set(mb.values())

    suffix_code = {
        '左':'D',
        '下':'V',
        '重':km[2][2],
        '能':km[2][3],
        '正':'Z',
        '简':'J',
        '和':'W',
        '喃':'N',
        '韩':'H'
    }

    for zi, ma in mb.items():
        stroke = ''
        for i, code in enumerate(ma):
            if code in suffix_code:
                stroke += suffix_code[code]
                continue

            stroke += chord_map[code][i%2]

        if ma + '简' in codes:
            stroke += suffix_code['正']
        if ma + '正' in codes:
            stroke += suffix_code['简']

        print(f'{zi}\t{stroke}')

if __name__ == '__main__':
    main()
