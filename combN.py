import numpy as np, scipy.io.wavfile as w, sys
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0
segs={1:(1.30,1.68),2:(3.70,7.50),3:(13.62,14.25),4:(15.70,17.36),5:(19.26,20.03),6:(22.22,24.26),7:(26.70,27.94),8:(29.76,32.23)}
hop=float(sys.argv[1]) if len(sys.argv)>1 else 0.005
Nw=int(0.016*sr)
Ns=np.arange(10,140)
def frameN(fr):
    n=len(fr); sp=np.abs(np.fft.rfft(fr*np.hanning(n),8*n)); df=sr/(8*n)
    L=np.log(sp+1e-6)
    best=None
    for N in Ns:
        f0=K/N; hs=np.arange(1,12); hs=hs[hs*f0<7000]
        on=L[np.round(hs*f0/df).astype(int)].mean()
        off=L[np.round((hs+0.5)*f0/df).astype(int)].mean()
        s=on-off
        if best is None or s>best[0]: best=(s,N)
    return best
for k in [int(a) for a in sys.argv[2:]] or [1,3,6,7,8]:
    a,b=segs[k]; y=x[int(a*sr):int(b*sr)]
    h=int(hop*sr); seq=[]
    for i in range(0,len(y)-Nw,h):
        fr=y[i:i+Nw]; r=np.sqrt(np.mean(fr**2))
        if r<0.03: seq.append('.');continue
        s,N=frameN(fr)
        seq.append(str(N) if s>1.2 else '?')
    # run-length
    rl=[];prev=None;c=0
    for q in seq:
        if q==prev: c+=1
        else:
            if prev is not None: rl.append('%s*%d'%(prev,c))
            prev=q;c=1
    rl.append('%s*%d'%(prev,c))
    print('=== seg',k,'hop',hop*1000,'ms'); print(' '.join(rl))
