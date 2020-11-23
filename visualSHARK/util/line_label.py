import tempfile
import git
import os
import magic
import shutil

from visualSHARK.models import Commit, FileAction, File, Hunk, Refactoring


def refactoring_lines(commit_id, file_action_id):
    """Return lines from one file in one commit which are detected as Refactorings by rMiner.
    """
    refactoring_lines_old = []
    refactoring_lines_new = []
    for r in Refactoring.objects.filter(commit_id=commit_id, detection_tool='rMiner'):
        for h in r.hunks:
            h2 = Hunk.objects.get(id=h['hunk_id'])
            if h2.file_action_id == file_action_id:
                if h['mode'] == 'D':
                    refactoring_lines_old += list(range(h['start_line'], h['end_line'] + 1))
                if h['mode'] == 'A':
                    refactoring_lines_new += list(range(h['start_line'], h['end_line'] + 1))
    return refactoring_lines_old, refactoring_lines_new


def normalize_line_endings(line):
    line = line.replace('\r\n', '\n')
    return line.replace('\r', '\n')


def get_label(line):
    # whitespace only line
    if len(line.strip()) == 0:
        return 2

    # comment only
    if line.strip().startswith('//') and '*/' not in line.strip():
        return 3
    if line.strip().startswith('/*') and '*/' not in line.strip():
        return 3
    if line.strip().startswith('*') and '*/' not in line.strip():
        return 3
    if line.strip().endswith('*/') and '/*' not in line.strip():
        return 3
    if line.strip().endswith('*/') and line.strip().startswith('/*'):
        return 3
    return 0


def get_lines(hunk):
    added_lines = {}
    deleted_lines = {}
    hunks_changes = []
    del_line = hunk.old_start
    add_line = hunk.new_start

    h = normalize_line_endings(hunk.content)
    i = 0

    content_started = False
    current_old_start = hunk.old_start
    count_old_lines = 0
    current_new_start = hunk.new_start
    count_new_lines = 0

    for line in h.split('\n'):

        tmp = line[1:]
        if line.startswith('+'):
            content_started = True
            added_lines[add_line] = {'code': tmp, 'hunk_id': hunk.id, 'hunk_line': i}
            del_line -= 1
            count_new_lines += 1
        elif line.startswith('-'):
            content_started = True
            deleted_lines[del_line] = {'code': tmp, 'hunk_id': hunk.id, 'hunk_line': i}
            add_line -= 1
            count_old_lines += 1
        else:
            # musst be context line
            if content_started:
                new_start_correction = (current_new_start if count_new_lines == 0 else current_new_start - 1)
                old_start_correction = (current_old_start if count_old_lines == 0 else current_old_start - 1)

                hunks_changes.append({'modifiedStart': new_start_correction, 'modifiedLength': count_new_lines,
                                      'originalStart': old_start_correction, 'originalLength': count_old_lines})

                current_new_start = current_new_start + count_new_lines
                current_old_start = current_old_start + count_old_lines
                count_new_lines = 0
                count_old_lines = 0
                content_started = False

            current_old_start += 1
            current_new_start += 1

        i += 1
        del_line += 1
        add_line += 1

    if count_new_lines == 0 and count_old_lines == 0:
        return added_lines, deleted_lines, hunks_changes

    # otherwise we add the last one
    new_start_correction = (current_new_start if count_new_lines == 0 else current_new_start - 1)
    old_start_correction = (current_old_start if count_old_lines == 0 else current_old_start - 1)

    hunks_changes.append({'modifiedStart': new_start_correction, 'modifiedLength': count_new_lines,
                          'originalStart': old_start_correction, 'originalLength': count_old_lines})

    return added_lines, deleted_lines, hunks_changes


