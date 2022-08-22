from sonusai.mixture import load_mixdb


def main():
    name = '/opt/Aaware/sonusai/scratch/eval1medium2'

    j_mixdb = load_mixdb(name + '.json')
    print(f'{len(j_mixdb.mixtures)} mixtures')

    h_mixdb = load_mixdb(name + '.h5')

    with open('/opt/Aaware/sonusai/scratch/j_mixdb.json', 'w') as f:
        f.write(j_mixdb.to_json(indent=2))
    with open('/opt/Aaware/sonusai/scratch/h_mixdb.json', 'w') as f:
        f.write(h_mixdb.to_json(indent=2))


if __name__ == '__main__':
    main()
