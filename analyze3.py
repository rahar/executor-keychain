import numpy as np, scipy.io.wavfile as w, scipy.signal as ss
sr,x=w.read('post.wav'); x=x.astype(float)/32768
f=np.array([954.1,925.1,899.3,874.5,850.7,828.7,807.3,788.0,769.0,750.6,733,717.5,701.7,688,672.5,658.4,645.5,633,621.9,609.3,597.8,577.1,557.7,539.5,522.7,506.7,491.5])
best=[]
for K in np.arange(25000,70000,5):
    n=K/f; err=np.sqrt(np.mean((n-np.round(n))**2)); best.append((err,K))
best.sort(); print('K fits', [(round(e,3),k) for e,k in best[:8]])
K=best[0][1]; print('N', np.round(K/f,2).tolist())
P=1/f; print('period diffs us', np.round(np.diff(P)*1e6,1).tolist())
# noise segments
for name,a,b in [('bombtail',8.0,11.2),('seg4',15.75,17.3),('seg5',19.3,19.4),('seg8noise',29.8,30.1)]:
    y=x[int(a*sr):int(b*sr)]; y=y-y.mean()
    ac=np.correlate(y[:min(len(y),sr)],y[:min(len(y),sr)],'full')[min(len(y),sr)-1:]; ac/=ac[0]
    lo=int(0.0004*sr); pk=ss.find_peaks(ac[lo:int(0.3*sr)],height=0.15)[0]+lo
    top=sorted(pk,key=lambda p:-ac[p])[:6]
    print(name,'ac peaks ms', [(round(p/sr*1000,2),round(ac[p],2)) for p in sorted(top)])
    fr,P=ss.welch(y,sr,nperseg=4096)
    db=10*np.log10(P/P.max())
    bands=[(int(fr[i]),int(db[i])) for i in range(0,len(fr),46) if fr[i]<8000]
    print('  spec', bands)
