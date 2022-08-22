from fuglu.shared import ScannerPlugin, DELETE, DUNNO, string_to_actioncode, Suspect
from fuglu.bounce import Bounce
from fuglu.mailattach import NoExtractInfo


class EncryptedArchives(ScannerPlugin):
    """Block password protected archives"""
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'template_blockedfile': {
                'default': '${confdir}/templates/blockedfile.tmpl',
                'description': 'Mail template for the bounce to inform sender about blocked attachment',
            },
            'sendbounce': {
                'default': 'True',
                'description': 'inform the sender about blocked attachments.\nIf a previous plugin tagged the message as spam or infected, no bounce will be sent to prevent backscatter',
            },
            'blockaction': {
                'default': 'DELETE',
                'description': 'what should the plugin do when a blocked attachment is detected\n'
                               'REJECT : reject the message (recommended in pre-queue mode)\n'
                               'DELETE : discard messages\n'
                               'DUNNO  : mark as blocked but continue anyway '
                               '(eg. if you have a later quarantine plugin)',
            },
        }
        self.logger = self._logger()

    def examine(self, suspect: Suspect):
        """Exampine suspect"""
        blockaction = self.config.get(self.section, 'blockaction')

        # NoExtractInfo object will collect information about files in archives (or the archive itself)
        # if something could not be extracted
        noextractinfo = NoExtractInfo()

        # get list of direct attachments as well as extracted files if direct attachment is an archive
        _ = suspect.att_mgr.get_objectlist(level=1, include_parents=True, noextractinfo=noextractinfo)

        # get all reasons why content was not extracted except due to level
        noextractlist = noextractinfo.get_filtered(minus_filters=["level"])
        blockinfo = {}
        for file, message in noextractlist:
            if message == "Password protected archive (data + meta)":
                self.logger.info()
                # filelists are protected as well
                blockinfo = {f'{file}': f"Attachment {file} is a password protected archive (data + meta)"}

            elif "password" in message.lower():
                # filelists are not protected, only data
                self.logger.info(f"Password protected file {file} in archive, msg: {message}")
                blockinfo = {f'{file}': f"Password protected file {file} in archive"}

        if blockinfo:
            # Blocked attachments contained...
            self._blockreport(suspect, blockinfo, enginename='EncryptedArchives')
            sendbounce = self.config.getboolean(self.section, 'sendbounce')
            if sendbounce:
                if suspect.is_spam() or suspect.is_virus():
                    self.logger.info(f"{suspect.id} backscatter prevention: not sending attachment block "
                                     f"bounce to {suspect.from_address} - the message is tagged spam or virus")
                elif not suspect.from_address:
                    self.logger.warning(f"{suspect.id}, not sending attachment block bounce to empty recipient")
                else:
                    # check if another attachment blocker has already sent a bounce
                    queueid = suspect.get_tag('Attachment.bounce.queueid')
                    if queueid:
                        self.logger.info(f'{suspect.id} already sent attachment block bounce '
                                         f'to {suspect.from_address} with queueid {queueid}')
                    else:
                        self.logger.debug(f"{suspect.id} sending attachment block "
                                          f"bounce to {suspect.from_address}")
                        bounce = Bounce(self.config)
                        blockedfiletemplate = self.config.get(self.section, 'template_blockedfile')
                        queueid = bounce.send_template_file(suspect.from_address,
                                                            blockedfiletemplate,
                                                            suspect,
                                                            dict(blockinfo=blockinfo))
                        self.logger.info(f'{suspect.id} sent attachment block bounce '
                                         f'to {suspect.from_address} with queueid {queueid}')
                        suspect.set_tag('Attachment.bounce.queueid', queueid)

            blockactioncode = string_to_actioncode(blockaction)
            return blockactioncode, "Password protected archives found!"
        return DUNNO
