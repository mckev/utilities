""" Report directories which have largest number of files """

import os


def main():
    excluded_dir_names = ['$RECYCLE.BIN', 'found.000', 'Recovery', 'System Volume Information']
    num_files = {}
    for root, dir_names, file_names in os.walk(os.getcwd()):
        dir_names[:] = [dir_name for dir_name in dir_names if dir_name not in excluded_dir_names]
        # print(f'Processing {root}')
        num_files[root] = len(file_names)

    print()
    print('Directories with most files:')
    for root in sorted(num_files, key=lambda k: num_files[k], reverse=True)[:30]:
        print(f'{root}: {num_files[root]} files')


main()
