import time
import boinccmd_parser as parser
from screen_handler import screen
import pdb


class TaskManager:
    def __init__(self):
        self.start_time = time.strftime(
                '%d %b %Y %H:%M:%S', time.localtime())
        self.time_elapsed = 0

        self.running_tasks_cnt = 0
        self.waiting_tasks_cnt = 0
        self.completed_tasks_cnt = 0
        self.errored_tasks_cnt = 0

        self.debug = []
        
        self.tasks = dict()

        self.completed_tsk_lifetime = 1440  # Minutes 
        self.errored_tsk_lifetime = 1440  # Minutes

    def synchronise(self, tasks_parser):
        self.debug = [] #FIXME

        # reset synchro flags for all tasks. 
        #This flags changed to True if object updates
        for task_obj in self.tasks.values():
            task_obj.reset_synchro()

        raw_tasks_lst = tasks_parser.get_tasks()
        old_tasks_lst = tasks_parser.get_old_tasks()

        for raw_task in raw_tasks_lst:
            # create new task if not find name matching
            if raw_task['name'] not in self.tasks:
                new_task = BoincTask(
                        raw_task['name'], raw_task['project'],
                        raw_task['deadline'], raw_task['start_time']
                        )
                new_task.update_state(raw_task['state'])
                self.tasks[raw_task['name']] = new_task

                self.debug.append((new_task.name, 'state 0'))
                # print('************************')
            
            # create temp variable to simplify code
            task_obj = self.tasks[raw_task['name']]

            # if new state the same than do nothing or update 
            # percent of running state
            if task_obj.state == raw_task['state']:
                if raw_task['state'] == 'running':
                    task_obj.update_progress(raw_task)
                    self.debug.append((task_obj.name, 'state 1')) #FIXME
                    self.errored_tasks_cnt += 1  #FIXME just to test
                else:
                    # ... task have changed state from waiting to running 
                    if (raw_task['state'] == 'running' and 
                            task_obj.state == 'waiting'):
                        task_obj.update_state(raw_task['state'])
                        self.running_tasks_cnt += 1
                        self.waiting_tasks_cnt -= 1
                        self.debug.append((task_obj.name, 'state 2')) #FIXME
                    # ... new task with running state was created
                    elif (raw_task['state'] == 'running' and 
                            task_obj.state == 'new'):
                        task_obj.update_state(raw_task['state'])
                        task_obj.update_progress(raw_task)
                        self.running_tasks_cnt += 1
                        self.debug.append((task_obj.name, 'state 3')) #FIXME
                    # ... new task wuth waiting state was created
                    elif (raw_task['state'] == 'waiting' and
                            task_obj.state == 'new'):
                        task_obj.update_state(raw_task['state'])
                        self.waiting_tasks_cnt += 1
    
                        self.debug.append((task_obj.name, 'state 4')) #FIXME
                    # ... task have changed state from running to waiting
                    elif (raw_task['state'] == 'waiting' and
                            task_obj.state == 'running'):
                        task_obj.update_state(raw_task['state'])
                        self.running_tasks_cnt -= 1
                        self.waiting_tasks_cnt += 1

                        self.debug.append((task_obj.name, 'state 5')) #FIXME
                    elif (raw_task['state'] == 'waiting' and
                            task_obj.state == 'waiting'):
                        task_obj.update_synchro()

                        self.debug.append((task_obj.name, 'state 6'))


        # check every unsynchronized task if it's completed. if not mark it
        # as errored
        # FIXME pdb.set_trace() 
        for task_name, task_obj in self.tasks.items():
            if task_obj.is_synchronized == False:
                if task_name in old_tasks_lst:
                    task_obj.update_state('completed')
                    self.completed_tasks_cnt += 1
                else:
                    task_obj.update_state('errored')
                    self.errored_tasks_cnt += 1
            
    def get_screen_content(self) -> list:
        total_cnt = self.running_tasks_cnt + self.waiting_tasks_cnt

        screen_content = list()
        screen_content.append('Welcome to boinc monitor program!')
        screen_content.append('')
        screen_content.append(f'Total tasks: {total_cnt}')
        screen_content.append(f'Waiting tasks: {self.waiting_tasks_cnt}')
        screen_content.append(f'Running tasks: {self.running_tasks_cnt}')
        screen_content.append('')
        screen_content.append('')
        
        for task_obj in self.tasks.values():
            if task_obj.state == 'running':
                name = task_obj.name
                project = task_obj.project
                start = task_obj.start_time
                end = task_obj.deadline
                done = task_obj.completed_percent

                screen_content.append(f'Task name: {name}')
                screen_content.append(f'Task project: {project}')
                screen_content.append(f'Task start: {start}')
                screen_content.append(f'Task deadline: {end}')
                screen_content.append(f'Task progress: {done}')
                screen_content.append('')

        screen_content.append('')
        screen_content.append(f'Monitoring start time: {self.start_time}')
        screen_content.append(f'Elapsed time: {self.time_elapsed}')
        screen_content.append(f'Completed tasks: {self.completed_tasks_cnt}')
        screen_content.append(f'Errored tasks: {self.errored_tasks_cnt}')

        #screen_content.append('')
        #screen_content.append(f'Debug string: {self.debug}')

        return screen_content


class BoincTask:
    def __init__(self, name: str, project: str, deadline: str, 
            start_time: str) -> None:
        self.name = name
        self.project = project
        self.deadline = deadline
        self.start_time = start_time
        self.state = 'new'
        self.completed_percent = None
        self.is_synchronized = False

    def update_progress(self, raw_task: dict):
        self.completed_percent = float(raw_task['completed']) * 100
        self.update_synchro()

    def update_state(self, state: str):
        self.state = state
        self.update_synchro()

    def reset_synchro(self):
        self.is_synchronized = False

    def update_synchro(self):
        self.is_synchronized = True

    def get_info(self) -> dict:
        result = {
                'name': self.name,
                'project': self.project,
                'deadline': self.deadline,
                'start_time': self.start_time,
                'completed': self.completed_percent
                }
        return result


if __name__ == '__main__':
    manager = TaskManager()

    manager.synchronise(parser)
    content = manager.get_screen_content()
    print(content)

