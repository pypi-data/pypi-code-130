import os
import shutil
import re
import glob
import bisect
from datetime import date
from enum import Enum
from kabaret import flow
from kabaret.flow_entities.entities import Entity
from libreflow.baseflow.film import Film as BaseFilm
from libreflow.utils.os import zip_folder

from .shot import Shots


class ShotState(Enum):

    MISSING_FILE                = 0
    FIRST_DELIVERY              = 1  # First delivery
    NEW_TAKE_PACK_SELECTED      = 5  # New take + resend pack
    NEW_TAKE_PACK_UNSELECTED    = 6
    RESEND_TAKE_PACK_SELECTED   = 11 # Resend last take + resend pack
    RESEND_TAKE_PACK_UNSELECTED = 12
    ALREADY_DELIVERED           = 7
    ALREADY_RECEIVED            = 8


class ShotToSend(flow.SessionObject):

    sequence_name  = flow.Param()
    shot_name      = flow.Param()
    last_take      = flow.Param()
    target_take    = flow.Computed()

    # state          = flow.Param()
    selected       = flow.Param().ui(editor='bool')
    new_take       = flow.Param().ui(editor='bool')
    send_pack      = flow.Param().ui(editor='bool')
    # message        = flow.Param()

    _action        = flow.Parent(2)

    def get_init_state(self):
        return self._action.get_init_state(self.name())
    
    def ensure_take(self, kitsu_task_name):
        return self._action.ensure_take(
            self.name(),
            'working_file_plas',
            kitsu_task_name,
            take_name=self.target_take.get(),
            replace_take=not self.new_take.get()
        )
    
    def create_package(self, delivery_dir=None):
        self._action.create_shot_package(
            self.name(),
            self._action.task.get(),
            self.target_take.get(),
            self.send_pack.get(),
            delivery_dir,
        )
    
    def update_kitsu_status(self, kitsu_task_name, kitsu_status_name, revision_name):
        self._action.update_kitsu_status(
            self.name(),
            kitsu_task_name,
            kitsu_status_name,
            self.target_take.get(),
            revision_name
        )

    def compute_child_value(self, child_value):
        if child_value is self.target_take:
            last_take = self.last_take.get()
            if last_take is None:
                index = 1
            else:
                m = re.match(r't(\d+)', last_take)
                if m is not None:
                    index = int(m.group(1))
                    if self.new_take.get():
                        index += 1
                else:
                    index = 1
            self.target_take.set('t'+str(index))


class ShotsToSend(flow.DynamicMap):

    _action = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return ShotToSend

    def __init__(self, parent, name):
        super(ShotsToSend, self).__init__(parent, name)
        self._shot_names = None
        self._shot_cache = None
    
    def mapped_names(self, page_num=0, page_size=None):
        kitsu_status = self._action.to_send_kitsu_status.get()
        
        if self._shot_names is None:
            self._mng.children.clear()
            self._shot_names = []
            self._shot_cache = {}
            
            # Get shots ready to be sent on Kitsu
            kitsu = self.root().project().kitsu_api()
            validated_shots = kitsu.get_shots({
                self._action.task.get(): [self._action.to_send_kitsu_status.get()]
            })
            for sq, sh in validated_shots:
                n = f'{sq}{sh}'
                
                bisect.insort(self._shot_names, n)
                self._shot_cache[n] = dict(
                    sequence_name=sq,
                    shot_name=sh,
                    last_take_name=self._action.get_last_take(n)
                )
        
        return self._shot_names
    
    def touch(self):
        self._shot_names = None
        super(ShotsToSend, self).touch()
    
    def _configure_child(self, item):
        self.mapped_names()
        data = self._shot_cache[item.name()]
        item.sequence_name.set(data['sequence_name'])
        item.shot_name.set(data['shot_name'])
        item.last_take.set(data['last_take_name'])


class KitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ['L&S KEY FRAME', 'L&S ANIMATION']