def get_change_view(file, hunks, refactoring_lines_old, refactoring_lines_new):
    view_lines = []
    lines_before = []
    lines_after = []
    hunks_changes = []
    added_lines = {}
    deleted_lines = {}

    for hunk in hunks:
        al, dl, hunk_changes = get_lines(hunk)
        hunks_changes = hunks_changes + hunk_changes
        added_lines.update(al)
        deleted_lines.update(dl)

    idx_old = idx_new = 1
    i = 1
    has_changed = False

    for line in file:
        while idx_old in deleted_lines.keys():
            tmp = {'old': idx_old, 'new': '-', 'code': deleted_lines[idx_old]['code'], 'label': get_label(deleted_lines[idx_old]['code']), 'number': i, 'hunk_id': str(deleted_lines[idx_old]['hunk_id']), 'hunk_line': deleted_lines[idx_old]['hunk_line']}
            if idx_old in refactoring_lines_old:
                tmp['label'] = 4
            view_lines.append(tmp)
            lines_before.append(deleted_lines[idx_old]['code'])

            i += 1
            idx_old += 1
            has_changed = True

        if idx_new in added_lines.keys():
            tmp = {'old': '-', 'new': idx_new, 'code': added_lines[idx_new]['code'], 'label': get_label(added_lines[idx_new]['code']), 'number': i, 'hunk_id': str(added_lines[idx_new]['hunk_id']), 'hunk_line': added_lines[idx_new]['hunk_line']}
            if idx_new in refactoring_lines_new:
                tmp['label'] = 4
            view_lines.append(tmp)
            lines_after.append(added_lines[idx_new]['code'])

            i += 1
            idx_new += 1
            has_changed = True
            continue

        if idx_old not in deleted_lines.keys() and idx_new not in added_lines.keys():
            view_lines.append({'old': idx_old, 'new': idx_new, 'code': line, 'label': get_label(line), 'number': i})
            lines_before.append(line)
            lines_after.append(line)

            i += 1
            idx_new += 1
            idx_old += 1

    return view_lines, has_changed, lines_before, lines_after, hunks_changes


def get_technology_commit(project_path, commit, consensus=False):
    """Get full data for one issue and project path.
    Checks out the commit locally, reads the hunks from the db and pre-labels everything.
    """
    commits = []

    folder = tempfile.mkdtemp()
    git.repo.base.Repo.clone_from(project_path + "/", folder)

    repo = git.Repo(folder)
    repo.git.reset('--hard', commit.revision_hash)

    fa_qry = FileAction.objects.filter(commit_id=commit.id)

    # print('commit', commit.revision_hash)
    changes = []
    for fa in fa_qry:
        f = File.objects.get(id=fa.file_id)

        source_file = folder + '/' + f.path
        if not os.path.exists(source_file):
            # print('file', source_file, 'not existing, skipping')
            continue

        # print('open file', source_file, end='')
        # use libmagic to guess encoding
        blob = open(source_file, 'rb').read()
        m = magic.Magic(mime_encoding=True)
        encoding = m.from_buffer(blob)
        # print('encoding', encoding)

        # we open everything but binary
        if encoding == 'binary':
            continue
        if encoding == 'unknown-8bit':
            continue
        if encoding == 'application/mswordbinary':
            continue

        # unknown encoding error
        try:
            nfile = open(source_file, 'rb').read().decode(encoding)
        except LookupError:
            continue
        nfile = nfile.replace('\r\n', '\n')
        nfile = nfile.replace('\r', '\n')
        nfile = nfile.split('\n')

        view_lines, has_changed, lines_before, lines_after, hunks = get_change_view(nfile, Hunk.objects.filter(file_action_id=fa.id), [], [])

        if has_changed:
            changes.append({'hunks': hunks, 'filename': f.path, 'lines': view_lines, 'parent_revision_hash': fa.parent_revision_hash, 'before': "\n".join(lines_before), 'after': "\n".join(lines_after)})

    if changes:
        commits.append({'revision_hash': commit.revision_hash, 'message': commit.message, 'changes': changes})

    shutil.rmtree(folder)
    return commits


def get_correction_data(issue, project_path, username, view):
    commits = []

    folder = tempfile.mkdtemp()
    git.repo.base.Repo.clone_from(project_path + "/", folder)

    for commit in Commit.objects.filter(fixed_issue_ids=issue.id).only('id', 'revision_hash', 'parents', 'message'):
        repo = git.Repo(folder)
        repo.git.reset('--hard', commit.revision_hash)

        if commit.parents:
            fa_qry = FileAction.objects.filter(commit_id=commit.id, parent_revision_hash=commit.parents[0])
        else:
            fa_qry = FileAction.objects.filter(commit_id=commit.id)

        # print('commit', commit.revision_hash)
        changes = []
        for fa in fa_qry:
            f = File.objects.get(id=fa.file_id)

            source_file = folder + '/' + f.path
            if not os.path.exists(source_file):
                # print('file', source_file, 'not existing, skipping')
                continue

            # print('open file', source_file, end='')
            # use libmagic to guess encoding
            blob = open(source_file, 'rb').read()
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(blob)
            # print('encoding', encoding)

            # we open everything but binary
            if encoding == 'binary':
                continue
            if encoding == 'unknown-8bit':
                continue
            if encoding == 'application/mswordbinary':
                continue

            ref_old, ref_new = refactoring_lines(commit.id, fa.id)

            # unknown encoding error
            try:
                nfile = open(source_file, 'rb').read().decode(encoding)
            except LookupError:
                continue
            nfile = nfile.replace('\r\n', '\n')
            nfile = nfile.replace('\r', '\n')
            nfile = nfile.split('\n')

            view_lines, has_changed, lines_before, lines_after, hunks = view(nfile, Hunk.objects.filter(file_action_id=fa.id), ref_old, ref_new, username)

            if has_changed:
                changes.append({'hunks': hunks, 'filename': f.path, 'lines': view_lines, 'parent_revision_hash': fa.parent_revision_hash, 'before': "\n".join(lines_before), 'after': "\n".join(lines_after)})

        if changes:
            commits.append({'revision_hash': commit.revision_hash, 'message': commit.message, 'changes': changes})

    shutil.rmtree(folder)
    return commits


