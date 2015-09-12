import subprocess, os, math, sys

def open_with_first_line_skipped(file_path, skip=False):
    f = open(file_path)
    if not skip:
        return f
    next(f)
    return f

def split_file(file_path, nr_files, has_header=False):
    def open_with_header_written(file_idx, header):
        f = open(file_path + '.__tmp__.{0}'.format(file_idx), 'w')
        if not has_header:
            return f
        f.write(header)
        return f
    def cal_nr_lines_per_file():
        nr_lines = list(subprocess.Popen(
            'wc -l {0}'.format(file_path),
            shell=True,
            stdout=subprocess.PIPE).stdout)[0].split()[0]
        nr_lines = int(nr_lines)
        if has_header:
            nr_lines -= 1
        if nr_lines < nr_files:
            raise ValueError, "nr_lines < nr_files"
        return math.floor(float(nr_lines) / nr_files)
    nr_lines_per_file = cal_nr_lines_per_file()
    header = open(file_path).readline()
    file_idx = 0
    f = open_with_header_written(file_idx, header)
    for i, line in enumerate(open_with_first_line_skipped(
        file_path, has_header), start=1):
        f.write(line)
        if i % nr_lines_per_file == 0 and file_idx < (nr_files-1):
            f.close()
            file_idx += 1
            f = open_with_header_written(file_idx, header)
    f.close()

def cat_to_new_file(old_path, new_path, nr_files, replace=True):
    if os.path.exists(new_path):
        if replace:
            os.remove(new_path)
        else:
            raise ValueError, "cat_to_new_file, file exists"
    for i in range(nr_files):
        cmd = 'cat {of}.__tmp__.{id} >> {nf}'.format(
                of=old_path, id=i, nf=new_path)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()

def parallel_convert_using_shell(cmd_str, nr_files):
    # cmd_str: ./upper.py from.__tmp__.{idx} to.__tmp__.{idx}
    workers = []
    results = []
    for i in range(nr_files):
        cmd = cmd_str.format(idx=i)
        worker = subprocess.Popen(cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        workers.append(worker)
    for worker in workers:
        results.append(worker.communicate())
    return results

def delete_files(path, nr_files):
    for i in range(nr_files):
        os.remove('{0}.__tmp__.{1}'.format(path, i))

def delete_file(path):
    os.remove(path)


if __name__ == "__main__":
    split_file(sys.argv[1], int(sys.argv[2]), False)
    cmd_str = "./upper.py {p1}.__tmp__.{idx} {p2}.__tmp__.{idx}".format(
            p1=sys.argv[1], p2=sys.argv[3], idx="{idx}")
    parallel_convert_using_shell(cmd_str, int(sys.argv[2]))
    cat_to_new_file(sys.argv[3], sys.argv[3], int(sys.argv[2]))
    delete_files(sys.argv[1], int(sys.argv[2]))
    delete_files(sys.argv[3], int(sys.argv[2]))

