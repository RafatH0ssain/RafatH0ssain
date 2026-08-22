<div align="center">

<img src="./contact-sheet.svg" width="660" alt="A frame of 35mm film: Rafat Hossain raising a camera to his eye, drawn in ASCII characters"/>

[photosbyrh.vercel.app](https://photosbyrh.vercel.app) &nbsp;·&nbsp;
[linkedin](https://www.linkedin.com/in/rafat--hossain/) &nbsp;·&nbsp;
[email](mailto:rafat.click.hossain@gmail.com)

</div>

<img src="./hd-about.svg" width="660" alt="about"/>

> Fourth-year CS at Dalhousie, in Halifax.<br>
> Machine learning and full-stack, with a bias toward systems that have to<br>
> hold up against something real.

Ten subjects' EEG, a camera on a copy stand, a browser at 60 fps — the work I<br>
care about is the kind that fails visibly when it is wrong. Right now that's<br>
SPECTRA-ICA, an EEG artifact-removal method that won its category at NeuroHack<br>
2026.

<img src="./hd-stack.svg" width="660" alt="stack"/>

<samp>languages&nbsp;&nbsp;&nbsp;python&nbsp;&nbsp;typescript&nbsp;&nbsp;javascript&nbsp;&nbsp;java&nbsp;&nbsp;c++&nbsp;&nbsp;c&nbsp;&nbsp;r&nbsp;&nbsp;sql</samp><br>
<samp>ml&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pytorch&nbsp;&nbsp;numpy&nbsp;&nbsp;pandas&nbsp;&nbsp;scikit-learn&nbsp;&nbsp;mne&nbsp;&nbsp;ollama</samp><br>
<samp>web&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;react&nbsp;&nbsp;next.js&nbsp;&nbsp;node&nbsp;&nbsp;express&nbsp;&nbsp;flask&nbsp;&nbsp;tailwind&nbsp;&nbsp;webgl2</samp><br>
<samp>data&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;postgres&nbsp;&nbsp;mysql&nbsp;&nbsp;mongodb</samp><br>
<samp>infra&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker&nbsp;&nbsp;aws&nbsp;&nbsp;gcp&nbsp;&nbsp;firebase&nbsp;&nbsp;vercel&nbsp;&nbsp;git</samp>

<img src="./hd-projects.svg" width="660" alt="projects"/>

<samp>01</samp> &nbsp; **[SPECTRA-ICA](https://github.com/RafatH0ssain/SPECTRAICA-Surge-NeuroHack-2026)** &nbsp;·&nbsp; <samp>python, mne</samp><br>
EEG artifact removal that gates ICA cleaning by time and frequency instead of<br>
discarding whole components. It beat standard ICA on all seven metrics across<br>
ten subjects. 1st place in the machine learning category, SURGE NeuroHack 2026.

<samp>02</samp> &nbsp; **Canon film scanners** &nbsp;·&nbsp; <samp>python, edsdk / ccapi</samp><br>
Negatives on a copy stand: live positive preview, remote focus and shutter, no<br>
rig shake from pressing the button. USB runs 59.8 fps to Wi-Fi's 4.0, so there<br>
are two builds, one per transport: [over USB](https://github.com/RafatH0ssain/Canon-EDSDK-Film-Scanner) and<br>
[over Wi-Fi](https://github.com/RafatH0ssain/Canon-Smart-Film-Scanner).

<samp>03</samp> &nbsp; **[Dosed Lens](https://github.com/RafatH0ssain/Dosed-Lens)** &nbsp;·&nbsp; <samp>typescript, webgl2</samp><br>
Twelve substances as GLSL shaders, each driven by the image's own edges and<br>
luminance rather than a filter laid over the top. Runs entirely in the browser;<br>
nothing is uploaded. Exports a PNG frame or a WebM.

<samp>04</samp> &nbsp; **[CamusGPT](https://github.com/RafatH0ssain/camus-gpt)** &nbsp;·&nbsp; <samp>python, ollama</samp><br>
A fine-tuned Albert Camus persona with a retrieval layer. Personality lives in<br>
the weights and facts live in retrieval, so a wrong fact is a retrieval bug and<br>
not a retraining job.

<samp>05</samp> &nbsp; **[PhotosByRH](https://github.com/RafatH0ssain/PhotosByRH)** &nbsp;·&nbsp; <samp>next.js, tailwind</samp><br>
A live photography portfolio on Next.js 16 and React 19. Page and grid motion is<br>
plain CSS so it runs on the compositor; Framer Motion is scoped to the lightbox,<br>
where it earns its weight.

<img src="./hd-about-this-page.svg" width="660" alt="about this page"/>

Nothing on this page loads from another server. The strip at the top is my own<br>
photograph, pushed through a thirteen-step character ramp by<br>
[`scripts/make_contact_sheet.py`](scripts/make_contact_sheet.py), and the section<br>
rules by [`scripts/make_headings.py`](scripts/make_headings.py). Both are run by<br>
hand and their output is committed, so there is no scheduled job here, and<br>
nothing on the page can rate-limit or go dark.

They animate with SMIL because GitHub strips `<script>` from READMEs, and they<br>
are images rather than styled text because it strips CSS too — drawing the<br>
heading is the only way to put this page's own typeface on it. The animation<br>
only ever subtracts: every element rests visible, so a renderer that ignores<br>
SMIL shows the finished picture instead of an empty frame.

That typeface is [JetBrains Mono](scripts/fonts), subset to the exact glyphs<br>
each file draws and inlined as base64. Not only for looks: the frame's grid<br>
assumes an advance width of exactly 0.600 em, and a viewer whose default<br>
monospace is narrower would see the strip shear.

The frame is drawn twice. Ink is ink, so one rendering would come out as a<br>
negative on a dark background; the second is mapped down an inverted ramp on<br>
its own tone curve, and the two themes swap which one is shown.