def get_commit_data(issue, project_path):
    commits = []

    folder = tempfile.mkdtemp()
    git.repo.base.Repo.clone_from(project_path + "/", folder)

    for commit in Commit.objects.filter(fixed_issue_ids=issue.id).only('id', 'revision_hash', 'parents', 'message'):
        repo = git.Repo(folder)
        repo.git.reset('--hard', commit.revision_hash)

        if commit.parents:
            fa_qry = FileAction.objects.filter(commit_id=commit.id, parent_revision_hash=commit.parents[0])
        else:
            fa_qry = FileAction.objects.filter(commit_id=commit.id)

        # print('commit', commit.revision_hash)
        changes = []
        for fa in fa_qry:
            f = File.objects.get(id=fa.file_id)

            source_file = folder + '/' + f.path
            if not os.path.exists(source_file):
                # print('file', source_file, 'not existing, skipping')
                continue

            # print('open file', source_file, end='')
            # use libmagic to guess encoding
            blob = open(source_file, 'rb').read()
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(blob)
            # print('encoding', encoding)

            # we open everything but binary
            if encoding == 'binary':
                continue
            if encoding == 'unknown-8bit':
                continue
            if encoding == 'application/mswordbinary':
                continue

            ref_old, ref_new = refactoring_lines(commit.id, fa.id)

            # unknown encoding error
            try:
                nfile = open(source_file, 'rb').read().decode(encoding)
            except LookupError:
                continue
            nfile = nfile.replace('\r\n', '\n')
            nfile = nfile.replace('\r', '\n')
            nfile = nfile.split('\n')

            view_lines, has_changed, lines_before, lines_after, hunks = get_change_view(nfile, Hunk.objects.filter(file_action_id=fa.id), ref_old, ref_new)

            if has_changed:
                changes.append({'hunks': hunks, 'filename': f.path, 'lines': view_lines, 'parent_revision_hash': fa.parent_revision_hash, 'before': "\n".join(lines_before), 'after': "\n".join(lines_after)})

        if changes:
            commits.append({'revision_hash': commit.revision_hash, 'message': commit.message, 'changes': changes})

    shutil.rmtree(folder)
    return commits


