import re, json, sys, os
W = sys.argv[1]; out = sys.argv[2]
links = "26j34 26j40 26j44 26j49 26j51 26j56 26j60 26j65 26j68 26j70".split()
res = {}
for l in links:
    h = open(os.path.join(W, l + ".html"), encoding="utf-8").read()
    label = re.search(r'const label = "([^"]+)"', h).group(1)
    raw = re.search(r'const rawdata = `(.*?)`;', h, re.S).group(1).strip().split("\n")
    X, Y = [], []
    for ln in raw:
        c = ln.split()
        X.append(float(c[1])); Y.append(float(c[0]))
    n = len(X); every = int(re.search(r"const every = ([0-9]+);", h).group(1)); m = n // every
    ds = [(i // every, i, X[i], Y[i]) for i in range(0, m * every, every)]
    title = re.search(r'<title>([^<|]+)', h).group(1).strip()
    res[title.split()[0].split("-")[0]] = dict(link=l, every=every, title=title, n=n, X=X, Y=Y, ds=ds)
    print(l, label, title, "n=", n, "m=", m, "xmax=%.4g ymax=%.4g" % (max(X), max(Y)))
json.dump(res, open(out, "w"))
