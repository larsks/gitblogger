import git

fields = [ 'a_mode', 'b_mode', 'a_sha', 'b_sha', 'status',
        'a_path', 'b_path' ]

def list_from_diff_tree(repo, text):
    diffs = []

    for line in text.split('\n'):
        if not line.startswith(':'):
            continue
        
        diff = {}
        for field in fields:
            try:
                diff[field] = line.pop(0)
            except IndexError:
                break

        diffs.append(git.diff.Diff(repo,
            diff.get('a_path'),
            None,
            None,
            None,
            diff.get('a_mode'),
            diff.get('b_mode'),
            status[0] == 'A',
            status[0] == 'D',
            diff.get('a_path'),
            diff.get('b_path'),
            None
            ))

    return diffs