def get_consensus_data(issue, project_path, consensus=False):
    """Get full data for one issue and project path.

    Checks out the commit locally, reads the hunks from the db and pre-labels everything.
    """
    commits = []

    folder = tempfile.mkdtemp()
    git.repo.base.Repo.clone_from(project_path + "/", folder)

    for commit in Commit.objects.filter(fixed_issue_ids=issue.id).only('id', 'revision_hash', 'parents', 'message'):
        repo = git.Repo(folder)
        repo.git.reset('--hard', commit.revision_hash)

        if commit.parents:
            fa_qry = FileAction.objects.filter(commit_id=commit.id, parent_revision_hash=commit.parents[0])
        else:
            fa_qry = FileAction.objects.filter(commit_id=commit.id)

        # print('commit', commit.revision_hash)
        changes = []
        for fa in fa_qry:
            f = File.objects.get(id=fa.file_id)

            source_file = folder + '/' + f.path
            if not os.path.exists(source_file):
                # print('file', source_file, 'not existing, skipping')
                continue

            # print('open file', source_file, end='')
            # use libmagic to guess encoding
            blob = open(source_file, 'rb').read()
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(blob)
            # print('encoding', encoding)

            # we open everything but binary
            if encoding == 'binary':
                continue
            if encoding == 'unknown-8bit':
                continue
            if encoding == 'application/mswordbinary':
                continue

            ref_old, ref_new = refactoring_lines(commit.id, fa.id)

            # unknown encoding error
            try:
                nfile = open(source_file, 'rb').read().decode(encoding)
            except LookupError:
                continue
            nfile = nfile.replace('\r\n', '\n')
            nfile = nfile.replace('\r', '\n')
            nfile = nfile.split('\n')

            if consensus:
                hunks = []
                view_lines, has_changed, lines_before, lines_after = get_consensus_view(nfile, Hunk.objects.filter(file_action_id=fa.id), ref_old, ref_new)
            else:
                view_lines, has_changed, lines_before, lines_after, hunks = get_change_view(nfile, Hunk.objects.filter(file_action_id=fa.id), ref_old, ref_new)
            if has_changed:
                changes.append({'hunks': hunks, 'filename': f.path, 'lines': view_lines, 'parent_revision_hash': fa.parent_revision_hash, 'before': "\n".join(lines_before), 'after': "\n".join(lines_after)})

        if changes:
            commits.append({'revision_hash': commit.revision_hash, 'message': commit.message, 'changes': changes})

    shutil.rmtree(folder)
    return commits


def hunk_lines(hunk):
    added_lines = {}
    deleted_lines = {}
    del_line = hunk.old_start
    add_line = hunk.new_start

    h = normalize_line_endings(hunk.content)

    for i, line in enumerate(h.split('\n')):

        line_label = None
        for lbl in ['bugfix', 'unrelated', 'refactoring', 'documentation', 'whitespace', 'test']:
            if lbl in hunk.lines_verified.keys() and i in hunk.lines_verified[lbl]:
                line_label = lbl

        tmp = line[1:]

        pre_label = get_label(tmp)

        if line.startswith('+'):
            added_lines[add_line] = {'code': tmp, 'hunk_id': hunk.id, 'hunk_line': i, 'consensus_label': line_label, 'label': pre_label}
            del_line -= 1
        elif line.startswith('-'):
            deleted_lines[del_line] = {'code': tmp, 'hunk_id': hunk.id, 'hunk_line': i, 'consensus_label': line_label, 'label': pre_label}
            add_line -= 1

        del_line += 1
        add_line += 1

    return added_lines, deleted_lines


def get_consensus_view(file, hunks, refactoring_lines_old, refactoring_lines_new):
    view_lines = []
    lines_before = []
    lines_after = []
    added_lines = {}
    deleted_lines = {}

    for hunk in hunks:
        al, dl = hunk_lines(hunk)
        added_lines.update(al)
        deleted_lines.update(dl)

    idx_old = idx_new = 1
    i = 1
    has_changed = False

    for line in file:
        while idx_old in deleted_lines.keys():
            tmp = {'old': idx_old, 'new': '-', 'consensus_label': deleted_lines[idx_old]['consensus_label'], 'code': deleted_lines[idx_old]['code'], 'label': get_label(deleted_lines[idx_old]['code']), 'number': i, 'hunk_id': str(deleted_lines[idx_old]['hunk_id']), 'hunk_line': deleted_lines[idx_old]['hunk_line']}
            if idx_old in refactoring_lines_old:
                tmp['label'] = 4
            view_lines.append(tmp)
            lines_before.append(deleted_lines[idx_old]['code'])

            i += 1
            idx_old += 1
            has_changed = True

        if idx_new in added_lines.keys():
            tmp = {'old': '-', 'new': idx_new, 'consensus_label': added_lines[idx_new]['consensus_label'], 'code': added_lines[idx_new]['code'], 'label': get_label(added_lines[idx_new]['code']), 'number': i, 'hunk_id': str(added_lines[idx_new]['hunk_id']), 'hunk_line': added_lines[idx_new]['hunk_line']}
            if idx_new in refactoring_lines_new:
                tmp['label'] = 4
            view_lines.append(tmp)
            lines_after.append(added_lines[idx_new]['code'])

            i += 1
            idx_new += 1
            has_changed = True
            continue

        if idx_old not in deleted_lines.keys() and idx_new not in added_lines.keys():
            view_lines.append({'old': idx_old, 'new': idx_new, 'code': line, 'label': get_label(line), 'number': i})
            lines_before.append(line)
            lines_after.append(line)

            i += 1
            idx_new += 1
            idx_old += 1

    return view_lines, has_changed, lines_before, lines_after
