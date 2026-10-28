set -e
mkdir -p cmp
for i in 1 2 3 4 5 6 7 8; do
  for src in seg out; do
    ffmpeg -v error -y -i $src/s$i.wav -lavfi "aresample=44100,showspectrumpic=s=600x260:legend=0:fscale=lin:stop=6000:win_func=hann:drange=80,drawtext=text='$i $src':fontsize=26:fontcolor=white:x=8:y=8" cmp/${src}$i.png
  done
  ffmpeg -v error -y -i cmp/seg$i.png -i cmp/out$i.png -filter_complex vstack cmp/p$i.png
done
ffmpeg -v error -y -i cmp/p1.png -i cmp/p2.png -i cmp/p3.png -i cmp/p4.png -i cmp/p5.png -i cmp/p6.png -i cmp/p7.png -i cmp/p8.png -filter_complex 'xstack=inputs=8:layout=0_0|w0_0|w0+w0_0|w0+w0+w0_0|0_h0|w0_h0|w0+w0_h0|w0+w0+w0_h0' cmp.png
