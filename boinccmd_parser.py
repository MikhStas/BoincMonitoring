import subprocess
import re


def get_tasks():
    subproc_result = subprocess.run(['boinccmd', '--get_tasks'],
            stdout=subprocess.PIPE)
    raw_str = subproc_result.stdout.decode('utf-8').strip()

    #print(raw_str)

    re_items = re.findall(r'(\d\)\s-{11}\n)((\s{3}.*\n)+)', raw_str)

    tasks = list()

    for item in re_items:
        item = item[1].split()

        task = dict()
        task['state'] = 'waiting'
        task['name'] = item[1]
        task['project'] = item[7]
        task['start_time'] = item[12] + ' ' + item[11] + ' ' + item[10] + ' ' + item[13]
        task['deadline'] = item[19] + ' ' + item[18] + ' ' + item[17] + ' ' + item[20]

        if 'done:' in item:
            task['state'] = 'running'
            task['completed'] = item[item.index('done:') + 1]

        tasks.append(task)

    return tasks

def get_old_tasks():
    subproc_result = subprocess.run(['boinccmd', '--get_old_tasks'],
            stdout=subprocess.PIPE)
    raw_str = subproc_result.stdout.decode('utf-8').strip()
    # print(raw_str)

    re_items = re.findall(r'task\s([\w-]+)', raw_str)

    tasks = list()
    # print(re_items)

    for item in re_items:
        tasks.append(item)

    return tasks


if __name__ == '__main__':
    print(get_old_tasks())
