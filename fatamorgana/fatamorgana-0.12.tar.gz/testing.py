from io import BytesIO
import fatamorgana
failed = []
for i in range(1, 16):
    for j in range(1, 20):
        print(i, j)
        try:
            with open(f'/home/jan/software/layout/klayout-source/testdata/oasis/t{i}.{j}.oas', 'rb') as f:
                a = f.read()
                b = fatamorgana.OasisLayout.read(BytesIO(a[:-253]))
        except FileNotFoundError:
            print('failed to open', i,'.',j)
            break
        except Exception as e:
            failed.append((i, j, e))

        if (i, j) == (9, 2):
            continue

        with open(f'/tmp/t{i}.{j}.oas', 'wb') as f:
            b.write(f)
[print(f) for f in failed]
