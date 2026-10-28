import numpy as np, scipy.io.wavfile as w, scipy.signal as ss
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0
def lowpeak(a,b,lo,hi,hop=0.005,win=0.012):
    y=x[int(a*sr):int(b*sr)]; n=int(win*sr); h=int(hop*sr); out=[]
    for i in range(0,len(y)-n,h):
        fr=y[i:i+n]; sp=np.abs(np.fft.rfft(fr*np.hanning(n),16*n)); fq=np.fft.rfftfreq(16*n,1/sr)
        m=(fq>lo)&(fq<hi); j=np.argmax(sp*m); out.append(fq[j])
    return out
for nm,a,b,lo,hi in [('seg1',1.30,1.68,300,1400),('seg7',26.70,27.94,300,700)]:
    p=lowpeak(a,b,lo,hi); print(nm,'f0 every 5ms:',' '.join('%d'%q for q in p))
    print('  N:',' '.join('%.1f'%(K/q) for q in p))
# seg3 peaks per quarter
for (a,b) in [(13.66,13.80),(13.83,13.97),(13.99,14.13),(14.15,14.22)]:
    y=x[int(a*sr):int(b*sr)]; sp=np.abs(np.fft.rfft(y*np.hanning(len(y)),4*len(y))); fq=np.fft.rfftfreq(4*len(y),1/sr)
    pk=ss.find_peaks(sp,distance=int(40/(fq[1])))[0]; pk=[p for p in pk if fq[p]<6000]
    top=sorted(pk,key=lambda p:-sp[p])[:10]
    print('seg3',a,b,[(int(fq[p]),int(20*np.log10(sp[p]/sp[top[0]]))) for p in sorted(top)])
# envelopes 5ms for 4,5,8
for nm,a,b in [('seg4',15.68,17.40),('seg5',19.24,20.06),('seg8',29.74,32.25),('seg2tail',7.40,11.45)]:
    y=x[int(a*sr):int(b*sr)]; h=int(0.01*sr)
    e=[np.sqrt(np.mean(y[i:i+h]**2)) for i in range(0,len(y)-h,h)]
    mx=max(e); print(nm,'env10ms:',''.join(' .:-=+*#%@'[min(9,int(9*q/mx+0.5))] for q in e))
