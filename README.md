# d1m1try_project
An automotive capture the flag game for educational purposes.

<h1>The d1m1try Project</h1>
<p>The emerging topic of the automotive cybersecurity is becoming particularly interesting these days as the vehicles become more and more connected to the external world and the increasing amount of personal data stored and processed by them.  Considering the safety critical aspect of these important products of the everydays, it is even more crucial to make sure that the (not only) metaphoric steering wheel will remanin in the hands of the drivers and the data will be used by the subjects authorized by that usage.</p>
<p>To give some aid in this matter, The d1m1try Project provides a safe environment to get familiar with some of the frequent security implementation issues focusing on the diagnostic and debug layers of the embedded devices called Electronic Control Units (ECUs), to build competence on the secure design of surfaces so exposed to the untrusted world. In my sincere belief the best way doing that is to break these security controls.</p1>
<p>The goal here was to provide a game which does not only assist in the matter mentioned above, but to provide this a supposedly entertaining way. The main inspiration was the genre of adventure books from the late 20th century. The gamepay is linear, but I dreamed a dystopia called Chernograd, which is a cyberpunk mammoth city located in somewhere in Eastern-Europe and ruled by a corrupt system. Nothing really original, but it might be some help to build an atmosphere. :) </p>
<p>I want to wish every user a few constructively spent hours with this game and I am open for the feedbacks. It might happened that some points remained unclear for the challenges and there also might be implementation issues in the virtualized diagnostic tool - ECU communication. </p>
<p>If you somehow leveraged this material for creating additional challenges, please publish the derivative products according to GNU v3.0, let others grow and have fun. </p>
<br>
<h2>Many thanks for the people contributed in these project:</h2>
<p>
my family for supporting me, my 2-yo daughter, Rozi for providing me some spare time by sleeping properly,<br>
my unborn daughter, Lujzi for inspirating me for work for the being worried of not having time for some time after she is born for such things like creating CTF games,<br>
my wife for being patient while I coded the stages and composed the story,<br>
Paul Rebar for providing the cover art picturing Dimitri for free,<br>
the artists providing pictures under Creative Commons license,<br>
and my friends and colleagues who tested the stages and provided ideas for them.</p>

<h2>System Requirement</h2>
To play with d1m1try, a configured Python 3 is necessary.
To play slideshows containing the challenges and the background story of them, Microsoft Power Point is preferred, since I cannot tell how other slideshow programs will affects the format of the slides like positioning of objects and colors.
<h2>How to play</h2>
To start story, open d1m1try_pt1 from the story folder. Everything will be described there. No programming skills are necessary for the completion of the game.
<h1>Technical background</h1>
<p>The d1m1try project uses a Python 3 based framework to emulate a connection between a diagnostic tool and a working vehicle ECU. This virtualization focuses only the diagnostic and the debug layer, and is the simplified version of the real world ones (including ISO 14229 UDS standard or Universal Measure and Calibration Protocol). </p>
<p>The basis of this is simulation is the base_ECU.py which can be found in the ECU_models package. It is supposed to be implemented as a robust ECU from security point of view and the other modules have the vulnerabilities deliberately placed inside them. Basically, anybody can create other models with another vulnerabilities or add more functionality to the ECU. </p>
<p>I tried to document the code thoroughly to assist in the development of any derivative work. If you got stucked, feel free to contact me and I will do my best to reply.</p>
<h1>Contact</h1>
János Kovács
https://www.linkedin.com/in/janoskovacs89/
