import datetime
import hashlib
import os

chksum_filename = '.chksum'


def sha256sum(file_path):
    hash = hashlib.sha256()
    with open(file_path, mode='rb') as f:
        while True:
            data = f.read(128 * 1024)
            if not data:
                # Done
                break
            hash.update(data)
    return hash.hexdigest()


def retrieve_file_properties(file_path):
    file_stats = os.stat(file_path)
    file_size = file_stats.st_size
    file_mtime_datetime = datetime.datetime.fromtimestamp(file_stats.st_mtime, datetime.timezone.utc)
    file_mtime_datetime_str = file_mtime_datetime.isoformat()

    file_sha256sum = sha256sum(file_path)
    file_name = os.path.basename(file_path)
    return file_size, file_mtime_datetime_str, file_sha256sum


def generate_chksum_contents(root, dir_names, file_names):
    contents = []
    for dir_name in dir_names:
        contents.append({
            'type': 'directory',
            'name': dir_name
        })
    for file_name in file_names:
        if file_name == chksum_filename:
            continue
        file_path = os.path.join(root, file_name)
        try:
            file_size, file_mtime_datetime_str, file_sha256sum = retrieve_file_properties(file_path=file_path)
            contents.append({
                'type': 'file',
                'name': file_name,
                'size': file_size,
                'mtime': file_mtime_datetime_str,
                'sha256sum': file_sha256sum
            })
        except FileNotFoundError as ex:
            # Example: Unable to read K:\CAMERA\TO_BE_SORTED_2017\201710\macbook pro retina\20171019 - Transfer data from Mom iPhone 6 Plus into 6S\Transfer content from your previous iOS device to your new iPhone, iPad, or iPod touch - Apple Support_files\._iphone7-ios11-home-setup-new-iphone-quick-start.jpg: [WinError 3] The system cannot find the path specified: 'K:\\CAMERA\\TO_BE_SORTED_2017\\201710\\macbook pro retina\\20171019 - Transfer data from Mom iPhone 6 Plus into 6S\\Transfer content from your previous iOS device to your new iPhone, iPad, or iPod touch - Apple Support_files\\._iphone7-ios11-home-setup-new-iphone-quick-start.jpg'
            print(f'Unable to read {file_path}: {ex}')
        except OSError as ex:
            # Example: Unable to read C:\Users\admin\AppData\Local\Microsoft\WindowsApps\Spotify.exe: [WinError 1920] The file cannot be accessed by the system: 'C:\\Users\\admin\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe'
            print(f'Unable to read {file_path}: {ex}')
    return contents


def read_chksum_file(chksum_path):
    contents = []
    with open(chksum_path, mode='rt', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            rows = line.split('*')
            if rows[0] == 'd':
                contents.append({
                    'type': 'directory',
                    'name': rows[1]
                })
                pass
            elif rows[0] == 'f':
                contents.append({
                    'type': 'file',
                    'name': rows[1],
                    'size': int(rows[2]),
                    'mtime': rows[3],
                    'sha256sum': rows[4]
                })
            else:
                raise Exception(f'Unsupported content type {rows[0]}')
    return contents


def write_chksum_file(chksum_contents, chksum_path):
    try:
        with open(chksum_path, mode='wt', encoding='utf-8') as f:
            for chksum_content in chksum_contents:
                if chksum_content['type'] == 'directory':
                    line = f'd*{chksum_content["name"]}'
                elif chksum_content['type'] == 'file':
                    line = f'f*{chksum_content["name"]}*{chksum_content["size"]}*{chksum_content["mtime"]}*{chksum_content["sha256sum"]}'
                else:
                    raise Exception(f'Unsupported content type {chksum_content["type"]}')
                f.write(line + '\n')
    except PermissionError as ex:
        # Example: Unable to write checksum file C:\.chksum: [Errno 13] Permission denied: 'C:\\.chksum'
        print(f'Unable to write checksum file {chksum_path}: {ex}')


def report_diff(log_file, root, past_contents, current_contents):
    past_contents = {content['name']: content for content in past_contents}
    current_contents = {content['name']: content for content in current_contents}
    for name in sorted(set(current_contents.keys()) - set(past_contents.keys())):
        log_file.write(f'{root}: Added: {current_contents[name]}\n')
    for name in sorted(set(past_contents.keys()) - set(current_contents.keys())):
        log_file.write(f'{root}: Deleted: {past_contents[name]}\n')
    for name in sorted(set(past_contents.keys()) & set(current_contents.keys())):
        if past_contents[name] != current_contents[name]:
            log_file.write(f'{root}: Changed: {past_contents[name]}   ->   {current_contents[name]}\n')


def main():
    excluded_dir_names = ['$RECYCLE.BIN', 'found.000', 'Recovery', 'System Volume Information']
    datetime_now = datetime.datetime.now()
    log_filename = 'chksum_' + datetime_now.strftime("%Y%m%d_%H%M%S") + '.log'
    print(f'Writing detailed log into {log_filename}...')
    with open(log_filename, mode='wt', encoding='utf-8') as log_file:
        for root, dir_names, file_names in os.walk(os.getcwd()):
            dir_names[:] = [dir_name for dir_name in dir_names if dir_name not in excluded_dir_names]
            try:
                # In Windows when redirecting STDOUT into a file, sometimes printing throws following error "UnicodeEncodeError: 'charmap' codec can't encode characters in position 138-141: character maps to <undefined>"
                log_file.write(f'Processing {root}\n')
                log_file.flush()
                chksum_path = os.path.join(root, chksum_filename)
                if os.path.exists(chksum_path):
                    past_chksum_contents = read_chksum_file(chksum_path=chksum_path)
                else:
                    past_chksum_contents = []
                current_chksum_contents = generate_chksum_contents(root, dir_names, file_names)
                if current_chksum_contents != past_chksum_contents:
                    report_diff(log_file, root, past_chksum_contents, current_chksum_contents)
                    write_chksum_file(chksum_contents=current_chksum_contents, chksum_path=chksum_path)
            except Exception as e:
                print(f'Error while processing: {e}')


main()
