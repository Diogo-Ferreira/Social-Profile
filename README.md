# Social-Profile
Recommending systems like netflix, spotify, amazon for instance can recommend us new stuff based on our history, behaviour and what content we play. But what happens when a new user arrives to the system with no data ? What to we recommend to him ? That's the cold start issue.

Social-Profile solve this issue by creating a user preferences profile from his Facebook account, in brief from a Facebook account the system finds:

* what music styles does the user like ?
* what kind of music does the user like ?
* what kind of events does the user like to go ?

This preferences are note from o to 1, 0=Don't like it, 0.5=Neutral, 1.0=Like it a lot.