class SendForValidation(flow.Action):

    FILES_BY_TASK = {
        'L&S KEY FRAME': ('takes_fix.plas', 'takes_fix', None),
        'L&S ANIMATION': ('takes_ani.plas', 'takes_ani', 'ani'),
    }

    to_send_kitsu_status = flow.Param('H TO SEND').ui(hidden=True)
    task                 = flow.SessionParam('L&S KEY FRAME', KitsuTaskNames).watched()
    task_status          = flow.Param('I Waiting For Approval').ui(hidden=True)
    target_site          = flow.Param('test2').ui(hidden=True)
    
    shots = flow.Child(ShotsToSend)

    _film = flow.Parent()

    def needs_dialog(self):
        self.message.set('<h2>Send shots for validation</h2>')
        self.task.revert_to_default()
        return True
    
    def run(self, button):
        task_name = self.task.get()
        task_status_name = self.task_status.get()
        delivery_dir = self.get_delivery_dir()

        delivered_shots = []
        take_prefix = self.FILES_BY_TASK[self.task.get()][2] or ''
        if take_prefix:
            take_prefix += '_'

        for s in self.shots.mapped_items():
            if s.selected.get():
                take_name, source_revision_name = s.ensure_take(task_name)
                s.create_package(delivery_dir)
                s.update_kitsu_status(task_name, task_status_name, source_revision_name)
                delivered_shots.append((s.name(), f'{take_prefix}{take_name}'))
        
        self.create_report(delivery_dir, delivered_shots)

    def ensure_take(self, shot_name, working_file_name, kitsu_task_name, take_name=None, replace_take=False):
        lighting_files = self._film.shots[shot_name].tasks['lighting'].files
        file_name, file_display_name, suffix = self.FILES_BY_TASK[kitsu_task_name]
        suffix = suffix and suffix+'_' or ''
        name, ext = file_name.split('.')

        if not lighting_files.has_file(name, ext):
            take_file = lighting_files.add_file(
                name, ext,
                display_name=file_display_name,
                tracked=True,
                default_path_format='{sequence}_{shot}/{sequence}_{shot}_'+suffix+'{revision}'
            )
        else:
            take_file = lighting_files[f'{name}_{ext}']
        
        source_revision = lighting_files[working_file_name].get_head_revision()
        source_path = source_revision.get_path()

        if replace_take:
            if take_name is None:
                take = take_file.get_head_revision()
            else:
                take = take_file.get_revision(take_name)
            
            take.comment.set(f'Created from working file {source_revision.name()}')
            os.remove(take.get_path())
        else:
            if take_name is None:
                take_index = len(take_file.get_revisions().mapped_names()) + 1
                take_name = 't'+str(take_index)
            
            take = take_file.add_revision(
                name=take_name,
                comment=f'Created from working file {source_revision.name()}'
            )

        take_path = take.get_path()
        os.makedirs(os.path.dirname(take_path), exist_ok=True)
        shutil.copy2(source_path, take_path)

        lighting_files.touch()

        return take.name(), source_revision.name()
    
    def create_shot_package(self, shot_name, kitsu_task_name, take_name, include_pack=False, delivery_dir=None):
        lighting_files = self._film.shots[shot_name].tasks['lighting'].files
        delivery_files = self._film.shots[shot_name].tasks['delivery'].files
        today = date.today().strftime('%y%m%d')
        package_name = f'package_{today}'

        # Create package folder
        if not delivery_files.has_folder(package_name):
            package = delivery_files.add_folder(
                package_name,
                tracked=True,
                default_path_format='{sequence}_{shot}/package/'+today+'/{revision}'
            )
        else:
            package = delivery_files[package_name]
        
        pkg_rev = package.add_revision()
        pkg_path = pkg_rev.get_path()
        os.makedirs(pkg_path)

        # Copy working file in package folder
        file_name, file_display_name, suffix = self.FILES_BY_TASK[kitsu_task_name]
        name, ext = file_name.split('.')
        suffix = suffix and suffix+'_' or ''

        take_file = lighting_files[f'{name}_{ext}']
        take_path = take_file.get_revision(take_name).get_path()

        self.root().session().log_info(
            f'Copy take {take_path} into package {pkg_path}'
        )
        shutil.copy2(take_path, pkg_path)

        # If asked, copy pack as well
        if include_pack:
            pack_path = lighting_files['pack'].get_head_revision().get_path()
            self.root().session().log_info(
                f'Copy pack {pack_path} into package {pkg_path}'
            )
            shutil.copytree(pack_path, os.path.join(pkg_path, 'pack'))
        
        # Upload package
        current_site = self.root().project().get_current_site()
        upload_job = current_site.get_queue().submit_job(
            emitter_oid=pkg_rev.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
            job_type='Upload',
            init_status='WAITING'
        )

        sync_mgr = self.root().project().get_sync_manager()
        sync_mgr.process(upload_job)
        
        # Zip package in given delivery folder
        if delivery_dir is not None:
            pkg_name = f'{shot_name}_rouge_{suffix}{take_name}.zip'     # <shot_name>_rouge_<take_name>.zip
            delivery_pkg_path = os.path.join(
                delivery_dir, pkg_name
            )
            zip_folder(pkg_path, delivery_pkg_path)
        else:
            self.root().session().log_warning(
                f'{shot_name} {take_name} :: delivery folder {delivery_dir} not found'
            )
        
        msg = f'{shot_name} {take_name} :: package uploaded'
        
        self.root().session().log_info(msg)
    
    def update_kitsu_status(self, shot_name, kitsu_task_name, kitsu_status_name, take_name, revision_name):
        user_name = self.root().project().get_user_name()
        take_file_name = self.FILES_BY_TASK[kitsu_task_name][1]
        shot = self._film.shots[shot_name]
        task = shot.tasks['lighting']

        shot.set_task_status(
            kitsu_task_name,
            kitsu_status_name,
            comment=(
                f"**{user_name}** has submitted take **{take_name}** for validation.\n"
                f"- Created from working file **{revision_name}**\n\n"
                f"*{task.oid()}*"
            )
        )
    
    def get_init_state(self, shot_name):
        state = ShotState.MISSING_FILE
        if (
            self._film.shots[shot_name].tasks.has_mapped_name('lighting')
            and self._film.shots[shot_name].tasks['lighting'].files.has_file('working_file', 'plas')
            and self._film.shots[shot_name].tasks['lighting'].files['working_file_plas'].get_head_revision() is not None
            and self._film.shots[shot_name].tasks['lighting'].files['working_file_plas'].get_head_revision().get_sync_status() == 'Available'
        ):
            files = self._film.shots[shot_name].tasks['lighting'].files

            if (
                self.task.get() == 'L&S KEY FRAME'
                and (
                    not files.has_file('takes_fix', 'plas')
                    or not files['takes_fix_plas'].has_revision('t1')
                )
            ):
                state = ShotState.FIRST_DELIVERY
            else:
                today = date.today().strftime('%y%m%d')
                package_name = f'package_{today}'
                if (
                    self._film.shots[shot_name].tasks['delivery'].files.has_folder(package_name)
                    and self._film.shots[shot_name].tasks['delivery'].files[package_name].get_head_revision() is not None
                    and self._film.shots[shot_name].tasks['delivery'].files[package_name].get_head_revision().get_sync_status() == 'Available'
                ):
                    last_package = self._film.shots[shot_name].tasks['delivery'].files[package_name].get_head_revision()
                    
                    if last_package.get_sync_status(site_name=self.target_site.get()) != 'Available':
                        state = ShotState.ALREADY_DELIVERED
                    else:
                        state = ShotState.ALREADY_RECEIVED
                else:
                    state = ShotState.NEW_TAKE_PACK_UNSELECTED
        
        return state
    
    def get_last_take(self, shot_name):
        last_take = None
        file_name, file_display_name, suffix = self.FILES_BY_TASK[self.task.get()]
        name, ext = file_name.split('.')

        if (
            self._film.shots[shot_name].tasks.has_mapped_name('lighting')
            and self._film.shots[shot_name].tasks['lighting'].files.has_file(name, ext)
        ):
            last_take = self._film.shots[shot_name].tasks['lighting'].files[f'{name}_{ext}'].get_head_revision()
            if last_take is not None:
                last_take = last_take.name()
        
        return last_take

    def get_delivery_dir(self):
        delivery_dir = self.root().project().get_current_site().delivery_dir.get()

        if delivery_dir is not None:
            today = date.today().strftime('%y%m%d')
            delivery_dir = os.path.join(delivery_dir, today)

            if os.path.isdir(delivery_dir):
                i = 2
                while os.path.isdir(f'{delivery_dir}-{i}'):
                    i += 1
                delivery_dir = f'{delivery_dir}-{i}'
            
            os.makedirs(delivery_dir, exist_ok=True)
        
        return delivery_dir
    
    def create_report(self, delivery_dir, delivered_shots):
        if not delivered_shots:
            return
        
        with open(os.path.join(delivery_dir, 'delivery_report.txt'), 'w+') as report_file:
            for shot_name, take_name in delivered_shots:
                report_file.write(f'{shot_name} {take_name}\n')
    
    def child_value_changed(self, child_value):
        if child_value is self.task:
            self.shots.touch()
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.rouge.ui.package.SendShotsForValidationWidget'


class AddPresetAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    # Maybe set to SessionParam
    preset_name          = flow.Param('').ui(label='Name')
    task_name            = flow.Param('')
    path_template        = flow.Param('')
    target_name          = flow.Param('')
    with flow.group('Optional'):
        optional_init    = flow.Param().ui(editor='bool').ui(label='When init')
        optional_new_rev = flow.Param().ui(editor='bool').ui(label='When new revision')
    no_track             = flow.BoolParam()

    _map = flow.Parent()

    def get_buttons(self):
        return ('Add', 'Cancel')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        p = self._map.add(self.preset_name.get())
        p.task_name.set(self.task_name.get())
        p.path_template.set(self.path_template.get())
        p.target_name.set(self.target_name.get())
        p.optional_init.set(self.optional_init.get())
        p.optional_new_rev.set(self.optional_new_rev.get())
        p.no_track.set(self.no_track.get())
        self._map.touch()
        return self.get_result(close=True)


class FileSourcePreset(flow.Object):

    task_name            = flow.Param('')
    path_template        = flow.Param() # e.g., "^rgr(\D*\d){2,}_(\d{3})(_*){1}.plas"
    target_name          = flow.Param('')
    with flow.group('Optional'):
        optional_init    = flow.BoolParam().ui(label='When init')
        optional_new_rev = flow.BoolParam().ui(label='When new revision')
    no_track             = flow.BoolParam()


