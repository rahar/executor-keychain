import numpy as np, scipy.io.wavfile as w, scipy.signal as ss
sr,x=w.read('post.wav'); x=x.astype(float)/32768
segs=[(1.30,1.68),(3.70,11.40),(13.62,14.25),(15.70,17.36),(19.26,20.03),(22.22,24.26),(26.70,27.94),(29.76,32.23)]
def track(y,hop=0.0025,N=0.012,fmin=200,fmax=3000):
    h=int(hop*sr);n=int(N*sr);res=[]
    for i in range(0,len(y)-n,h):
        fr=y[i:i+n]-y[i:i+n].mean()
        sp=np.fft.rfft(fr*np.hanning(n),16*n); ac=np.fft.irfft(np.abs(sp)**2)[:n]; ac/=ac[0]+1e-12
        lo=int(sr/fmax);hi=int(sr/fmin)
        pk=ss.find_peaks(ac[lo:hi])[0]+lo
        if len(pk)==0: res.append((i/sr,0,0,0));continue
        m=ac[pk].max(); p=[q for q in pk if ac[q]>0.8*m][0]
        a,b,c=ac[p-1],ac[p],ac[p+1]; d=0.5*(a-c)/(a-2*b+c+1e-12)
        res.append((i/sr,sr/(p+d),ac[p],np.sqrt(np.mean(fr**2))))
    return res
def steps(tr,tol=0.006,minlen=3):
    out=[];cur=[]
    for t,f,c,r in tr:
        if c<0.75 or f==0:
            if len(cur)>=minlen: out.append(cur)
            cur=[];continue
        if cur and abs(f/np.median([q[1] for q in cur])-1)>tol:
            if len(cur)>=minlen: out.append(cur)
            cur=[]
        cur.append((t,f,c,r))
    if len(cur)>=minlen: out.append(cur)
    return [(round(s[0][0],4),round(s[-1][0]-s[0][0]+0.0025,4),round(float(np.median([q[1] for q in s])),1),round(float(np.mean([q[3] for q in s])),3)) for s in out]
def harm(y,f0,nh=10):
    n=len(y); sp=np.abs(np.fft.rfft(y*np.hanning(n),4*n)); fr=np.fft.rfftfreq(4*n,1/sr)
    a=[sp[np.argmin(abs(fr-k*f0))-3:np.argmin(abs(fr-k*f0))+4].max() for k in range(1,nh+1)]
    a=np.array(a); return np.round(20*np.log10(a/a.max()+1e-9)).astype(int).tolist()
for k in [1,2,3,6,7,8]:
    a,b=segs[k-1]; y=x[int(a*sr):int(b*sr)]
    tr=track(y)
    print('=== seg',k)
    if k in (1,7,8):
        # continuous: print f every 10ms
        print(' '.join('%.0f'%f if c>0.7 else '-' for t,f,c,r in tr[::4]))
    else:
        st=steps(tr)
        for s in st:
            i0=int(s[0]*sr);i1=int((s[0]+s[1])*sr)
            hh=harm(y[i0:i1],s[2]) if s[1]>0.03 else ''
            print(s,hh)
