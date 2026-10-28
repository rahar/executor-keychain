import numpy as np, scipy.io.wavfile as w, sys
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0
segs={1:(1.30,1.68),2:(3.70,7.50),3:(13.62,14.25),4:(15.70,17.36),5:(19.26,20.03),6:(22.22,24.26),7:(26.70,27.94),8:(29.76,32.23)}
Nw=int(0.016*sr); Z=8*Nw; df=sr/Z
# response estimate from noise parts (bomb tail) smoothed
y=x[int(8.0*sr):int(11.2*sr)]
acc=np.zeros(Z//2+1)
for i in range(0,len(y)-Nw,Nw//2): acc+=np.abs(np.fft.rfft(y[i:i+Nw]*np.hanning(Nw),Z))
R=np.convolve(acc,np.ones(80)/80,'same')+1e-9
np.save('resp.npy',np.vstack([np.fft.rfftfreq(Z,1/sr),R/R.max()]))
Ns=np.arange(16,121)
def frameN(fr):
    sp=np.abs(np.fft.rfft(fr*np.hanning(Nw),Z))/R; L=np.log(sp+1e-9)
    sc=[]
    for N in Ns:
        f0=K/N; hs=np.arange(1,16); hs=hs[hs*f0<6500]
        on=L[np.round(hs*f0/df).astype(int)].mean(); off=L[np.round((hs+0.5)*f0/df).astype(int)].mean()
        sc.append(on-off)
    j=int(np.argmax(sc)); return sc[j],Ns[j]
hop=0.005
for k in [int(a) for a in sys.argv[1:]]:
    a,b=segs[k]; y=x[int(a*sr):int(b*sr)]; h=int(hop*sr); seq=[]
    for i in range(0,len(y)-Nw,h):
        fr=y[i:i+Nw]
        if np.sqrt(np.mean(fr**2))<0.03: seq.append('.');continue
        s,N=frameN(fr); seq.append(str(N) if s>1.0 else '?')
    rl=[];prev=None;c=0
    for q in seq:
        if q==prev: c+=1
        else:
            if prev is not None: rl.append(prev if c==1 else '%s*%d'%(prev,c))
            prev=q;c=1
    rl.append(prev if c==1 else '%s*%d'%(prev,c))
    print('=== seg',k); print(' '.join(rl))
