import json
import logging
from visualSHARK.models import TechnologyLabelCommit, Hunk, FileAction, Commit, People, File

log = logging.getLogger('root')


def export_technology_labels(user):

    # todo:
    # - should we allow single exports via detail_route?

    # get all labels for current user and construct output
    out = {'user': user.username, 'data': []}
    for c in TechnologyLabelCommit.objects.filter(user=user):
        for hunk_id, ll in json.loads(c.changes).items():
            h = Hunk.objects.get(id=hunk_id)
            fa = FileAction.objects.get(id=h.file_action_id)
            commit = Commit.objects.only('author_id', 'committer_date').get(id=fa.commit_id)
            a = People.objects.get(id=commit.author_id)

            f = File.objects.get(id=fa.file_id)

            tmp = {'project': c.project_name, 'commit': c.revision_hash, 'committer_date': str(commit.committer_date), 'author': str(a.name), 'file': f.path, 'hunk_id': str(h.id), 'full_hunk': h.content, 'lines': []}
            block_lines = []
            block_techs = []
            block_code = []
            in_block = False
            for lno, hl in enumerate(h.content.split('\n')):
                line = ll.get(str(lno), {})

                techs = []
                seltype = ''

                # skip everythin that isnt labeled
                # if not line:
                    # continue

                if line:
                    techs = line.get('technologies', [])
                    seltype = line.get('selectionType', '')

                if not hl.startswith(('-', '+')):
                    if line:
                        log.error('found line %s which was not added or deleted (%s)', lno, line)
                    continue

                # start a new block
                if seltype == 'per-block' and not in_block:
                    # print('starting block')
                    in_block = True
                    block_lines.append(lno)
                    block_techs = techs
                    block_code.append(hl)
                    continue

                # continue a new block
                if seltype == 'per-block' and in_block and techs == block_techs:
                    # print('continuing block')
                    block_lines.append(lno)
                    block_techs = techs
                    block_code.append(hl)
                    continue

                # we are no longer in block mode, switch back
                if seltype != 'per-block' and in_block:
                    in_block = False
                    bl = '{}-{}'.format(block_lines[0], block_lines[-1])
                    tmp['lines'].append({'hunk_line': bl, 'code': '\n'.join(block_code), 'technologies': block_techs, 'selectionType': 'per-block'})
                    block_lines = []
                    block_code = []
                    block_techs = []

                # we are still in block mode but we did switch techs
                if seltype == 'per-block' and techs != block_techs and in_block:
                    # print('ending block because we switched techs')
                    bl = '{}-{}'.format(block_lines[0], block_lines[-1])
                    tmp['lines'].append({'hunk_line': bl, 'code': '\n'.join(block_code), 'technologies': block_techs, 'selectionType': 'per-block'})

                    block_lines = [lno]
                    block_code = [hl]
                    block_techs = techs
                    continue

                if hl.startswith(('-', '+')):
                    if not line:
                        continue
                    tmp['lines'].append({'hunk_line': lno, 'code': hl, 'technologies': techs, 'selectionType': seltype})

            if block_code:
                bl = '{}-{}'.format(block_lines[0], block_lines[-1])
                tmp['lines'].append({'hunk_line': bl, 'code': '\n'.join(block_code), 'technologies': block_techs, 'selectionType': 'per-block'})

            out['data'].append(tmp)
    return out
