import json, sys
d = json.load(open(sys.argv[1]))
def fit(pts):
    n=len(pts); Sx=sum(p[2] for p in pts); Sy=sum(p[3] for p in pts)
    Sxy=sum(p[2]*p[3] for p in pts); Sx2=sum(p[2]**2 for p in pts); Sy2=sum(p[3]**2 for p in pts)
    m=(n*Sxy-Sx*Sy)/(n*Sx2-Sx*Sx); b=(Sy-m*Sx)/n
    R2=(n*Sxy-Sx*Sy)**2/((n*Sx2-Sx*Sx)*(n*Sy2-Sy*Sy)); return m,b,R2
out={}
for k,v in d.items():
    ds=v["ds"]; M=len(ds)
    ip=max(range(M), key=lambda i: ds[i][3]); yp=ds[ip][3]
    il=M-1
    # rule: ascending branch points between 20% and 80% of peak y
    lo=[i for i in range(ip+1) if ds[i][3]>=0.25*yp][0]
    hi=[i for i in range(ip+1) if ds[i][3]<=0.75*yp][-1]
    m,b,R2=fit(ds[lo:hi+1])
    # best-R2 search for comparison: windows >= 10 points, max slope with R2>=0.995
    best=None
    for a in range(5,ip):
        for e in range(a+9,min(ip,M-16)+1):
            mm,bb,rr=fit(ds[a:e+1])
            if rr>=0.995 and (best is None or e-a>best[1]-best[0]):
                best=(a,e,mm,bb,rr)
    out[k]=dict(peak=ip,last=il,lini=lo,linf=hi,m=m,b=b,R2=R2,M=M,
        xpeak=ds[ip][2],ypeak=yp,xlast=ds[il][2],ylast=ds[il][3],x0=-b/m)
    print(f"{k} M={M} peak={ip} ({ds[ip][2]:.4f},{yp:.2f}) last={il} ({ds[il][2]:.4f},{ds[il][3]:.2f}) lin={lo}-{hi} m={m:.2f} b={b:.2f} R2={R2:.5f} x0={-b/m:.3f} | longest R2>=.995: {best[0]}-{best[1]} m={best[2]:.1f} R2={best[4]:.4f}  ok={lo>=5 and hi+15<=M-1}")
json.dump(out,open(sys.argv[2],"w"),indent=1)
