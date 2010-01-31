import git

fields = [ 'a_mode', 'b_mode', 'a_sha', 'b_sha', 'status',
        'a_path', 'b_path' ]

class AttrDict (dict):

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            return None

def diff_tree(repo, a, b):
    if a == '0'*40:
        a = '--root'

    text = repo.git.diff_tree('-M', '-r', a, b)
    return list_from_diff_tree(text, a, b)

def list_from_diff_tree(text, old_commit_id, new_commit_id):
    diffs = []

    for line in text.split('\n'):
        if not line.startswith(':'):
            continue
        
        diff = AttrDict()
        diff['old_commit_id'] = old_commit_id
        diff['new_commit_id'] = new_commit_id
        parts = line.split()
        for field in fields:
            try:
                diff[field] = parts.pop(0)
            except IndexError:
                break

        status = diff['status'][0]
        if status == 'D':
            diff['deleted_file'] = True
        elif status == 'R':
            diff['renamed_file'] = True
        elif status == 'A':
            diff['new_file'] = True
        elif status == 'M':
            diff['modified_file'] = True

        diffs.append(diff)

    return diffs

