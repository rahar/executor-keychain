import numpy as np, scipy.io.wavfile as w, scipy.signal as ss, sys
sr,x=w.read('post.wav'); x=x.astype(float)/32768
segs=[(1.30,1.68),(3.70,11.40),(13.62,14.25),(15.70,17.36),(19.26,20.03),(22.22,24.26),(26.70,27.94),(29.76,32.23)]
def f0_frame(fr):
    fr=fr-fr.mean(); n=len(fr)
    sp=np.fft.rfft(fr*np.hanning(n),8*n); ac=np.fft.irfft(np.abs(sp)**2)[:n]
    ac/=ac[0]+1e-12
    lo=int(sr/4000); hi=int(sr/150)
    i=lo+np.argmax(ac[lo:hi])
    # prefer earliest peak within 0.9 of max (avoid octave errors)
    m=ac[i]
    pk=ss.find_peaks(ac[lo:hi])[0]+lo
    for p in pk:
        if ac[p]>0.85*m: i=p;break
    if 1<=i<n-1:
        a,b,c=ac[i-1],ac[i],ac[i+1]; d=0.5*(a-c)/(a-2*b+c+1e-12)
    else: d=0
    return sr/(i+d), ac[i]
which=[int(a) for a in sys.argv[1:]] or range(1,9)
for k in which:
    a,b=segs[k-1]; y=x[int(a*sr):int(b*sr)]
    hop=int(0.005*sr); N=int(0.02*sr)
    out=[]
    for i in range(0,len(y)-N,hop):
        fr=y[i:i+N]; r=np.sqrt(np.mean(fr**2))
        f,c=f0_frame(fr)
        sp=np.abs(np.fft.rfft(fr*np.hanning(N)))**2; fr_=np.fft.rfftfreq(N,1/sr)
        cen=(sp*fr_).sum()/sp.sum()
        flat=np.exp(np.mean(np.log(sp+1e-12)))/np.mean(sp+1e-12)
        out.append((i/sr,r,f,c,cen,flat))
    print('=== seg',k,a,b)
    step=int(sys.argv[0] and 2)
    for t,r,f,c,cen,flat in out[::2]:
        print('%.3f r%.3f f%6.0f c%.2f cen%5.0f fl%.2f'%(t,r,f,c,cen,flat))
