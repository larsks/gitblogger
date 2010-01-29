import git

fields = [ 'a_mode', 'b_mode', 'a_sha', 'b_sha', 'status',
        'a_path', 'b_path' ]

class AttrDict (dict):

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

def diff_tree(repo, a, b):
    if a == '0'*40:
        a = '--root'

    text = repo.git.diff_tree('-M', a, b)
    return list_from_diff_tree(text)

def list_from_diff_tree(text):
    diffs = []

    for line in text.split('\n'):
        if not line.startswith(':'):
            continue
        
        diff = AttrDict()
        parts = line.split()
        for field in fields:
            try:
                diff[field] = parts.pop(0)
            except IndexError:
                break
        diffs.append(diff)

    return diffs

