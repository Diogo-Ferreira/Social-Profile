# Social-Profile

Recommending systems like Netflix, Spotify, amazon, for instance, can recommend us new stuff based on our history, behavior and what content we play. But what happens when a new user arrives in the system with no data? What to we recommend to him? That's the cold start issue.

Social-Profile solve this issue by creating a user preferences profile from his Facebook account, in brief from a Facebook account the system finds:

* what music styles does the user like?
* what kind of music does the user like?
* what kind of events does the user like to go?

These preferences are noted from o to 1, 0=Donot like it, 0.5=Neutral, 1.0=Like it a lot.

[There's some documentation here, but in french sorry](https://drive.google.com/file/d/0B9rxAiua5lIZa1FBTFRMU3Rvd1U/view?usp=sharing)


## How to use it

The service works on RabbitMQ, in order to launch a job you need to send a facebook user token to the queue "input_queue", then when the jobs finishes it will be avaible at the queue "job_done".

## Architecture

The architecture is based on microservices, since each tag (music, movies, events) needs a different processing and different external sources.

![archi](https://github.com/Diogo-Ferreira/Social-Profile/blob/master/archi.jpg)
