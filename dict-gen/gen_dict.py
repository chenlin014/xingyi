import json, csv, argparse, sys, re

ACTIONS = {
    '0': (),
    '1': ('+1',),
    '2': ('0',),
    '3': ('+1', '0'),
    '4': ('-1',),
    '5': ('0', '-1'),
    'tk': {
        'a': (2,),
        'b': (1,),
        'c': (2, 1),
        'd': (0,),
        'e': (1, 0)
    }
}

def trans_chord_map(cm, km, acts):
    new_cm = dict()
    last_col = len(km['0']) - 1
    last_tk_col = len(km['thumb_keys']) - 1
    for zg, ma in cm:
        lstroke = ''.join(''.join(km[row][col] for row in acts[act])
            for col, act in enumerate(ma) if act in acts)
        rstroke = ''.join(''.join(km[row][last_col-col] for row in acts[act])
            for col, act in enumerate(ma) if act in acts)

        for act in ma:
            if act in acts['tk']:
                lstroke += ''.join(km['thumb_keys'][col] for col in acts['tk'][act])
                rstroke += ''.join(km['thumb_keys'][last_tk_col-col] for col in acts['tk'][act])

        new_cm[zg] = (lstroke, rstroke)

    return new_cm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('chordmap', help='字根并击表')
    parser.add_argument('keymap', help='键盘布局')
    parser.add_argument('mb_path', help='码表')
    parser.add_argument('-pt', '--priority_table', default=None)
    args = parser.parse_args()

    with open(args.keymap) as f:
        km = json.loads(f.read())

    uniquifier = ['', km["dup_key"], km["func_key"], km["dup_key"]+km["func_key"]]

    with open(args.chordmap) as f:
        reader = csv.reader(f, delimiter='\t')
        chord_map = [(zg, ma) for zg, ma in reader]
    chord_map = trans_chord_map(chord_map, km, ACTIONS)

    with open(args.mb_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        mb = {zi:ma for zi, ma in reader}
    codes = set(mb.values())

    if args.priority_table:
        with open(args.priority_table, encoding='utf_8') as f:
            reader = csv.reader(f, delimiter='\t')
            char_priority = {code: chars for code, chars in reader}
    else:
        char_priority = dict()

    for zi, ma in mb.items():
        if re.match(r'\{.+\}', ma):
            chords = {i:chord for i, chord in enumerate(ma[1:-1].split(','))}
            chords = trans_chord_map(chords.items(), km, ACTIONS)
            chords = [chords[i][i%2] for i in range(len(strokes))]
            ma = ''
        else:
            chords = []

        for i, code in enumerate(ma):
            if code == '空':
                chords.append('')
            elif code == '重':
                chords[-1] += km['dup_key']
            elif code == '能':
                chords[-1] += km['func_key']
            else:
                chords.append(chord_map[code][i%2])

        if ma in char_priority:
            try:
                ind = char_priority[ma].index(zi)
                chords[-1] += uniquifier[ind]
            except Exception as e:
                print(f'\n{zi}\t{ma}')
                raise e

        strokes = [(lchord, rchord)
            for lchord, rchord in zip(chords[::2], chords[1::2])]
        if len(chords) == 2 and all(chords) and not chords[-1][-1] in (km['dup_key'], km['func_key']):
            chords.append(chord_map['完'][0])

        if len(chords) % 2 == 1:
            strokes.append((chords[-1],))

        print(f'{zi}\t{" | ".join("<>".join(stroke) for stroke in strokes)}')

if __name__ == '__main__':
    main()