class FileSourcePresets(flow.Map):

    add_preset = flow.Child(AddPresetAction)

    @classmethod
    def mapped_type(cls):
        return FileSourcePreset


class FilesItem(flow.Object):

    file_name            = flow.Param('')
    file_format          = flow.Param('')
    file_comment         = flow.Param('')
    file_path            = flow.Param('')
    file_target          = flow.Param('')
    rev_version          = flow.Param('v001')
    with flow.group('Optional'):
        optional_init    = flow.BoolParam().ui(label='When init')
        optional_new_rev = flow.BoolParam().ui(label='When new revision')


class AddFileTest(flow.Action):

    file_name           = flow.Param('')
    file_comment        = flow.Param('')
    file_path           = flow.Param('')
    file_target         = flow.Param('')
    rev_version         = flow.Param('v001')
    
    files_map           = flow.Parent()

    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        return ['Add', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        display_name = self.file_name.get().replace(".", "_")
        item = self.files_map.add(display_name)
        item.file_name.set(self.file_name.get())
        item.file_comment.set(self.file_comment.get())
        item.file_path.set(self.file_path.get())
        item.file_target.set(self.file_target.get())
        item.rev_version.set(self.rev_version.get())

        self.files_map.touch()
        return self.get_result(close=True)


class FilesMap(flow.Map):

    add_file            = flow.Child(AddFileTest)

    @classmethod
    def mapped_type(cls):
        return FilesItem

    def columns(self):
        return ["Name", "Target", "Revision"]

    def _configure_child(self, child):
        child.file_name.set('')
        child.file_comment.set('')
        child.file_path.set('')
        child.file_target.set('')
        child.rev_version.set('v001')

    def _fill_row_cells(self, row, item):
        row["Name"] = item.file_name.get()
        row["Target"] = item.file_target.get()
        row["Revision"] = item.rev_version.get()


class ShotItem(flow.Object):

    shot_name           = flow.Param('')
    new_shot            = flow.BoolParam(False)
    shot_status         = flow.Param('')
    files_map           = flow.Child(FilesMap)


class AddShotTest(flow.Action):

    shot_name           = flow.Param('')
    new_shot            = flow.BoolParam(False)
    shot_status         = flow.Param('')
    
    shots_map           = flow.Parent()

    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        return ['Add', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        item = self.shots_map.add(self.shot_name.get())
        item.shot_name.set(self.shot_name.get())
        item.new_shot.set(self.new_shot.get())
        item.shot_status.set(self.shot_status.get())

        self.shots_map.touch()
        return self.get_result(close=True)


class ShotsMap(flow.Map):

    add_shot            = flow.Child(AddShotTest)

    @classmethod
    def mapped_type(cls):
        return ShotItem

    def columns(self):
        return ["Name", "New Shot"]

    def reset_all(self):
        for item in self.mapped_items():
            item.files_map.clear()
        self.clear()

    def _configure_child(self, child):
        child.shot_name.set(child.name())
        child.new_shot.set(False)
        child.shot_status.set('')

    def _fill_row_cells(self, row, item):
        row["Name"] = item.shot_name.get()
        row["New Shot"] = item.new_shot.get()


class ImportFiles(flow.Action):

    ICON = ('icons.gui', 'file')

    shots_map           = flow.Child(ShotsMap)

    # Settings (les passer en SessionParam)
    file_source_presets = flow.Child(FileSourcePresets)
    shot_name_pattern   = flow.Param('^rgr(\D*\d){2,}_(\d{3})')
    can_edit_target     = flow.BoolParam(False)
    change_kitsu_status = flow.BoolParam(False)
    target_kitsu_task   = flow.DictParam(dict(name='PREPARATION PALAS', status='DONE'))

    _film               = flow.Parent()

    def clear_list(self):
        self.shots_map.reset_all()

    def get_user_status(self):
        name = self.root().project().get_user_name()
        return self.root().project().get_user(name).status.get()

    def get_shot(self, name):
        kitsu_shot_names = self.get_kitsu_shot_names(name)

        if kitsu_shot_names is None:
            return False
        
        kitsu_config = self.root().project().kitsu_api()
        sequence_name = list(kitsu_shot_names.keys())[0]
        
        for shot_name in kitsu_shot_names[sequence_name]:
            if kitsu_config.get_shot_data(shot_name, sequence_name) is None:
                return False

        # Check object
        if self._film.shots.has_mapped_name(name) == False:
            return 'Create'

        return self._film.shots[name]

    def check_files(self, paths):
        incorrect = {
            'files': [],
            'shots': []
        }
        valid = []

        for path in paths:
            rev = None
            status = None
            shot_files = []
            if os.path.isfile(path):
                #region Check if plas file
                file_fullname = path.split('/')[-1]
                m = None
                preset = None
                for p in self.file_source_presets.mapped_items():
                    regex = p.path_template.get()
                    m = re.search(regex, file_fullname, re.IGNORECASE)
                    if m:
                        preset = p
                        break
                # unknown file
                if m is None:
                    incorrect['files'].append({
                        'name': '/'.join(path.split('/')[-2:]),
                        'error': 'file'
                    })
                    continue
                #endregion

                #region Call get_shot
                shot_name = file_fullname.split('.')[0]
                if shot_name.endswith('_') and shot_name[-3] == 't':
                    shot_name = '_'.join(shot_name.split('_')[:-2])
                elif shot_name.endswith('_'):
                    shot_name = shot_name[:-1]
                shot = self.get_shot(shot_name)
                if shot == False:
                    incorrect['files'].append({
                        'name': '/'.join(path.split('/')[-2:]),
                        'error': 'kitsu'
                    })
                    continue
                if shot == 'Create':
                    if p.optional_init.get() == False:
                        incorrect['files'].append({
                            'name': '/'.join(path.split('/')[-2:]),
                            'error': 'init'
                        })
                        continue
                #endregion

                #region Check revision
                # For generic version
                # file_name = file_fullname.replace('.', '_')
                # file_obj = shot.tasks[preset.task_name.get()].files.has_mapped_name(file_name)
                file_name = file_fullname.split('.')[0]
                target_name = preset.target_name.get()
                if target_name == '':
                    target_name = file_fullname
                if '.' in target_name:
                    target_name = target_name.replace('.', '_')

                #region rtk status
                if shot != 'Create':
                    if shot.tasks[preset.task_name.get()].files.has_mapped_name(target_name) == True:
                        status = 'rtk'
                        rev = shot.tasks[preset.task_name.get()].files[target_name].get_head_revision()
                        if rev and file_name.endswith('_') == False or (file_name.endswith('_') == False and file_name[-3] != 't'):
                            if preset.optional_new_rev.get() == False:
                                incorrect['files'].append({
                                    'name': '/'.join(path.split('/')[-2:]),
                                    'error': 'rtk'
                                })
                                continue
                #endregion
                
                #region init status
                    else:
                        status = 'init'
                        if preset.optional_init.get() == False:
                            incorrect['files'].append({
                                'name': '/'.join(path.split('/')[-2:]),
                                'error': 'init'
                            })
                            continue
                
                if shot == 'Create':
                    status = 'init'
                #endregion

                #endregion
                    
                #region Add in valid list
                # Add in correct shot object
                find_shot = False
                for s in valid:
                    if s['shot'] == shot_name:
                        find_shot = True
                        s['files'].append({
                            'path': path,
                            'preset': preset,
                            'name': file_fullname
                        })
                        break
                if find_shot == False:
                    valid.append({
                        'shot': shot_name,
                        'obj': shot,
                        'status': status,
                        'files': [{
                            'path': path,
                            'preset': preset,
                            'name': file_fullname
                        }]
                    })
                #endregion
            if os.path.isdir(path):
                #region Check dir name
                dir_name = path.split('/')[-1]
                regex = self.shot_name_pattern.get()
                m = re.search(regex, dir_name, re.IGNORECASE)
                if m is None:
                    if dir_name == 'pack':
                        incorrect['files'].append({
                            'name': '/'.join(path.split('/')[-2:]),
                            'error': 'pack_only'
                        })
                    else:
                        incorrect['files'].append({
                            'name': '/'.join(path.split('/')[-2:]),
                            'error': 'dir_name'
                        })
                    continue
                #endregion

                #region Call get_shot
                shot = self.get_shot(dir_name)
                if shot == False:
                    find_entry = False
                    for s in incorrect['shots']:
                        if s['shot'] == dir_name:
                            find_entry = True
                            s['error'] = 'kitsu'
                            break
                    if find_entry == False:
                        incorrect['shots'].append({
                            'shot': dir_name,
                            'files': [],
                            'error': 'kitsu'
                        })
                    continue
                #endregion

                #region Check if dir is empty
                if os.listdir(path) == []:
                    find_entry = False
                    for s in incorrect['shots']:
                        if s['shot'] == dir_name:
                            find_entry = True
                            s['error'] = 'dir_empty'
                            break
                    if find_entry == False:
                        incorrect['shots'].append({
                            'shot': dir_name,
                            'files': [],
                            'error': 'dir_empty'
                        })
                    continue
                #endregion
                
                #region listdir
                for file_fullname in os.listdir(path):
                    m = None
                    preset = None
                    #region Check targets
                    for p in self.file_source_presets.mapped_items():
                        regex = p.path_template.get()
                        m = re.search(regex, file_fullname, re.IGNORECASE)
                        if m:
                            preset = p
                            break
                    file_path = os.path.join(path, file_fullname)
                    file_name = file_fullname.split('.')[0]
                    # unknown file
                    if m is None:
                        find_entry = False
                        for s in incorrect['shots']:
                            if s['shot'] == dir_name:
                                find_entry = True
                                s['files'].append({
                                    'name': file_fullname,
                                    'error': 'file'
                                })
                                break
                        if find_entry == False:
                            incorrect['shots'].append({
                                'shot': dir_name,
                                'files': [{
                                    'name': file_fullname,
                                    'error': 'file'
                                }],
                                'error': ''
                            })
                        continue
                    #endregion
                    
                    #region Check for pack
                    if 'pack' in file_fullname:
                        if shot != 'Create':
                            if shot.tasks[preset.task_name.get()].files.has_mapped_name(file_fullname) == True:
                                if preset.no_track.get() == True:
                                    find_entry = False
                                    for s in incorrect['shots']:
                                        if s['shot'] == dir_name:
                                            find_entry = True
                                            s['files'].append({
                                                'name': file_fullname,
                                                'error': 'no_track'
                                            })
                                            break
                                    if find_entry == False:
                                        incorrect['shots'].append({
                                            'shot': dir_name,
                                            'files': [{
                                                'name': file_fullname,
                                                'error': 'no_track'
                                            }],
                                            'error': ''
                                        })
                                    continue
                                else:
                                    find_entry = False
                                    for s in incorrect['shots']:
                                        if s['shot'] == dir_name:
                                            find_entry = True
                                            s['files'].append({
                                                'name': file_fullname,
                                                'error': 'overwrite'
                                            })
                                            break
                                    if find_entry == False:
                                        incorrect['shots'].append({
                                            'shot': dir_name,
                                            'files': [{
                                                'name': file_fullname,
                                                'error': 'overwrite'
                                            }],
                                            'error': ''
                                        })

                    #endregion

                    #region Checks for plas file
                    if '.plas' in file_fullname:
                        #region if plas name == dir name
                        if file_name.endswith('_') and file_name[-3] == 't':
                            file_name = '_'.join(file_name.split('_')[:-2])
                        elif file_name.endswith('_'):
                            file_name = file_name[:-1]
                        if file_name != dir_name:
                            find_entry = False
                            for s in incorrect['shots']:
                                if s['shot'] == dir_name:
                                    find_entry = True
                                    s['files'].append({
                                        'name': file_fullname,
                                        'error': 'not_match'
                                    })
                                    break
                            if find_entry == False:
                                incorrect['shots'].append({
                                    'shot': dir_name,
                                    'files': [{
                                        'name': file_fullname,
                                        'error': 'not_match'
                                    }],
                                    'error': ''
                                })
                            continue
                        #endregion

                        #region Check revision
                        file_name = file_fullname.split('.')[0]
                        target_name = preset.target_name.get()
                        if target_name == '':
                            target_name = file_fullname
                        if '.' in target_name:
                            target_name = target_name.replace('.', '_')
                        #region rtk status
                        if shot != 'Create':
                            if shot.tasks[preset.task_name.get()].files.has_mapped_name(target_name) == True:
                                status = 'rtk'
                                rev = shot.tasks[preset.task_name.get()].files[target_name].get_head_revision()
                                if rev and file_name.endswith('_') == False or (file_name.endswith('_') == False and file_name[-3] != 't'):
                                    if preset.optional_new_rev.get() == False:
                                        find_entry = False
                                        for s in incorrect['shots']:
                                            if s['shot'] == dir_name:
                                                find_entry = True
                                                s['files'].append({
                                                    'name': file_fullname,
                                                    'error': 'rtk'
                                                })
                                                break
                                        if find_entry == False:
                                            incorrect['shots'].append({
                                                'shot': dir_name,
                                                'files': [{
                                                    'name': file_fullname,
                                                    'error': 'rtk'
                                                }],
                                                'error': ''
                                            })
                                        continue
                        #endregion

                        #region init status
                            else:
                                status = 'init'
                                if file_name.endswith('_') or (file_name.endswith('_') and file_name[-3] == 't'):
                                    if preset.optional_init.get() == False:
                                        find_entry = False
                                        for s in incorrect['shots']:
                                            if s['shot'] == dir_name:
                                                find_entry = True
                                                s['files'].append({
                                                    'name': file_fullname,
                                                    'error': 'init'
                                                })
                                                break
                                        if find_entry == False:
                                            incorrect['shots'].append({
                                                'shot': dir_name,
                                                'files': [{
                                                    'name': file_fullname,
                                                    'error': 'init'
                                                }],
                                                'error': ''
                                            })
                                        continue
                        
                        if shot == 'Create':
                            status = 'init'
                            if file_name.endswith('_') or (file_name.endswith('_') and file_name[-3] == 't'):
                                if preset.optional_init.get() == False:
                                    find_entry = False
                                    for s in incorrect['shots']:
                                        if s['shot'] == dir_name:
                                            find_entry = True
                                            s['files'].append({
                                                'name': file_fullname,
                                                'error': 'init'
                                            })
                                            break
                                    if find_entry == False:
                                        incorrect['shots'].append({
                                            'shot': dir_name,
                                            'files': [{
                                                'name': file_fullname,
                                                'error': 'init'
                                            }],
                                            'error': ''
                                        })
                                    continue

                        #endregion

                        #endregion
                    
                    #endregion
                    
                    shot_files.append({
                        'path': file_path,
                        'preset': preset,
                        'name': file_fullname
                    })
                #endregion
                
                #region no valid files
                if shot_files == []:
                    find_entry = False
                    for s in incorrect['shots']:
                        if s['shot'] == dir_name:
                            find_entry = True
                            s['error'] = 'no_valid_files'
                            break
                    if find_entry == False:
                        incorrect['shots'].append({
                            'shot': dir_name,
                            'files': [],
                            'error': 'no_valid_files'
                        })
                    continue
                #endregion

                #region all files is here ?
                # voir plus tard pour remettre au propre les paramètres

                #region init status
                all_files = True
                if shot == 'Create' or shot.tasks['lighting'].files.has_mapped_name('working_file_plas') == False:
                    for p in self.file_source_presets.mapped_items():
                        find_file = False
                        for f in shot_files:
                            if f['preset'] == p:
                                f = f['path']
                                find_file = True
                                break
                        if find_file == False:
                            if p.optional_init.get() == True:
                                continue
                            else:
                                all_files = False
                                break
                        continue
                #endregion
                
                #region rtk status
                else:
                    for p in self.file_source_presets.mapped_items():
                        find_file = False
                        for f in shot_files:
                            if f['preset'] == p:
                                find_file = True
                                break
                        if find_file == False:
                            if p.optional_new_rev.get() == True:
                                continue
                            else:
                                all_files = False
                                break
                        continue
                #endregion

                #region add to valid list
                if all_files == True:
                    print('SHOT OK!')

                    valid.append({
                        'shot': dir_name,
                        'obj': shot,
                        'status': status,
                        'files': shot_files
                    })
                else:
                    if shot_files != []:
                        print('SHOT NOT OKAY!')
                        find_entry = False
                        for s in incorrect['shots']:
                            if s['shot'] == dir_name:
                                find_entry = True
                                s['error'] = 'not_all_files'
                                break
                        if find_entry == False:
                            incorrect['shots'].append({
                                'shot': dir_name,
                                'files': [],
                                'error': 'not_all_files'
                            })

                #endregion

                #endregion
        
        # Correct files
        # Create objects in maps
        for i in valid:
            # Create shot if needed
            if self.shots_map.has_mapped_name(i['shot']) == True:
                shot = self.shots_map[i['shot']]
            else:
                shot = self.shots_map.add(i['shot'])

            if i['obj'] == 'Create':
                shot.new_shot.set(True)
            
            shot.shot_status.set(i['status'])
            
            #Create files in shot
            for f in i['files']:
                name = f['name'].replace('.', '_')
                # Ignore if already add
                if shot.files_map.has_mapped_name(name) == True:
                    continue
                # Folder has a base and retake file
                if shot.files_map.has_mapped_name(i['shot'] + '_plas') == True:
                    name, ext = f['name'].rsplit('.', 1)
                    if name.endswith('_') or (name.endswith('_') and name[-3] == 't'):
                        continue

                f_item = shot.files_map.add(name)
                f_item.file_name.set(f['name'])

                if i['status'] == 'rtk':
                    if '.' in f['name']:
                        f_item.file_comment.set('Created from ' + f['name'])

                root, ext = os.path.splitext(f['path'])
                if ext:
                    f_item.file_format.set(ext)
                
                f_item.file_path.set(f['path'])
                
                target_name = f['preset'].target_name.get()
                if target_name == '':
                    target_name = name
                if f['preset'].task_name.get() != '':
                    f_item.file_target.set(f['preset'].task_name.get() + '/' + target_name)
                else:
                    f_item.file_target.set(target_name)
                
                if i['obj'] == 'Create':
                    f_item.rev_version.set('v001')
                else:
                    if '.' in target_name:
                        target_name = target_name.replace('.', '_')
                    if i['obj'].tasks[f['preset'].task_name.get()].files.has_mapped_name(target_name):
                        rev = i['obj'].tasks[f['preset'].task_name.get()].files[target_name].get_head_revision()
                        ver = int(rev.name().replace('v', ''))
                        ver = 'v' + f'{(ver + 1):03}'
                        f_item.rev_version.set(ver)
                
                if f['preset'].optional_init.get() == True:
                    f_item.optional_init.set(True)
                if f['preset'].optional_new_rev.get() == True:
                    f_item.optional_new_rev.set(True)

        # print('Incorrect files=> ', incorrect)
        # print('Valid shots=> ', valid)
        return incorrect
    
    def get_kitsu_shot_names(self, name):
        m = re.match('^(rgr\d\d+_)(\d{3})(_\d{3})?(_\d{3})?(_\d{3})?', name)

        if m is None:
            return None
        
        sequence_name = m.group(1)
        shot_names = [m.group(2)]
        for i in range(3, len(m.groups()) + 1):
            if m.group(i) is None:
                break
            shot_names.append(m.group(i)[1:])
        
        return {sequence_name: shot_names}

    def create_shot(self, name):
        if self._film.shots.has_mapped_name(name) == False:
            return self._film.shots.add_shot(
                name, self.get_kitsu_shot_names(name)
            )
        else:
            return self._film.shots[name]

    def import_shot_files(self, shots):
        for s in shots:
            # Get shot object
            print('ImportFiles :: {shot} - Import started'.format(shot=s))
            shot_data = self.shots_map[s]
            if shot_data.new_shot.get() == True:
                shot = self.create_shot(s)
                print('ImportFiles :: {shot} - Added to libreflow'.format(shot=s))
            else:
                shot = self._film.shots[s]
            
            # Import files
            for f in shot_data.files_map.mapped_items():
                task, target = f.file_target.get().split('/')
                
                # Task check
                if shot.tasks.has_mapped_name(task) == True:
                    file_map = shot.tasks[task].files
                    # File type check
                    if f.file_format.get() != '':
                        # For file
                        name, ext = target.rsplit('.', 1)
                        if file_map.has_file(name, ext):
                            f_object = file_map[f'{name}_{ext}']
                        else:
                            f_object = file_map.add_file(name, ext, tracked=True)
                        
                        r = self._create_revision(f_object)
                        revision_path = r.get_path()
                        revision_name = r.name()

                        if f.file_comment.get() != '':
                            r.comment.set(f.file_comment.get())
                        
                        print('ImportFiles :: {shot} - Importing {name} ({version})'.format(shot=s, name=target, version=revision_name))
                        shutil.copy2(f.file_path.get(), revision_path)
                        # self._upload_revision(r)

                        #Delete file in files_map
                        shot_data.files_map.remove(f.name())
                    else:
                        # For folder
                        if file_map.has_folder(target):
                            f_object = file_map[target]

                            r = f_object.get_head_revision()
                            revision_path = r.get_path()

                            if os.path.exists(revision_path):
                                shutil.rmtree(revision_path)
                        else:
                            f_object = file_map.add_folder(target, tracked=True, default_path_format='{sequence}_{shot}/' + target)
                        
                        r = self._create_revision(f_object)
                        revision_path = r.get_path()
                        revision_name = r.name()

                        if f.file_comment.get() != '':
                            r.comment.set(f.file_comment.get())
                        
                        print('ImportFiles :: {shot} - Importing {name} ({version})'.format(shot=s, name=target, version=revision_name))
                        shutil.copytree(f.file_path.get(), revision_path)
                        # self._upload_revision(r)

                        #Delete file in files_map
                        shot_data.files_map.remove(f.name())
                else:
                    print('ImportFiles [ERROR] :: {shot} - Can\'t find the task {task} for {name}. Import for this file is aborded'.format(shot=s, task=task, name=target))
                    continue
            
            if self.change_kitsu_status.get() == True:
                self.update_statutes(s)
            
            # if all files are imported, delete shot in shot_map of importfiles
            if shot_data.files_map.mapped_items() == []:
                self.shots_map.remove(s)
        
        print('ImportFiles :: Import complete!')

    def _create_revision(self, f):
        r = f.add_revision()
        revision_path = r.get_path()
        f.last_revision_oid.set(r.oid())
        os.makedirs(os.path.dirname(revision_path), exist_ok=True)

        return r

    def _upload_revision(self, revision):
        current_site = self.root().project().get_current_site()
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )

        self.root().project().get_sync_manager().process(job)

    def _update_kitsu_status(self, target):
        kitsu_api = self.root().project().kitsu_api()

        sequence_name, shot_name = target.get().split('_')
        sequence_name = sequence_name + '_'

        target_status = self.target_kitsu_task.get()
        task_name = target_status['name']
        task_status = target_status['status']

        kitsu_api.set_shot_task_status(sequence_name, shot_name, task_name, task_status)

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.rouge.ui.ImportFilesWidget'


class Film(BaseFilm):
    
    shots = flow.Child(Shots).ui(
        expanded=True,
        show_filter=True,
    )

    sequences = flow.Child(flow.Object).ui(hidden=True)

    send_for_validation = flow.Child(SendForValidation)

    import_files = flow.Child(ImportFiles)
