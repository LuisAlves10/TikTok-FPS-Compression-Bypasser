<h1 align="center">🎬 TikTok FPS Compression Bypasser</h1>

<p align="center">
Bypass da limitação de FPS do TikTok através da modificação direta do <code>timescale</code> em arquivos MP4.
</p>

<hr>

<h2>📌 Sobre o projeto</h2>

<p>
O TikTok limita a taxa máxima de quadros dos vídeos para <b>30 FPS</b> por padrão, utilizando um
<b>hardware encoder</b> que ajusta o tempo do vídeo com base no parâmetro
<code>timescale</code> presente nos átomos internos do arquivo MP4
(<code>mvhd</code> e <code>mdhd</code>).
</p>

<p>
Embora o vídeo final seja exibido na taxa de quadros original, essa aceleração depende diretamente
do valor do <code>timescale</code>.
</p>

<p>
Como criador de edições para TikTok e buscando manter vídeos em <b>60 FPS (ou mais)</b>,
desenvolvi este método para contornar a compressão automática da plataforma,
ajustando diretamente o <code>timescale</code> do arquivo para enganar o encoder
e preservar a fluidez original.
</p>

<hr>

<h2>⚠️ Avisos importantes</h2>

<ul>
  <li>Este método permite enviar vídeos com FPS <b>acima do limite padrão de 30 FPS</b>.</li>
  <li>O FPS no arquivo é efetivamente ilimitado.</li>
  <li>A reprodução final depende totalmente do hardware e do decoder do dispositivo do usuário.</li>
</ul>

<p>
Em dispositivos mais fracos, vídeos com FPS muito alto podem não rodar de forma fluida.
</p>

<p>
<b>Recomendação:</b> utilizar vídeos com até <b>120 FPS</b> de origem.
</p>

<hr>

<h2>🧭 Histórico e inspiração</h2>

<p>
O método antigo de bypass de FPS via upload deixou de funcionar em
<b>14 de março de 2025</b>. A partir disso, iniciei o desenvolvimento de um novo método.
</p>

<p>
A inspiração inicial foi tentar reproduzir o método do
<a href="https://www.tiktok.com/@nxt_shark537" target="_blank">@nxt_shark537</a>.
Na época, não havia clareza sobre como ele funcionava. Hoje é sabido que o método utilizava
<code>ffmpeg</code>:
</p>

<pre><code>ffmpeg -itsscale 2 -i input.mp4 -c:v copy -c:a copy output.mp4</code></pre>

<p>
Como isso não era conhecido inicialmente, segui um caminho diferente,
focando na modificação direta dos metadados internos do arquivo MP4.
</p>

<p>
Enquanto o método do <code>ffmpeg</code> atua externamente,
este projeto modifica diretamente os átomos
<code>mvhd</code> e <code>mdhd</code>.
</p>

<hr>

<h2>⚙️ Como o método funciona</h2>

<p>
O vídeo possui uma taxa de quadros original (ex: 60 FPS).
O TikTok tenta forçar essa taxa para 30 FPS utilizando um hardware encoder
que acelera o vídeo.
</p>

<p>
Para contornar isso, o script ajusta o valor do <code>timescale</code>
nos átomos MP4 com a seguinte fórmula:
</p>

<pre><code>Novo timescale = timescale original × (30 / FPS original do vídeo)</code></pre>

<p>
Dessa forma, o vídeo é acelerado proporcionalmente,
mantendo a fluidez original mesmo após a compressão do TikTok.
</p>

<hr>

<h2>🌐 Sobre slow motion no TikTok Web</h2>

<p>
No <b>TikTok Web (navegador)</b>, vídeos processados com este método
podem aparentar estar em <b>slow motion</b>.
</p>

<p>
Isso ocorre porque a versão web utiliza um <b>software encoder</b>,
que interpreta o <code>timescale</code> de forma diferente do
hardware encoder presente nos aplicativos móveis.
</p>

<p>
Para observar o efeito correto, recomenda-se assistir aos vídeos
pelo <b>aplicativo móvel do TikTok</b>.
</p>

<hr>

<h2>▶️ Uso</h2>

<ol>
  <li>Clone ou baixe este repositório.</li>
  <li>Execute o script via terminal:</li>
</ol>

<pre><code>python3 patcher.py input.mp4 output.mp4 [scale_factor]</code></pre>

<ul>
  <li><code>input.mp4</code>: arquivo de vídeo original</li>
  <li><code>output.mp4</code>: arquivo modificado</li>
  <li><code>scale_factor</code> (opcional): fator manual para ajuste do timescale</li>
</ul>

<hr>

<h2>👥 Créditos</h2>

<ul>
  <li>
    <a href="https://www.tiktok.com/@lenoz7" target="_blank">Lenoz7</a> (Luís) —
    Criador do projeto e do script.
  </li>
  <li>
    <a href="https://www.tiktok.com/@poshyler" target="_blank">Poshyler</a> —
    Colaborador no desenvolvimento da ideia e implementação técnica.
  </li>
  <li>
    <a href="https://www.tiktok.com/@nxt_shark537" target="_blank">nxt_shark537</a> —
    Inspiração conceitual.
  </li>
</ul>

<hr>

<h2>📄 Licença</h2>

<p>
Este projeto é <b>open source</b>.  
Você pode usar, modificar e contribuir livremente.
</p>

<hr>

<h1 align="center">🌍 English Version</h1>

<p align="center">
TikTok FPS limit bypass via direct <code>timescale</code> manipulation in MP4 files.
</p>

<hr>

<h2>📌 About the project</h2>

<p>
TikTok limits video playback to <b>30 FPS</b> by default using a
<b>hardware encoder</b> that adjusts video timing based on the
<code>timescale</code> value stored in MP4 atoms
(<code>mvhd</code> and <code>mdhd</code>).
</p>

<p>
Although the video may appear to keep its original frame rate,
this behavior depends entirely on the <code>timescale</code> value.
</p>

<p>
This project bypasses TikTok’s automatic compression by modifying
the internal MP4 metadata, preserving the original smoothness of the video.
</p>

<hr>

<h2>⚠️ Important notices</h2>

<ul>
  <li>Allows uploading videos above TikTok’s 30 FPS limit.</li>
  <li>The FPS stored in the file is effectively unlimited.</li>
  <li>Actual playback depends on device hardware and decoder.</li>
</ul>

<p>
<b>Recommendation:</b> use videos with up to <b>120 FPS</b>.
</p>

<hr>

<h2>⚙️ How it works</h2>

<p>
The script modifies the MP4 <code>timescale</code> value using the formula:
</p>

<pre><code>New timescale = original timescale × (30 / original FPS)</code></pre>

<p>
This tricks TikTok’s hardware encoder into preserving the original smoothness.
</p>

<hr>

<h2>▶️ Usage</h2>

<pre><code>python3 patcher.py input.mp4 output.mp4 [scale_factor]</code></pre>

<ul>
  <li><code>input.mp4</code>: original file</li>
  <li><code>output.mp4</code>: patched file</li>
  <li><code>scale_factor</code>: optional manual override</li>
</ul>

<hr>

<h2>📄 License</h2>

<p>
This project is <b>open source</b>.  
Feel free to use, modify and contribute.
</p>
