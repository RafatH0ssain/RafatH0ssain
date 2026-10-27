<div align="center">

<img src="./scene.svg" width="660" alt="A frame of 35mm film holding a starfield: a ringed planet turning on its axis, drifting stars, a comet, and passing spacecraft"/>

[11 project write-ups](https://rafathossain.com/) &nbsp;·&nbsp;
[linkedin](https://www.linkedin.com/in/rafat--hossain/) &nbsp;·&nbsp;
[email](mailto:rafat.hossain@dal.ca)

</div>

<img src="./hd-about.svg" width="660" alt="about"/>

> Fourth-year CS at Dalhousie, class of 2027, in Halifax.<br>
> Machine learning and full-stack, with a bias toward systems that have to<br>
> hold up against something real.

<img src="./hd-projects.svg" width="660" alt="projects"/>

<samp>01</samp> &nbsp; **Canon film scanners** &nbsp;·&nbsp; <samp>python, edsdk / ccapi</samp><br>
Negatives on a copy stand: live positive preview, remote focus and shutter, no<br>
rig shake from pressing the button. USB runs 59.8 fps to Wi-Fi's 4.0, so there<br>
are two builds, one per transport: [over USB](https://github.com/RafatH0ssain/Canon-EDSDK-Film-Scanner) and<br>
[over Wi-Fi](https://github.com/RafatH0ssain/Canon-Smart-Film-Scanner).

<samp>02</samp> &nbsp; **[SPECTRA-ICA](https://github.com/RafatH0ssain/spectra-ica-eeg)** &nbsp;·&nbsp; <samp>python, mne</samp><br>
EEG artifact removal that gates ICA cleaning by time and frequency instead of<br>
discarding whole components. It beat standard ICA on all seven metrics across<br>
ten subjects. 1st place in the machine learning category, SURGE NeuroHack 2026.

<samp>03</samp> &nbsp; **[lazy-catalog](https://github.com/RafatH0ssain/lazy-catalog)** &nbsp;·&nbsp; <samp>python, tmdb / ollama</samp><br>
Catalogues a local film and TV library into a CONTENTS.md file and an offline<br>
web page. TMDB for the facts, ffprobe for the files, a local LLM for the mood<br>
tags and for picking what to watch from what you already own.

<samp>04</samp> &nbsp; **[CamusGPT](https://github.com/RafatH0ssain/camus-gpt)** &nbsp;·&nbsp; <samp>python, ollama</samp><br>
A fine-tuned Albert Camus persona with a retrieval layer. Personality lives in<br>
the weights and facts live in retrieval, so a wrong fact is a retrieval bug and<br>
not a retraining job.

<samp>05</samp> &nbsp; **[PhotosByRH](https://github.com/RafatH0ssain/PhotosByRH)** &nbsp;·&nbsp; <samp>next.js, tailwind</samp><br>
A live photography portfolio on Next.js 16 and React 19. Page and grid motion is<br>
plain CSS so it runs on the compositor; Framer Motion is scoped to the lightbox,<br>
where it earns its weight.

<img src="./hd-stack.svg" width="660" alt="stack"/>

<samp>languages&nbsp;&nbsp;&nbsp;python&nbsp;&nbsp;typescript&nbsp;&nbsp;javascript&nbsp;&nbsp;java&nbsp;&nbsp;c++&nbsp;&nbsp;c&nbsp;&nbsp;r&nbsp;&nbsp;sql</samp><br>
<samp>ml&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pytorch&nbsp;&nbsp;numpy&nbsp;&nbsp;pandas&nbsp;&nbsp;scikit-learn&nbsp;&nbsp;mne&nbsp;&nbsp;ollama</samp><br>
<samp>web&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;react&nbsp;&nbsp;next.js&nbsp;&nbsp;node&nbsp;&nbsp;express&nbsp;&nbsp;flask&nbsp;&nbsp;tailwind&nbsp;&nbsp;webgl2</samp><br>
<samp>data&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;postgres&nbsp;&nbsp;mysql&nbsp;&nbsp;mongodb</samp><br>
<samp>infra&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker&nbsp;&nbsp;aws&nbsp;&nbsp;gcp&nbsp;&nbsp;firebase&nbsp;&nbsp;vercel&nbsp;&nbsp;git</samp>

<img src="./hd-about-this-page.svg" width="660" alt="about this page"/>

Nothing on this page loads from another server. [`scripts/make_scene.py`](scripts/make_scene.py) draws the<br>
strip and [`scripts/make_headings.py`](scripts/make_headings.py) the section rules, run by hand with their<br>
output committed, the font subset to the exact glyphs each file uses and inlined<br>
as base64. SMIL because GitHub strips `<script>`; images because it strips CSS.
