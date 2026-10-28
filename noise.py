import numpy as np, scipy.io.wavfile as w, scipy.signal as ss
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0
def acper(y,lo=0.0015,hi=0.02):
    y=y-y.mean(); n=len(y); sp=np.fft.rfft(y,2*n); ac=np.fft.irfft(np.abs(sp)**2)[:n]; ac/=ac[0]
    a=int(lo*sr); b=min(int(hi*sr),n-1); j=a+np.argmax(ac[a:b]); return j/sr*1000, ac[j]
for nm,a,b,win in [('bombtail',7.6,11.3,0.25),('seg4',15.72,17.34,0.06),('seg5',19.28,20.0,0.05),('seg8',29.77,32.2,0.05)]:
    out=[]
    t=a
    while t+win<=b:
        y=x[int(t*sr):int((t+win)*sr)]
        if np.sqrt(np.mean(y**2))>0.02:
            p,c=acper(y); out.append('%.2f:%.2fms(%.2f)'%(t-a,p,c))
        t+=win
    print(nm,' '.join(out))
# comb check bomb tail at 208.6 multiples
y=x[int(8*sr):int(11*sr)]; sp=np.abs(np.fft.rfft(y*np.hanning(len(y)))); fq=np.fft.rfftfreq(len(y),1/sr)
for f0 in np.arange(195,225,1.0):
    pass
sc=[]
for f0 in np.arange(150,260,0.25):
    hs=np.arange(3,30)*f0; on=np.log(sp[np.round(hs/fq[1]).astype(int)]+1e-9).mean(); off=np.log(sp[np.round((hs+f0/2)/fq[1]).astype(int)]+1e-9).mean(); sc.append((on-off,f0))
sc.sort(reverse=True); print('bombtail comb best', [(round(s,2),f) for s,f in sc[:5]])
